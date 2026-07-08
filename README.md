# TalentMatch AI

TalentMatch AI is a full-stack AI-powered job board that helps candidates discover relevant opportunities through explainable job matching while giving administrators a structured hiring workflow and recruitment analytics.

The application combines a React frontend with a FastAPI backend, role-based authentication, candidate profiles, job management, application tracking, explainable matching, analytics dashboards, deployment health checks, request observability, CI quality gates, and a containerized deployment stack.

## Features

### Candidate Workspace

Candidates can:

- Sign in through role-based authentication.
- Create and update a candidate profile.
- Maintain skills, education, project experience, preferred location, role type, and domain interests.
- Search open jobs using filters.
- Describe desired opportunities using natural language.
- Receive ranked job recommendations with explainable match scores.
- Apply to available jobs.
- Track submitted applications and hiring statuses.
- View application, job, and profile completeness analytics.

### Admin Workspace

Administrators can:

- Sign in to the protected admin workspace.
- Create and manage job opportunities.
- Review open and closed jobs.
- Inspect applicants for individual jobs.
- Review candidate profile snapshots.
- Move applications through applied, shortlisted, and rejected states.
- View hiring and application pipeline analytics.

### Explainable Job Matching

The matching engine evaluates candidate intent against job data and produces ranked recommendations.

Matching considers:

- Skills.
- Preferred location.
- Experience level.
- Role type.
- Domain interests.
- Natural-language search intent.

Recommendations include match scores and explanations so candidates can understand why a job was ranked.

### Reliability and Observability

The backend includes:

- Centralized environment-based configuration.
- JWT configuration validation.
- Configurable database connectivity.
- Configurable CORS origins.
- Health and readiness endpoints.
- Database readiness checks.
- Request ID generation and propagation.
- Request completion logging.
- Request duration and response status logging.

The frontend includes:

- Authentication session restoration.
- Session recovery for temporary API failures.
- Protected role-based routes.
- Application-level error recovery.
- Loading, empty, and error states.

## Technology Stack

### Frontend

- React 19
- Vite
- React Router
- Fetch API
- Oxlint

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- PyJWT
- pwdlib with Argon2 password hashing
- Pytest
- Uvicorn

### Deployment and Automation

- Docker
- Docker Compose
- Nginx
- GitHub Actions

## Project Structure

```text
talentmatch-ai/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── middleware/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   ├── tests/
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── seed.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── layouts/
│   │   └── pages/
│   ├── .env.example
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── compose.yml
└── README.md
```

## Local Development

### Backend Setup

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt

cp .env.example .env
```

Configure the backend environment:

```env
DATABASE_URL=sqlite:///./talentmatch.db
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Seed the development database:

```bash
python seed.py
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend is available at:

```text
http://127.0.0.1:8000
```

Health endpoints:

```text
GET /health
GET /ready
```

### Frontend Setup

Open another terminal:

```bash
cd frontend

npm ci

cp .env.example .env

npm run dev
```

The frontend is available at:

```text
http://127.0.0.1:5173
```

Vite proxies `/api` requests to the local FastAPI backend during development.

## Demo Accounts

The seeded development environment provides two demo accounts.

### Candidate

```text
Email: candidate@talentmatch.dev
Password: CandidatePass123!
```

### Administrator

```text
Email: admin@talentmatch.dev
Password: AdminPass123!
```

The current application does not provide public account registration. Authentication intentionally uses seeded demo accounts for the current project workflow.

## Docker Deployment

Build and start the complete application stack:

```bash
docker compose up --build -d
```

Check container status:

```bash
docker compose ps
```

The containerized application is available at:

```text
http://127.0.0.1:8080
```

Nginx serves the React production build and proxies `/api` requests to the FastAPI backend container.

The backend uses a persistent Docker volume for the SQLite database.

Stop the application:

```bash
docker compose down
```

Remove the application and persistent database volume:

```bash
docker compose down -v
```

For non-development environments, provide a secure JWT secret:

```bash
JWT_SECRET_KEY="$(openssl rand -hex 32)" docker compose up --build -d
```

## API Health Checks

Application liveness:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Application readiness:

```bash
curl http://127.0.0.1:8000/ready
```

Expected response:

```json
{
  "status": "ready",
  "database": "reachable"
}
```

Through the Docker frontend proxy:

```bash
curl http://127.0.0.1:8080/api/health
curl http://127.0.0.1:8080/api/ready
```

## Testing and Quality Checks

Run backend tests:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Run frontend linting:

```bash
cd frontend
npm run lint
```

Build the production frontend:

```bash
npm run build
```

Check Git whitespace errors:

```bash
git diff --check
```

## Continuous Integration

The GitHub Actions CI workflow runs on pushes and pull requests.

The backend quality gate:

- Sets up Python 3.12.
- Installs backend dependencies.
- Runs the complete Pytest suite.

The frontend quality gate:

- Sets up Node.js 22.
- Installs dependencies using `npm ci`.
- Runs Oxlint.
- Builds the Vite production bundle.

## API Architecture

Backend routes are organized by application responsibility:

- `/auth` - authentication and current-user operations.
- `/jobs` - job management and filtering.
- `/candidates` - candidate profile operations.
- `/applications` - candidate application workflow.
- Admin application routes - hiring pipeline administration.
- `/matching` - explainable job matching.
- `/analytics` - candidate and admin dashboard analytics.
- `/health` - application liveness.
- `/ready` - application and database readiness.

Protected endpoints use JWT bearer authentication and role-based dependencies for candidate and administrator authorization.

## Request Observability

Every HTTP response includes an `X-Request-ID` header.

Clients may provide a valid request ID:

```bash
curl \
  http://127.0.0.1:8000/health \
  -H "X-Request-ID: manual-request-123"
```

The backend preserves valid request IDs and generates UUID request IDs when the header is missing or invalid.

Request completion logs include:

- Request ID.
- HTTP method.
- Request path.
- Response status code.
- Request duration.

Sensitive authorization tokens and query strings are not included in request completion logs.

## Current Scope

TalentMatch AI is implemented as a portfolio and engineering-assignment application.

The current authentication workflow intentionally uses seeded demo accounts and does not expose public registration.

SQLite is used for the current deployment scope. Environment-based database configuration allows the persistence layer to be changed in a future production architecture.

## Future Improvements

Potential extensions include:

- Public candidate registration.
- Administrator invitation workflows.
- PostgreSQL deployment.
- Database migrations with Alembic.
- External LLM-assisted intent extraction.
- Embedding-based semantic job retrieval.
- Resume upload and structured resume parsing.
- Email notifications.
- Password reset workflows.
- Pagination for large job and application datasets.
- Dedicated frontend automated tests.
- Cloud deployment and managed observability.

## License

This project is currently maintained as a portfolio and engineering-assignment project.