"""Global app configuration."""
from pathlib import Path

import dynaconf
from sqlalchemy.engine.url import URL

PROJECT_PATH = str(Path(__file__).parent.parent.resolve())
DB_DSN_KW = {
    'username': dynaconf.settings.DB_USER,
    'password': dynaconf.settings.DB_PASSWORD,
    'host': dynaconf.settings.DB_HOST,
    'port': dynaconf.settings.DB_PORT,
    'database': dynaconf.settings.DB_DATABASE,
}


dynaconf.settings.DB_DSN_ALEMBIC = DB_DSN_ALEMBIC = URL(
    drivername='postgresql',
    **DB_DSN_KW,
)

dynaconf.settings.DB_DSN = DB_DSN = URL(
    drivername='asyncpg',
    **DB_DSN_KW,
)

dynaconf.settings.logging_params = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'default': {'class': 'logging.StreamHandler'}},
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO' if not dynaconf.settings.DEBUG else 'DEBUG',
            'propagate': True,
        },
    },
}

# these settings should not be moved to env variables
# cuz it affects database migrations and only can be
# changed followed by the database migrations
dynaconf.settings.ASSET_AMOUNT_MAX_DIGITS = 12
dynaconf.settings.ASSET_AMOUNT_PRECISION = 2

settings = dynaconf.settings
