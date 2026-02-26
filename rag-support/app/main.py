from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.db.session import Base, engine
from app.utils.config import get_settings
from app.utils.logging import setup_logging

settings = get_settings()
setup_logging()

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
