FROM python:3.12.1-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python packages
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

# copy source code
COPY . /app
