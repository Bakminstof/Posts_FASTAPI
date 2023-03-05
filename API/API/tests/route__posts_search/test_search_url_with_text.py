import datetime
import pytest
import httpx

from db import Post
from tests.t_config import TConfig
from tests.t_database import DB


# /posts/search/{text:str}
@pytest.mark.asyncio
async def test_search_url_with_text():
    """
    Проверка на поиск постов по заданному тексту
    """
    TEXT = 'test'
    URL = f'posts/search/{TEXT}'

    db = DB()

    test_data = [
        Post(
            text='Test 1',
            created_date=datetime.datetime(
                year=2023,
                month=1,
                day=2,
                hour=2,
                minute=44,
                second=4
            ),
            rubrics=['12', '3']
        ),
        Post(
            text='Test test 2',
            created_date=datetime.datetime(
                year=2023,
                month=1,
                day=2,
                hour=12,
                minute=55,
                second=14
            ),
            rubrics=['1', '4']
        ),
        Post(
            text='3 test 2 foo',
            created_date=datetime.datetime(
                year=2023,
                month=1,
                day=2,
                hour=21,
                minute=22,
                second=35
            ),
            rubrics=['121', '66']
        ),
    ]

    await db.add_test_data(test_data)

    posts = await Post.search(TEXT, db.async_sessionmaker, db.async_elastic_client)

    expected_data = {
        'data': {
            'result': [
                {
                    'id': post.id,
                    'text': post.text,
                    'created_date': post.created_date.strftime(TConfig.DATETIME_FORMAT),
                    'rubrics': post.rubrics
                } for post in posts
            ]
        },
        'meta': TConfig.META
    }

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.get(URL)

    # Clear test data and close all connections #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    check_delete = await db.remove_test_data()
    await db.close()
    assert check_delete is True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    assert response.status_code == 200
    assert response.json() == expected_data
