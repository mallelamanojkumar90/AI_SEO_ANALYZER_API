import httpx
import time
from typing import Tuple, Optional

class Crawler:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def fetch_page(self, url: str) -> Tuple[Optional[str], float]:
        start_time = time.time()
        
        # Following redirects and acting like a browser
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                load_time = time.time() - start_time
                return response.text, load_time
            except httpx.RequestError:
                return None, 0.0
            except httpx.HTTPStatusError:
                return None, 0.0
