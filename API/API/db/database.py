from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from data import settings

db_url_object = URL.create(
    drivername=settings.DB_DRIVER,
    database=settings.DB_NAME,
    username=settings.DB_USER,
    password=settings.DB_PASS,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
)

async_engine = create_async_engine(
    url=db_url_object,
    echo=settings.ECHO_SQL
)

async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=True,
    class_=AsyncSession
)
