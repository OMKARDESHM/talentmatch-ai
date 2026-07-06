from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    required_skills: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    experience_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    role_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=JobStatus.OPEN.value,
        nullable=False,
    )
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_by: Mapped["User"] = relationship(
        back_populates="jobs",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job",
    )