import httpx, os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
REQUEST_RETRIES = int(os.getenv("REQUEST_RETRIES", "2"))

headers = {"User-Agent":"CityAssistant/1.0","Accept":"application/json"}

@retry(reraise=True, stop=stop_after_attempt(REQUEST_RETRIES), wait=wait_exponential(multiplier=0.3, min=0.3, max=2.0),
       retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)))
async def get(url: str, params=None):
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers=headers) as client:
        r = await client.get(url, params=params); r.raise_for_status()
        return r.json()
