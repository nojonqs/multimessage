FROM python:3.11-bullseye

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# for building packages like multidict
RUN apt-get update
RUN apt-get --assume-yes install build-essential systemd

# needed to run wait-for-it.sh to wait for healthy db on startup
RUN apt-get --assume-yes install bash

# for signal related stuff
RUN curl -sL -o /etc/apt/trusted.gpg.d/morph027-signal-cli.asc https://packaging.gitlab.io/signal-cli/gpg.key
RUN echo "deb https://packaging.gitlab.io/signal-cli signalcli main" | tee /etc/apt/sources.list.d/morph027-signal-cli.list
RUN apt-get update
RUN apt-get --assume-yes install signal-cli-native signal-cli-service

# needed by pydbus
RUN apt-get --assume-yes install libcairo2-dev libgirepository1.0-dev

# install python packages
COPY requirements_prod.txt /app

RUN python3 -m pip install -r requirements_prod.txt --no-cache-dir

# copy source code
COPY . /app

RUN python3 manage.py makemigrations contacts --noinput --settings multimessage.settings_prod

ENTRYPOINT ["sh", "entrypoint.sh"]