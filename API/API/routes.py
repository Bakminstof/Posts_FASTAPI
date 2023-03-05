from elasticsearch import AsyncElasticsearch
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_oauth2_redirect_html,
    get_swagger_ui_html,
)

from db import async_engine, async_session, Post
from data import settings
from utils import init_db
from handlers import app
from models.models import DumpModel, PostModel, ResultsModel, DumpObj
from handlers.exceptions import APIException
from elastic.elastic_conf import node_config


@app.on_event('startup')
async def _startup():
    await init_db()

    async with AsyncElasticsearch(hosts=[node_config], request_timeout=20) as es_client:
        await Post.reindex_elastic(async_session, es_client)


@app.on_event('shutdown')
async def _shutdown():
    await async_engine.dispose()


@app.get('/posts/search/{text:str}', response_model=DumpModel, name='posts_search')
async def search(text: str):
    async with AsyncElasticsearch(hosts=[node_config]) as es_client:
        posts = await Post.search(text, async_session, es_client)

    posts_models = []

    for post in posts:
        posts_model = PostModel(
            id=post.id,
            text=post.text,
            created_date=post.created_date,
            rubrics=post.rubrics
        )
        posts_models.append(posts_model)

    result = ResultsModel(result=posts_models)
    dump = DumpObj(data=result)

    return dump


@app.delete('/posts/{post_id:int}/delete', response_model=DumpModel, name='posts_delete')
async def delete_post_by_id(post_id: int):
    async with AsyncElasticsearch(hosts=[node_config]) as es_client:
        res = await Post.delete(post_id, async_session, es_client)

    if res:
        status = 'Deleted'
        result = ResultsModel(result=status)
        dump = DumpObj(data=result)

        return dump

    else:
        type_ = 'NotFoundError'
        title_ = 'Not found'
        detail_ = f'Post with id={post_id} not found'
        status_ = 404
        instance_ = f'/posts/{post_id}/delete'

        raise APIException(
            type_=type_,
            title_=title_,
            status_=status_,
            detail_=detail_,
            instance_=instance_,
        )


@app.get("/docs", include_in_schema=False, name='docs')
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"{settings.STATIC_DIR}/swagger-ui-bundle.js",
        swagger_css_url=f"{settings.STATIC_DIR}/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False, name='redoc')
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url=f"{settings.STATIC_DIR}/redoc.standalone.js",
    )
