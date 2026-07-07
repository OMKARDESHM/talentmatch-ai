from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401
from app.database import Base, engine
from app.routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TalentMatch AI API",
    description="Backend API for the TalentMatch AI job board.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}