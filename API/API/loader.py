import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data import settings

app = FastAPI(
    root_path=settings.ROOT_PATH,
    debug=settings.DEV,
    title=settings.API_NAME,
    version=settings.API_VERSION,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

app.mount(
    path=settings.STATIC_PATH,
    app=StaticFiles(directory=settings.STATIC_DIR),
    name='static'
)


def custom_openapi():
    with open(settings.DOCS_FILE, 'r') as open_api:
        return json.loads(open_api.read())


app.openapi = custom_openapi
