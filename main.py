import uvicorn
from fastapi import FastAPI

from wallet.conf import settings
from wallet.models import db
from wallet.views import router


async def init_app(db_dsn=settings.DB_DSN):
    await db.set_bind(db_dsn,
                      echo=settings.DB_ECHO,
                      min_size=settings.DB_POOL_MIN_SIZE,
                      max_size=settings.DB_POOL_MAX_SIZE,
                      ssl=settings.DB_SSL)


app = FastAPI(title='jati',
              version='0.1.0',
              on_startup=[init_app])
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
