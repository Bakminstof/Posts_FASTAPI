import pytest
import httpx

from .t_config import TConfig


# /posts/search/{text:str}
@pytest.mark.asyncio
async def test_search_url_wo_text():
    """
    Проверка на поиск постов по без текста
    """
    TEXT = ''
    URL = f'posts/search/{TEXT}'

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.get(URL)

    expected_data = {'detail': 'Not Found'}

    assert response.status_code == 404
    assert response.json() == expected_data


# /posts/search/{text:str}
@pytest.mark.asyncio
async def test_search_url_not_allowed_method():
    """
    Проверка неподдерживаемого метода
    """
    TEXT = '123'
    URL = f'posts/search/{TEXT}'

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
