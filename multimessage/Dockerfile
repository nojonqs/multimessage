FROM python:3.12.1-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# for building packages like multidict
RUN apk add alpine-sdk

# install python packages
COPY requirements.txt /app

RUN pip3 install -r requirements.txt --no-cache-dir

# copy source code
COPY . /app

ENTRYPOINT ["sh", "entrypoint.sh"]