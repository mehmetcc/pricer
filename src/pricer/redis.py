import redis.asyncio as redis

from .config import Config

config = Config()
client = redis.from_url(
    f"redis://{config.redis_host}:{config.redis_port}", decode_responses=True)


class NoSymbolsException(Exception):
    pass


async def set_symbol(stock: str, client_id: str) -> None:
    await client.sadd(f"pricer:symbols:{client_id}", stock)

async def get_symbols(client_id: str) -> list[str]:
    symbols = await client.smembers(f"pricer:symbols:{client_id}")
    if not symbols:
        return []
    return list(symbols)
