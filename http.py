import asyncio
import random
from typing import Optional
import aiohttp

RETRYABLE = {408, 425, 429, 500, 502, 503, 504}

async def fetch_text(
    session: aiohttp.ClientSession,
    url: str,
    *,
    semaphore: asyncio.Semaphore,
    retries: int = 5,
    timeout_seconds: int = 30,
    headers: Optional[dict] = None,
) -> str:
    async with semaphore:
        for attempt in range(retries):
            try:
                timeout = aiohttp.ClientTimeout(total=timeout_seconds)
                async with session.get(url, timeout=timeout, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    if resp.status not in RETRYABLE:
                        raise RuntimeError(f"HTTP {resp.status}: {url}")

                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay = min(float(retry_after), 60.0)
                        except ValueError:
                            delay = 2 ** attempt
                    else:
                        delay = min(60.0, (2 ** attempt) + random.random())

                    await asyncio.sleep(delay)

            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt == retries - 1:
                    raise
                delay = min(60.0, (2 ** attempt) + random.random())
                await asyncio.sleep(delay)

    raise RuntimeError(f"Failed after retries: {url}")
