# user-approval-system-759-769

## Social Media Backend (FastAPI)

- App entry: social_media_backend/src/api/main.py (app object)
- Generate OpenAPI: `python -m src.api.generate_openapi` (writes to social_media_backend/interfaces/openapi.json)
- Env:
  - `CORS_ALLOW_ORIGINS`: comma-separated list or `*`
  - `SQLITE_DB`: path to sqlite db file (default: data/social_media.db)

### Run locally
Install requirements:
```
pip install -r social_media_backend/requirements.txt
```

Run the app:
```
uvicorn src.api.main:app --reload --port 3001 --app-dir social_media_backend
```

### Tests
```
pytest social_media_backend/tests -q
```