FROM python:3.12.1-alpine

WORKDIR /app

# create the app user
# RUN addgroup -S appgroup && adduser -S app -G appgroup

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python packages
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

# copy source code
COPY . /app

# RUN chown -R app:appgroup /app
# RUN chown app:appgroup /app/manage.py
# CMD whoami && ls -lah /app && python3 manage.py runserver 0.0.0.0:8000

# change to app user
# USER app
