import asyncio
import httpx
import requests
from tenacity import retry, retry_if_exception_type, retry_if_result, stop_after_attempt, wait_exponential

from src.services.tools.constants import MAX_CONCURRENT_CALLS, RETRYABLE_STATUS_CODES

# ----------------- RETRY STRATEGY ----------------- #


def is_retryable_response(response: httpx.Response) -> bool:
    return response.status_code in RETRYABLE_STATUS_CODES


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=(
        retry_if_exception_type(httpx.RequestError)
        | retry_if_result(is_retryable_response)
    ),
)
async def post_with_retry_async(
    url: str, payload: dict, headers: dict
) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        return response
    
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=(
        retry_if_exception_type(httpx.RequestError)
        | retry_if_result(is_retryable_response)
    ),
)
async def get_with_retry_async(
    url: str, params: dict = None, headers: dict = None
) -> httpx.Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params, headers=headers)
        return response



async def fetch_weather(lat: float, lon: float, duration: int, 
                  units: str = 'metric', lang: str = 'en') -> dict:
    """
    Fetch weather data for given coordinates using OpenWeather One Call API 3.0.

    Parameters:
        lat (float): Latitude (-90 to 90).
        lon (float): Longitude (-180 to 180).
        duration (int): Number of daily forecast days (1-8).
        units (str): Units of measurement. One of 'standard', 'metric', 'imperial'. Default 'metric'.
        lang (str): Language code for descriptions. Default 'en'.

    Returns:
        dict: {
            'current': {...},
            'hourly': [...],
            'daily': [... up to duration ...],
            'alerts': [... or empty ...],
            'timezone': str,
            'lat': float,
            'lon': float
        }

    Raises:
        ValueError: if duration is out of range.
        requests.HTTPError: if the API request fails.
    """
    # Validate duration
    if not (1 <= duration <= 8):
        raise ValueError("`duration` must be between 1 and 8 (inclusive).")

    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': apikey,
        'units': units,
        'lang': lang,
    }
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

    async with semaphore:
        try:
            response = await get_with_retry_async(url, params=params)
            data = response.json()
            result = {
                'lat': data.get('lat'),
                'lon': data.get('lon'),
                'timezone': data.get('timezone'),
                'timezone_offset': data.get('timezone_offset'),
                'current': data.get('current'),
                'hourly': data.get('hourly'),
                'daily': data.get('daily', [])[:duration],
                'alerts': data.get('alerts', [])
            }

            return result
        except httpx.RequestError as e:
            raise httpx.RequestError(f"OpenWeather API error {response.status_code}: {response.text}") from e

