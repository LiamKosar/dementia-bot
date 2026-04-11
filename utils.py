from functools import lru_cache
from supabase import create_client, Client
from supabase._async.client import create_client as create_async_client, AsyncClient
import os

from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SECRET_KEY"),
    )


async def get_async_supabase_client() -> AsyncClient:
    return await create_async_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SECRET_KEY"),
    )
