# user-approval-system-759-769

## Social Media Backend (FastAPI)

Workspace: `social_media_backend`

- App entry: `social_media_backend/src/api/main.py` (exposes FastAPI `app`)
- OpenAPI generator: `python -m src.api.generate_openapi` (writes to `social_media_backend/interfaces/openapi.json`)

## Ports
- Backend API: http://localhost:3001

## Environment Variables
Create an env file for local development:

```
cd social_media_backend
cp .env.example .env
# Adjust values as needed:
#  CORS_ALLOW_ORIGINS=http://localhost:3000
#  SQLITE_DB=./data/social_media.db
#  SESSION_TTL_MINUTES=120
```

- `CORS_ALLOW_ORIGINS`: Comma-separated list of allowed origins for CORS.
  - For the React dev server, include `http://localhost:3000`
- `SQLITE_DB`: Path to the SQLite database file. Defaults to `data/social_media.db` if not set.
  - You can point this to a DB created under the database container workspace.
- `SESSION_TTL_MINUTES`: Optional session TTL in minutes.

## Run locally

Install requirements:

```
pip install -r social_media_backend/requirements.txt
```

Start the app (port 3001):

```
uvicorn src.api.main:app --reload --port 3001 --app-dir social_media_backend
```

Open API docs:
- http://localhost:3001/docs

## Integration Notes

- Frontend (React) should set:
  - `REACT_APP_API_BASE_URL=http://localhost:3001`
- Ensure CORS is configured to include the frontend origin.
- Ensure `SQLITE_DB` points to an existing SQLite database file path (use the database container scripts to initialize if needed).

## Tests

```
pytest social_media_backend/tests -q
```
