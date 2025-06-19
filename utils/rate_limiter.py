import asyncio
import time

class RateLimiter:
    def __init__(self, max_requests: int):
        self.max_tokens = max_requests
        self.tokens = max_requests
        self.refill_rate = max_requests / 60  # tokens per second
        self.last_refill_timestamp = time.time()
    
    async def try_acquire(self) -> bool:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        time_until_next_token = 1.0 / self.refill_rate
        await asyncio.sleep(time_until_next_token)
        return await self.try_acquire()
    
    def _refill(self) -> None:
        now = time.time()
        time_passed = now - self.last_refill_timestamp
        self.tokens = min(self.max_tokens, self.tokens + time_passed * self.refill_rate)
        self.last_refill_timestamp = now 