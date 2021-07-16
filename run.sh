docker run --name flaskapp --restart=always \
    -p 8000:80 \
    -v $PWD:/app \
    -d jazzdd/alpine-flask
