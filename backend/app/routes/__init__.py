from app.routes.admin_applications import (
    router as admin_applications_router,
)
from app.routes.applications import router as applications_router
from app.routes.auth import router as auth_router
from app.routes.candidates import router as candidates_router
from app.routes.jobs import router as jobs_router
from app.routes.matching import router as matching_router

__all__ = [
    "admin_applications_router",
    "applications_router",
    "auth_router",
    "candidates_router",
    "jobs_router",
    "matching_router",
]