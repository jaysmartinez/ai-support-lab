# Customer Health Monitor

Customer Health Monitor is a production-minded demo application for identifying at-risk customer accounts and managing human-approved follow-up actions.

The application calculates deterministic health scores from account activity, payment trends, product usage, support tickets, recent logins, and feature adoption.

## Features

- Dashboard with customer health totals and risk filters
- Customer search, ordering, and pagination API
- Deterministic health scores and risk classifications
- Customer detail pages with account metrics
- Follow-up creation for high-risk customers
- Persistent follow-up history
- Follow-up completion workflow
- Responsive dashboard and loading, error, and not-found states
- PostgreSQL constraints and Alembic migrations
- Automated backend tests

## Technology

### Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- PostgreSQL 17
- Alembic
- Pydantic
- pytest

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- ESLint

### Development

- Docker Compose
- uv
- npm

## Project Structure

```text
ai-support-lab/
├── alembic/             Database migrations
├── frontend/            Next.js application
├── routers/             FastAPI route modules
├── scripts/             Customer seed script
├── services/            Health-scoring service
├── tests/               Backend tests
├── database.py          Database configuration
├── main.py              FastAPI application
├── models.py            SQLAlchemy models
├── schemas.py           API request and response schemas
└── docker-compose.yml   PostgreSQL and FastAPI services
```

## Requirements

Install the following before starting:

- Docker Desktop
- Node.js 22 or later
- npm
- uv

## Local Setup

Clone the repository:

```bash
git clone https://github.com/jaysmartinez/ai-support-lab.git
cd ai-support-lab
```

Copy the backend environment example:

```bash
cp .env.example .env
```

Start PostgreSQL and FastAPI:

```bash
docker compose up --build
```

The API will be available at:

- API: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The API container automatically applies Alembic migrations before starting.

## Seed Demo Customers

In a separate terminal, run:

```bash
docker compose run --rm api uv run python scripts/seed_customers.py
```

The seed script creates 25 fictional fintech and insurance customers. It is idempotent, so existing demo customers are not duplicated.

## Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000.

The default frontend configuration connects to the API at `http://localhost:8000`.

## Environment Variables

### Backend

```env
DATABASE_URL=postgresql+psycopg://jay:devpassword@localhost:5432/ai_support_lab
CORS_ORIGINS=http://localhost:3000
```

`CORS_ORIGINS` accepts multiple comma-separated frontend addresses.

### Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Variables beginning with `NEXT_PUBLIC_` are visible in the browser and must not contain secrets.

## Database Migrations

Apply all migrations:

```bash
docker compose run --rm api uv run alembic upgrade head
```

View the current migration:

```bash
docker compose run --rm api uv run alembic current
```

Roll back one migration:

```bash
docker compose run --rm api uv run alembic downgrade -1
```

## Testing

Run the backend tests:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. uv run pytest -q
```

Check the frontend:

```bash
cd frontend
./node_modules/.bin/tsc --noEmit --incremental false
npm run lint
npm run build
```

## Customer API

- `GET /customers` — List, filter, and paginate customers
- `GET /customers/summary` — Return dashboard totals
- `GET /customers/{customer_id}` — Return customer details
- `GET /customers/{customer_id}/follow-ups` — List saved follow-ups
- `POST /customers/{customer_id}/follow-ups` — Create a follow-up
- `PATCH /customers/{customer_id}/follow-ups/{task_id}/complete` — Complete a follow-up

## Additional API Features

The repository also contains an earlier support-ticket foundation:

- User registration
- Ticket CRUD operations
- Ticket filtering, search, sorting, and pagination
- Ticket notes

Interactive documentation for every endpoint is available at http://localhost:8000/docs.

## Product Roadmap

Planned post-MVP work includes:

- Authentication and authorization
- AI-generated health explanations
- AI-recommended follow-up actions with human approval
- Customer activity history
- Task filtering and management
- Monitoring and automated deployments
