from sqlalchemy import inspect
from elasticsearch import AsyncElasticsearch
from elastic_transport import ConnectionTimeout

from db import async_engine, async_session, Base, Post
from .check_connect import check_connect
from elastic.elastic_conf import node_config


async def init_db(export_csv: bool = True) -> None:
    time = 60

    while not await check_connect():
        time -= 1
        if time == 0:
            raise ConnectionError('Timeout')
    else:
        exists = True

        async with async_engine.begin() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )

            if Post.__tablename__ not in tables:
                exists = False

                await conn.run_sync(Base.metadata.create_all)
                await async_engine.dispose()

        if exists is False and export_csv is True:
            async with AsyncElasticsearch(hosts=[node_config], request_timeout=80) as es_client:
                try:
                    await Post.load_csv('posts.csv', async_session, es_client)

                except ConnectionTimeout:
                    await Post.reindex_elastic(async_session, es_client)
