# dementia-bot

A Pipecat-based voice bot that joins Daily rooms to assist dementia patients, powered by Gemini Live.

## Environment variables

Create a `.env` file in the project root with:

```
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_SECRET_KEY=
OPENWEATHER_API_KEY=
```

## Running

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

The bot subscribes to inserts on the Supabase `meeting_rooms` table and spawns a session for each new row.
