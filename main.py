import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import models  # noqa: F401  (registers tables)
from database import Base, engine
from logging_config import setup_logging
from routers.admin import router as admin_router
from routers.user import router as user_router
from routers.votes import router as votes_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Application started (database tables ready)")
    yield
    logger.info("Application shutting down")


app = FastAPI(title="Voting System API", version="3.0.0", lifespan=lifespan)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(votes_router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        # don't restart when the app writes its own logs or database
        reload_excludes=["logs/*", "*.log", "*.db"],
    )
