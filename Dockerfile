FROM python:3.8-alpine as base

FROM base as builder
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev make postgresql-dev
RUN pip install poetry
COPY poetry.lock pyproject.toml /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && poetry install

FROM base
RUN apk add --no-cache postgresql-libs
COPY --from=builder /env /env
WORKDIR /src
COPY tox.ini main.py alembic.ini .isort.cfg config ./
COPY alembic ./alembic
COPY tests ./tests
COPY wallet ./wallet
CMD ["/env/bin/python",  "main.py"]