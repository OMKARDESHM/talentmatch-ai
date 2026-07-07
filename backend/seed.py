import json

from sqlalchemy import select

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Application,
    ApplicationStatus,
    CandidateProfile,
    Job,
    JobStatus,
    User,
    UserRole,
)


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == "admin@talentmatch.dev")
        )

        if existing_user:
            print("Seed data already exists. Skipping.")
            return

        admin = User(
            email="admin@talentmatch.dev",
            password_hash=hash_password("AdminPass123!"),
            role=UserRole.ADMIN.value,
        )

        candidate_user = User(
            email="candidate@talentmatch.dev",
            password_hash=hash_password("CandidatePass123!"),
            role=UserRole.CANDIDATE.value,
        )

        db.add_all([admin, candidate_user])
        db.flush()

        candidate = CandidateProfile(
            user_id=candidate_user.id,
            name="Demo Candidate",
            skills="Python, FastAPI, SQL",
            education="B.E. in Computer Engineering",
            project_summaries=(
                "Built an AI-assisted data analysis application "
                "and backend API projects using Python."
            ),
            preferred_location="Pune",
            preferred_role_type="Backend",
            domain_interest="Healthcare",
        )

        jobs = [
            Job(
                title="Python Backend Engineer",
                description=(
                    "Build backend APIs for a digital healthcare platform "
                    "using Python and FastAPI."
                ),
                required_skills="Python, FastAPI, PostgreSQL",
                experience_level="Entry Level",
                location="Pune",
                role_type="Backend",
                domain="Healthcare",
                status=JobStatus.OPEN.value,
                created_by_id=admin.id,
            ),
            Job(
                title="Java Backend Developer",
                description=(
                    "Develop transaction services for a financial technology "
                    "platform."
                ),
                required_skills="Java, Spring Boot, MySQL",
                experience_level="Mid Level",
                location="Mumbai",
                role_type="Backend",
                domain="FinTech",
                status=JobStatus.OPEN.value,
                created_by_id=admin.id,
            ),
            Job(
                title="Healthcare Data Analyst",
                description=(
                    "Analyse healthcare datasets and build reporting "
                    "dashboards for operational teams."
                ),
                required_skills="Python, SQL, Tableau",
                experience_level="Entry Level",
                location="Pune",
                role_type="Data Analyst",
                domain="Healthcare",
                status=JobStatus.OPEN.value,
                created_by_id=admin.id,
            ),
            Job(
                title="React Frontend Developer",
                description=(
                    "Build customer-facing interfaces for an e-commerce "
                    "platform."
                ),
                required_skills="React, JavaScript, CSS",
                experience_level="Entry Level",
                location="Bengaluru",
                role_type="Frontend",
                domain="E-commerce",
                status=JobStatus.OPEN.value,
                created_by_id=admin.id,
            ),
            Job(
                title="Machine Learning Engineer",
                description=(
                    "Develop machine learning models for healthcare "
                    "prediction workflows."
                ),
                required_skills="Python, PyTorch, Machine Learning",
                experience_level="Mid Level",
                location="Remote",
                role_type="Machine Learning",
                domain="Healthcare",
                status=JobStatus.OPEN.value,
                created_by_id=admin.id,
            ),
            Job(
                title="Legacy Python Developer",
                description=(
                    "Maintain an internal Python service that is no longer "
                    "accepting new applicants."
                ),
                required_skills="Python, Flask, SQL",
                experience_level="Entry Level",
                location="Pune",
                role_type="Backend",
                domain="Healthcare",
                status=JobStatus.CLOSED.value,
                created_by_id=admin.id,
            ),
        ]

        db.add(candidate)
        db.add_all(jobs)
        db.flush()

        snapshot = {
            "name": candidate.name,
            "skills": candidate.skills,
            "education": candidate.education,
            "project_summaries": candidate.project_summaries,
            "preferred_location": candidate.preferred_location,
            "preferred_role_type": candidate.preferred_role_type,
            "domain_interest": candidate.domain_interest,
        }

        sample_application = Application(
            candidate_id=candidate.id,
            job_id=jobs[2].id,
            status=ApplicationStatus.APPLIED.value,
            profile_snapshot=json.dumps(snapshot),
        )

        db.add(sample_application)
        db.commit()

        print("Seed data created successfully.")
        print("Users created: 2")
        print("Candidate profiles created: 1")
        print(f"Jobs created: {len(jobs)}")
        print("Applications created: 1")


if __name__ == "__main__":
    seed_database()