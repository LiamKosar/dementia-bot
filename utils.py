from functools import lru_cache
from supabase import create_client, Client
from supabase._async.client import create_client as create_async_client, AsyncClient
import os
import requests
from typing import Optional

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


def get_weather_description(city: str, state: str, country: str = "US") -> Optional[str]:
    """
    Get current weather description for a location using OpenWeatherMap API.
    Returns a simple description like "sunny", "cloudy", "rainy", etc.
    Returns None if weather data cannot be retrieved.
    """
    from loguru import logger

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("OPENWEATHER_API_KEY not found in environment")
        return None

    try:
        # Convert country code if needed (USA -> US)
        if country == "USA":
            country = "US"

        # Build location query
        location = f"{city},{state},{country}"
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "imperial"
        }

        logger.debug(f"Fetching weather for: {location}")
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        weather_main = data["weather"][0]["main"].lower()
        temp = round(data["main"]["temp"])

        # Map weather conditions to simple descriptions
        weather_map = {
            "clear": "sunny",
            "clouds": "cloudy",
            "rain": "rainy",
            "drizzle": "drizzly",
            "thunderstorm": "stormy",
            "snow": "snowy",
            "mist": "misty",
            "fog": "foggy"
        }

        description = weather_map.get(weather_main, weather_main)
        result = f"{description} and {temp}°F"
        logger.debug(f"Weather result: {result}")
        return result

    except Exception as e:
        # Log error but don't crash
        logger.warning(f"Failed to fetch weather for {city}, {state}: {e}")
        return None
