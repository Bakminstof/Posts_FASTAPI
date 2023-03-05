import asyncio

from elasticsearch import AsyncElasticsearch

from db import async_engine
from elastic.elastic_conf import node_config


async def check_connect() -> bool:
    async with AsyncElasticsearch(hosts=[node_config]) as es_client:
        elastic_ping = await es_client.ping()

        if elastic_ping:
            try:
                await async_engine.connect()
            except Exception:
                check = False

            else:
                check = True

            finally:
                await async_engine.dispose()
        else:
            check = False

    await asyncio.sleep(1)
    return check
