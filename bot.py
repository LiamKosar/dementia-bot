#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
import os
from uuid import UUID
import asyncio
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
from pipecat.services.google.gemini_live import GeminiLiveLLMService
from pipecat.services.google.gemini_live.llm import GeminiVADParams
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.adapters.schemas.tools_schema import ToolsSchema

from context import session_context, BotSession
from prompts import SYSTEM_PROMPT_V1
from tools.person_tools import (
    build_person_tools,
    handle_lookup_person,
)
from loguru import logger
from utils import get_async_supabase_client
from pipecat.audio.vad.silero import SileroVADAnalyzer


async def run_bot(room_url: str, token: str, user_id: UUID):
    person_tools = asyncio.create_task(build_person_tools(user_id))

    pipecat_transport = DailyTransport(
        room_url=room_url,
        token=token,
        bot_name="Dementia Aid",
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(
                    confidence=0.65,
                    start_secs=0.2,
                    stop_secs=0.2,
                    min_volume=0.01,
                )
            ),
        ),
    )

    # Set session context with transport reference
    session_context.set(BotSession(user_id=user_id, transport=pipecat_transport))

    llm = GeminiLiveLLMService(
        api_key=os.getenv("GEMINI_API_KEY"),
        settings=GeminiLiveLLMService.Settings(
            model="models/gemini-3.1-flash-live-preview",
            voice="Vindemiatrix",
            system_instruction=SYSTEM_PROMPT_V1,
            vad=GeminiVADParams(disabled=True),
        ),
    )

    llm.register_function("lookup_person", handle_lookup_person)

    person_tools = await person_tools

    tools = ToolsSchema(standard_tools=person_tools)
    context = LLMContext(tools=tools)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            pipecat_transport.input(),
            user_aggregator,
            llm,
            pipecat_transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=False,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @task.event_handler("on_pipeline_error")
    async def on_pipeline_error(task, frame):
        logger.error(f"Pipeline error: {frame}")
        await task.cancel()

    @pipecat_transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        # Kick off the conversation.
        # context.add_message(
        #     {"role": "developer", "content": "Please introduce yourself to the user."}
        # )
        await task.queue_frames([LLMRunFrame()])

    @pipecat_transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Pipecat Client disconnected")
        await task.cancel()

    @pipecat_transport.event_handler("on_error")
    async def on_error(error):
        logger.error(f"Gemini BidiGenerateContent error: {error}")

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)


async def main():
    """Main function that listens for meeting_rooms inserts and triggers bot instances."""
    supabase = await get_async_supabase_client()

    def on_insert(payload):
        """Callback for new meeting room inserts."""
        logger.info(f"New meeting room created: {payload}")
        try:
            new_record = payload["data"]["record"]
            room_url = new_record["room_url"]
            token = new_record["token"]
            user_id = UUID(new_record["user_id"])

            logger.info(f"New meeting room created for user {user_id}")

            # Run the bot in a new task
            asyncio.create_task(run_bot(room_url, token, user_id))

        except Exception as e:
            logger.error(f"Error handling meeting room insert: {e}")

    # Subscribe to meeting_rooms table inserts
    channel = supabase.channel("meeting_rooms_channel")
    await channel.on_postgres_changes(
        event="INSERT", schema="public", table="meeting_rooms", callback=on_insert
    ).subscribe()

    logger.info("Listening for meeting room inserts...")

    # Keep the main loop running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        channel.unsubscribe()


if __name__ == "__main__":
    asyncio.run(main())
