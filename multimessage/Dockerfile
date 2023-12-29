FROM python:3.11-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# for building packages like multidict
RUN apk add alpine-sdk

# needed to run wait-for-it.sh to wait for healthy db on startup
RUN apk add --no-cache bash

# install python packages
COPY requirements.txt /app

RUN python3 -m pip install -r requirements.txt --no-cache-dir

# copy source code
COPY . /app

RUN python3 manage.py makemigrations contacts --noinput

ENTRYPOINT ["sh", "entrypoint.sh"]