from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import aioredis


async def init_rate_limiter(app: FastAPI):
    redis = await aioredis.from_url("redis://localhost")
    await FastAPILimiter.init(redis)


async def rate_limiter_dependency():
    return RateLimiter(times=100, seconds=3600)  # 100 requests per hour
