import datetime
import httpx
import pytest

from db import Post
from tests.t_config import TConfig
from tests.t_database import DB


# /posts/{post_id:int}/delete
@pytest.mark.asyncio
async def test_delete_post_by_valid_int_id():
    """
    Проверка на удаление поста по валидному id
    """
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
    ]

    await db.add_test_data(test_data)

    POST_ID = db.posts[0].id
    URL = f'posts/{POST_ID}/delete'

    expected_data = {
        'data': {
            'result': 'Deleted'
        },
        'meta': TConfig.META
    }

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.delete(URL)

    assert response.status_code == 200
    assert response.json() == expected_data

    # Clear test data and close all connections #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    check_delete = await db.remove_test_data()
    await db.close()
    assert check_delete is False
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
