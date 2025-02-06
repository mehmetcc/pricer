import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        self.redis_port = os.getenv('REDIS_PORT', 6379)

    def __repr__(self):
        return f"Config(REDIS_HOST={self.redis_host}, REDIS_PORT={self.redis_port})"
