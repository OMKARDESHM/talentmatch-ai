from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.config import settings
from app.database import Base, engine
from app.middleware import RequestContextMiddleware
from app.routes import (
    admin_applications_router,
    analytics_router,
    applications_router,
    auth_router,
    candidates_router,
    jobs_router,
    matching_router,
    system_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TalentMatch AI API",
    description=(
        "Backend API for the TalentMatch AI job board."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(applications_router)
app.include_router(admin_applications_router)
app.include_router(matching_router)
app.include_router(analytics_router)
app.include_router(system_router)
