import pytest
import httpx

from tests.t_config import TConfig


# /redoc
@pytest.mark.asyncio
async def test_redoc_url():
    """
    Проверка redoc URL
    """
    url = "/redoc"

    async with httpx.AsyncClient(
            app=TConfig.APP,
            base_url=TConfig.BASE_URL,
            timeout=TConfig.TIMEOUT,
            http2=TConfig.HTTP2,
    ) as async_client:
        response = await async_client.get(url)

    assert response.status_code == 200
    assert 'ReDoc' in response.text


# /redoc
@pytest.mark.asyncio
async def test_not_allowed_method():
    """
    Проверка неподдерживаемого метода
    """
    URL = '/redoc'

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
