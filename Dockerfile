FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10 as base

COPY ./requirements.txt /app/requirements.txt

RUN apk update \
    && apk add --no-cache --virtual .build-deps curl gcc g++ \
    && python3 -m pip install --upgrade pip setuptools wheel && pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && apk del .build-deps

FROM base as fastapi-dss-pnrp

COPY ./app /app
