import asyncio

from typing import List, Tuple
from elasticsearch import AsyncElasticsearch
from elastic_transport import NodeConfig
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine, AsyncEngine

from db import Post
from data import settings
from tests.t_config import TConfig


class DB:
    """
    Класс для новых подключений к Postgres и Elasticsearch и взаимодействия с таблицей Post
    """

    def __init__(self):
        self.posts: List[Post] | None = None

        self.async_elastic_client = self.__get_elastic_client()

        self.async_engine = self.__get_database_async_engine()
        self.async_sessionmaker = self.__get_database_async_session(self.async_engine)

    # Get Elasticsearch async client
    @staticmethod
    def __get_elastic_client() -> AsyncElasticsearch:
        node_config = NodeConfig(
            scheme=settings.ELASTIC_SCHEMA,
            host=TConfig.ELASTIC_HOST,
            port=settings.ELASTIC_PORT
        )

        es_client = AsyncElasticsearch(
            hosts=[node_config],
        )
        return es_client

    # Get Postgres async engine
    @staticmethod
    def __get_database_async_engine() -> AsyncEngine:
        db_url_object = URL.create(
            drivername=settings.DB_DRIVER,
            database=settings.DB_NAME,
            username=settings.DB_USER,
            password=settings.DB_PASS,
            host=TConfig.DB_HOST,
            port=settings.DB_PORT,
        )

        async_engine = create_async_engine(
            url=db_url_object,
            echo=settings.ECHO_SQL
        )

        return async_engine

    # Get Postgres async session
    @staticmethod
    def __get_database_async_session(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        async_session = async_sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
            autoflush=True,
            class_=AsyncSession
        )

        return async_session

    # Add to Elasticsearch index
    async def add_to_index(self, post: Post) -> str:
        document = {
            'text': post.text
        }

        result = await self.async_elastic_client.index(
            index=TConfig.ELASTIC_INDEX_NAME,
            document=document,
            id=post.id
        )

        return result['result']

    # Add to Postgres database
    async def add_to_db(self, post: Post) -> Post:
        async with self.async_sessionmaker() as session:
            async with session.begin():
                session.add(post)
                await session.commit()

        return post

    # Add test data
    async def add_test_data(self, posts) -> None:
        db_tasks = [self.add_to_db(post) for post in posts]

        posts = await asyncio.gather(*db_tasks)

        self.posts = posts

        elastic_tasks = [self.add_to_index(post) for post in self.posts]

        await asyncio.gather(*elastic_tasks)

    # Delete test data
    async def remove_test_data(self) -> bool:
        rm_tasks = [Post.delete(post.id, self.async_sessionmaker, self.async_elastic_client) for post in self.posts]

        result: Tuple[bool, bool, bool] = await asyncio.gather(*rm_tasks)  # noqa

        if all(result) is True:
            return True
        else:
            return False

    # Close all connections
    async def close(self):
        await self.async_elastic_client.close()
        await self.async_engine.dispose()
