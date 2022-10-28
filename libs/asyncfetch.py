from typing import Tuple, Dict, Union
import aiohttp
import asyncio
import time


class Fetch(object):
    async def fetch(self, url: str, proxy=None, headers: dict = None,
                    message: str = None) -> Tuple[Dict, int]:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=proxy) as response:
                if message: print(message)
                return await response.json(), response.status

    async def boundFetch(self, semaphore: asyncio.BoundedSemaphore, url: str, proxy=None,
                         headers: dict = None, time_sleep: int = None, message: str = None) -> Tuple[Dict, int]:
        async with semaphore:
            if time_sleep:
                time.sleep(time_sleep)
            return await self.fetch(url=url, proxy=proxy, headers=headers, message=message)
