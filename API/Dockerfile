ARG WEBAPP_PORT

FROM python:3.10.5

WORKDIR /api

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r /api/requirements.txt

COPY API/ /api

CMD uvicorn api_wsgi:app --host 0.0.0.0 --port ${WEBAPP_PORT}
