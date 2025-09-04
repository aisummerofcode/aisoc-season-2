import asyncio
from langchain_core.tools import tool
from src.services.tools.apis import fetch_weather


@tool
def get_weather(query: str) -> list:
    """
    Tool to fetch weather forecast given a query string.
    Expected format: 'lat,lon,duration'
    Example: '6.5244,3.3792,'
    Returns: list of daily weather reports (up to duration).
    """
    try:
        lat, lon, duration, apikey = query.split(",")
        lat = float(lat.strip())
        lon = float(lon.strip())
        duration = int(duration.strip())

        # Run async function in sync context
        result = asyncio.run(fetch_weather(lat, lon, duration, apikey))

        return result

    except Exception as e:
        return [{"error": str(e)}]
