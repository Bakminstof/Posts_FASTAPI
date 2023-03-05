from __future__ import annotations

import asyncio
import csv
import datetime

from typing import AsyncIterator, Dict, List
from sqlalchemy import String, DateTime, select, delete
from elasticsearch import NotFoundError, AsyncElasticsearch
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY

from data import settings


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(
        'id', autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    text: Mapped[str] = mapped_column('text', String(), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(
        'created_date',
        DateTime(),
        default=datetime.datetime.fromisoformat(datetime.datetime.now().strftime(settings.DATETIME_FORMAT))
    )
    rubrics: Mapped[ARRAY] = mapped_column('rubrics', ARRAY(String))

    @classmethod
    async def __add_to_index(cls, index_name: str, post: Post, es_client: AsyncElasticsearch) -> None:
        document = {
            'text': post.text
        }

        await es_client.index(
            index=index_name,
            document=document,
            id=post.id
        )

    @classmethod
    def __extract_cvs_data(cls, file: str) -> Dict[str, List]:
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')

            columns_names = []
            columns_data = []

            for row in reader:
                if not columns_names:
                    columns_names = row
                else:
                    text = row[0]
                    created_date = datetime.datetime.fromisoformat(row[1])
                    rubrics = eval(row[2])

                    data = [text, created_date, rubrics]

                    columns_data.append(data)

        return {
            'columns_names': columns_names,
            'columns_data': columns_data
        }

    @classmethod
    async def load_csv(
            cls,
            file: str,
            async_session: async_sessionmaker[AsyncSession],
            es_client: AsyncElasticsearch
    ) -> None:
        posts = []

        for row in cls.__extract_cvs_data(file)['columns_data']:
            post = Post(
                text=row[0],
                created_date=row[1],
                rubrics=row[2]
            )

            posts.append(post)

        async with async_session() as session:
            async with session.begin():
                session.add_all(posts)
                await session.commit()

        index_tasks = [cls.__add_to_index(settings.ELASTIC_INDEX_NAME, post, es_client) for post in posts]

        await asyncio.gather(*index_tasks)

    @classmethod
    async def __get_elements_from_db_by_id(
            cls,
            ids: List[int],
            async_session: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[Post]:
        async with async_session() as session:
            stmt = select(cls).filter(cls.id.in_(ids))

            stream_scalars = await session.stream_scalars(stmt.order_by(cls.created_date))

            async for row in stream_scalars:
                yield row

    @classmethod
    async def __search_in_index_by_text(cls, text: str, es_client: AsyncElasticsearch) -> list:
        query = {
            "match": {
                "text": {
                    "query": text,
                }
            }
        }

        result = await es_client.search(
            index=settings.ELASTIC_INDEX_NAME,
            query=query,
            size=20
        )

        hits = result['hits']['hits']

        return hits

    @classmethod
    async def search(
            cls,
            text: str,
            async_session: async_sessionmaker[AsyncSession],
            es_client: AsyncElasticsearch
    ) -> List[Post]:
        hits = await cls.__search_in_index_by_text(text, es_client)
        ids = [int(elem['_id']) for elem in hits]
        result = [elem async for elem in cls.__get_elements_from_db_by_id(ids, async_session)]

        return result

    @classmethod
    async def __delete_from_index(cls, id_: int, es_client: AsyncElasticsearch) -> str:
        try:
            result = await es_client.delete(index=settings.ELASTIC_INDEX_NAME, id=str(id_))
            result = result['result']

        except NotFoundError:
            result = 'not_found'

        return result

    @classmethod
    async def __delete_from_db_by_id(cls, id_: int, async_session: async_sessionmaker[AsyncSession]) -> bool:
        async with async_session() as session:
            stmt = delete(cls).where(cls.id == id_)
            res = await session.execute(stmt)
            await session.commit()

            return bool(res.__getattribute__('rowcount'))

    @classmethod
    async def delete(
            cls,
            id_: int,
            async_session: async_sessionmaker[AsyncSession],
            es_client: AsyncElasticsearch
    ) -> bool:
        index_result = await cls.__delete_from_index(id_, es_client)
        db_result = await cls.__delete_from_db_by_id(id_, async_session)

        if db_result and index_result == 'deleted':
            return True
        else:
            return False

    @classmethod
    async def read_all(cls, async_session: async_sessionmaker[AsyncSession]):
        async with async_session() as session:
            stmt = select(cls)
            stream_scalars = await session.stream_scalars(stmt)

            async for row in stream_scalars:
                yield row

    @classmethod
    async def reindex_elastic(cls, async_session: async_sessionmaker[AsyncSession], es_client: AsyncElasticsearch):
        posts = [elem async for elem in cls.read_all(async_session)]
        index_tasks = [cls.__add_to_index(settings.ELASTIC_INDEX_NAME, post, es_client) for post in posts]

        await asyncio.gather(*index_tasks)
