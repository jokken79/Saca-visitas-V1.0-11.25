# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI app with routers in `auth.py`, `haken_saki.py`, and `export.py`; entrypoint `main.py`; database pool helpers in `database.py`; Excel/CSV utilities in `excel_generator.py`; Python deps in `requirements.txt`.
- `database/init.sql`: PostgreSQL schema for employees, contracts, haken_saki companies, and related reference data.
- `frontend/`: Static Tailwind/vanilla JS pages (`index.html`, `employees.html`, `haken-saki.html`, `import.html`, `login.html`, etc.) plus shared validation helpers in `validators.js`.
- `uploads/` and `generated/`: mounted for file imports/exports (persist across container restarts). `nginx/` hosts the static frontend. `docker-compose.yml` orchestrates db/api/frontend/redis/adminer.

## Build, Test, and Development Commands
- `docker compose up -d`: start PostgreSQL (5433 external), FastAPI API (8100), nginx frontend (8180), Redis (6380), Adminer (8181).
- `docker compose logs -f api`: tail backend logs; use for debugging startup or request errors.
- Local-only tweak: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload` (uses local env vars; skips Docker).
- Frontend: with compose running, open `http://localhost:8180/index.html` (and other pages) to hit the live API.

## Coding Style & Naming Conventions
- Python: 4-space indent; snake_case for functions/vars; PascalCase for Pydantic models. Keep validators centralized (`Validators` class) and share request schemas between endpoints.
- API: prefer REST verbs on `/api/*` prefixes already used (employees, haken-saki, alerts, validate). Return JSON-friendly primitives; avoid duplicating routes.
- SQL: add tables/columns in `database/init.sql` using snake_case and include timestamps/audit fields when relevant.
- Frontend JS/HTML: keep scripts modular in `validators.js` when possible; use descriptive data-* attrs and kebab-case ids/classes; stick to Tailwind utility patterns already present.

## Testing Guidelines
- No automated suite yet; prioritize manual flows: employee CRUD, visa alerts, haken-saki creation/update, CSV/Excel export, OCR import payloads.
- With compose running, exercise API via Swagger UI at `http://localhost:8100/docs` and confirm the same operations through the frontend pages.
- Document manual test notes in your PR (inputs used, expected outputs, screenshots of table updates or modals).

## Commit & Pull Request Guidelines
- Recent history favors short, descriptive messages (e.g., "Add Haken Saki editor page"); keep present-tense/imperative and scope-focused.
- Reference related issues/tickets when available; mention env or data dependencies (`.env`, sample imports).
- PRs: include summary of changes, screenshots/GIFs for UI updates, and API samples when altering contract. Note any manual tests performed and rollback steps if relevant.

## Security & Configuration Tips
- Copy `.env.example` to `.env` and set `DB_PASSWORD`, `SECRET_KEY`, and ports before running locally. Never commit secrets or real personal data.
- Keep `uploads/` and `generated/` out of version control; use sanitized fixtures when sharing files. Limit CORS/DEBUG overrides to dev environments.
