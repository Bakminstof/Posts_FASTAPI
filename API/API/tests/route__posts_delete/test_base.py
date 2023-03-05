import pytest
import httpx

from tests.t_config import TConfig


# /posts/{post_id:int}/delete
@pytest.mark.asyncio
async def test_delete_post_by_invalid_int_id():
    """
    Проверка на удаление поста по невалидному строковому id
    """
    POST_ID = - 2
    URL = f'/posts/{POST_ID}/delete'

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.post(URL)

    expected_data = {'detail': 'Not Found'}

    assert response.status_code == 404
    assert response.json() == expected_data


# /posts/{post_id:int}/delete
@pytest.mark.asyncio
async def test_delete_post_by_invalid_string_id():
    """
    Проверка на удаление поста по невалидному строковому id
    """
    POST_ID = 'Foo'
    URL = f'/posts/{POST_ID}/delete'

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.post(URL)

    expected_data = {'detail': 'Not Found'}

    assert response.status_code == 404
    assert response.json() == expected_data


# /posts/{post_id:int}/delete
@pytest.mark.asyncio
async def test_not_allowed_method():
    """
    Проверка неподдерживаемого метода
    """
    POST_ID = 1
    URL = f'/posts/{POST_ID}/delete'

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.post(URL)

    expected_data = {'detail': 'Method Not Allowed'}

    assert response.status_code == 405
    assert response.json() == expected_data


# /posts/{post_id:int}/delete
@pytest.mark.asyncio
async def test_delete_post_by_valid_int_id_not_in_db():
    """
    Проверка на удаление поста по валидному id, которого нет в базе данных
    """
    POST_ID = 123456789
    URL = f'posts/{POST_ID}/delete'

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.delete(URL)

    expected_data = {
        'error': {
            'type': 'NotFoundError',
            'title': 'Not found',
            'detail': f'Post with id={POST_ID} not found',
            'status': 404,
            'instance': f'/posts/{POST_ID}/delete',
            'timestamp': None
        }
    }

    data = response.json()
    data['error']['timestamp'] = None

    assert response.status_code == 404
    assert data == expected_data
