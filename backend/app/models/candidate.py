from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    skills: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    education: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    project_summaries: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    preferred_location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    preferred_role_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    domain_interest: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="candidate_profile",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="candidate",
    )