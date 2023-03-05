from api_wsgi import app
from data import settings


class TConfig:
    """
    Настройки для тестов
    """
    APP = app
    TIMEOUT = 5
    BASE_URL = 'http://test'
    HTTP2 = True

    META = settings.META

    DATETIME_FORMAT = settings.DATETIME_FORMAT

    ELASTIC_INDEX_NAME = 'posts_index'
    ELASTIC_HOST = settings.ELASTIC_HOST

    DB_HOST = settings.DB_HOST
