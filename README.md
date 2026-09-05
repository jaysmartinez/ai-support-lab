# AI Support Lab

AI Support Lab is a FastAPI backend for managing customer support tickets. It provides ticket workflows, notes, search, sorting, pagination, user registration, and a foundation for AI-assisted support features.

## Features

- Create, view, update, and delete support tickets
- Filter tickets by priority and status
- Search and sort tickets
- Paginated ticket results
- Add notes to tickets
- Register users with hashed passwords
- Database migrations with Alembic
- Automated API tests with pytest

## Tech Stack

- Python 3.14+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- pytest
- OpenAI Python SDK

## Getting Started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/jaysmartinez/ai-support-lab.git
cd ai-support-lab
uv sync
```

Create a `.env` file and add your PostgreSQL connection string:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost/ai_support_lab
```

Run the database migrations:

```bash
uv run alembic upgrade head
```

Start the development server:

```bash
uv run uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000). Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Running Tests

```bash
uv run pytest
```

## API Overview

- `GET /health` — Check API health
- `POST /auth/register` — Register a user
- `GET /tickets` — List, filter, search, sort, and paginate tickets
- `POST /tickets` — Create a ticket
- `GET /tickets/{ticket_id}` — Get a ticket and its notes
- `PATCH /tickets/{ticket_id}` — Update a ticket
- `DELETE /tickets/{ticket_id}` — Delete a ticket
- `GET /tickets/{ticket_id}/notes` — List ticket notes
- `POST /tickets/{ticket_id}/notes` — Add a ticket note
