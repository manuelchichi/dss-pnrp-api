FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

COPY ./requirements.txt /app/requirements.txt

RUN apk update \
    && apk add --no-cache --virtual .build-deps curl gcc g++ \
    && pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && apk del .build-deps

COPY ./app /app
