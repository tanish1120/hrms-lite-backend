# HRMS Lite — Backend ✅

## Project overview
A simple FastAPI backend for HRMS Lite that provides endpoints for managing employees and attendance. The project uses SQLite database for persistence.

## Tech stack
- **Framework:** FastAPI
- **Database:** SQLite
- **Server:** Uvicorn
- **Validation:** Pydantic

## Local setup & run
1. Ensure Python 3.10+ is installed.
2. (Optional but recommended) create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server with auto-reload:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
5. The API will be available at `http://localhost:8000/`. Open `http://localhost:8000/docs` for automatic API docs (Swagger UI).

## Database
- Uses `sqlite:///./hrms.db` by default. The database file (`hrms.db`) is created automatically by SQLAlchemy (`Base.metadata.create_all`) on first run.

## Production
- A `Procfile` is provided for platforms like Heroku or Render: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`.

## Assumptions & limitations
- Uses SQLite which is suitable for development and small deployments only. For production, use PostgreSQL or another robust DB.
- No authentication/authorization implemented.
- CORS is permissive (all origins allowed) for ease of local development.

---
