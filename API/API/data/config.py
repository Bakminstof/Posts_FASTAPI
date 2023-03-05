import os

from pydantic import BaseSettings
from pathlib import Path

BASE_DIR_PATH = Path(__file__).parent.parent.absolute()
ENV_DIR: str = 'environment'


class Settings(BaseSettings):
    # API settings
    ROOT_PATH: str = str(BASE_DIR_PATH)

    API_NAME: str = 'Posts API'
    API_VERSION: str = '0.1.0'

    STATIC_PATH: str = '/static'
    STATIC_DIR: str = f'{ROOT_PATH}/static'

    OPENAPI_URL: str = '/openapi.json'
    DOCS_FILE: str = f'{STATIC_DIR}/docs/docs.json'
    REDOC_URL: str = None
    DOCS_URL: str = None

    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    DEV: bool

    WEBAPP_PORT: int

    META: dict = {
        'version': API_VERSION,
    }

    # DB settings
    ECHO_SQL: bool

    DB_DRIVER: str
    DB_NAME: str

    DB_HOST: str
    DB_PORT: int

    DB_USER: str
    DB_PASS: str

    # Elasticsearch settings
    ELASTIC_INDEX_NAME: str = 'posts_index'

    ELASTIC_SCHEMA: str

    ELASTIC_HOST: str
    ELASTIC_PORT: int

    ELASTIC_USER: str
    ELASTIC_PASS: str

    class Config:
        env = os.environ['ENV_FILE_TYPE']
        env_file = BASE_DIR_PATH / ENV_DIR / f'{env}'


settings = Settings()
