FROM python:3.14-alpine

COPY ./requirements.txt /app/requirements.txt

RUN apk update \
    && apk add --no-cache libstdc++ \
    && apk add --no-cache --virtual .build-deps curl gcc g++ krb5-dev \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apk del .build-deps

COPY ./app /app

WORKDIR /app

CMD ["fastapi", "run", "/app/main.py", "--port", "80"]
