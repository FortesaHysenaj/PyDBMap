import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    # DB Credentials
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql+psycopg2")
    LOG_LEVEL = int(os.getenv("LOG_LEVEL", 20))


@lru_cache
def get_config():
    return Config()


configuration: Config = get_config()
