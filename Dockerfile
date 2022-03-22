FROM python:3.9.9-slim-bullseye

WORKDIR /bank_account_app

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install --user poetry

ENV PATH="${PATH}:/root/.local/bin"

COPY ./ ./

RUN poetry config virtualenvs.create false

RUN poetry install