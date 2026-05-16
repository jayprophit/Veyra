# API Gateway App

This directory is the active Python package for the local API gateway.

- `application.py` owns the runnable FastAPI app.
- `database.py` owns the local persistence layer.
- `../main.py` stays as the stable `uvicorn main:app` entrypoint.
- Historical prototype modules were moved to `archive/api_app_legacy/` so the active runtime stays small and reviewable.
