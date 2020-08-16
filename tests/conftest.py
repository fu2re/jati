"""Tests."""

import pytest
from gino import Gino
from httpx import AsyncClient
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils import (
    create_database,
    drop_database,
)

from main import (
    app,
    init_app,
)
from wallet.conf import DB_DSN_KW as DB_DSN_KW_
from wallet.conf import settings
from wallet.models import db as _db

DB_DSN_KW = DB_DSN_KW_.copy()
DB_DSN_KW['database'] = f'test_{settings.DB_DATABASE}'

DB_DSN_ALEMBIC = str(URL(
    drivername='postgresql',
    **DB_DSN_KW,
))

DB_DSN = URL(
    drivername='asyncpg',
    **DB_DSN_KW,
)


@pytest.fixture
@pytest.mark.asyncio
async def gino() -> Gino:
    """
    Database fixture.

    :return:
    """
    try:
        create_database(DB_DSN_ALEMBIC)
    except ProgrammingError:
        drop_database(DB_DSN_ALEMBIC)
        create_database(DB_DSN_ALEMBIC)
    await _db.set_bind(DB_DSN,
                       echo=settings.DB_ECHO,
                       min_size=settings.DB_POOL_MIN_SIZE,
                       max_size=settings.DB_POOL_MAX_SIZE,
                       ssl=settings.DB_SSL)
    await _db.gino.create_all()
    yield _db
    drop_database(DB_DSN_ALEMBIC)


@pytest.fixture
@pytest.mark.asyncio
async def client(gino: Gino) -> AsyncClient:  # noqa: D401
    """
    Connection.

    :param gino:
    :return:
    """
    await init_app(DB_DSN)

    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


pytest_plugins = (
    'tests.fixtures',
)
