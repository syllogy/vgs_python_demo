# vgs_python_demo base container

FROM python:3-alpine3.7

# install console and node
RUN apk update &&\
    apk add --no-cache bash \
    openssl \
    make    \
    nodejs  \
    git &&\
    mkdir -p /opt/app

# Done