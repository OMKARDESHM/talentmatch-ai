from app.routes.auth import router as auth_router
from app.routes.jobs import router as jobs_router


__all__ = [
    "auth_router",
    "jobs_router",
]