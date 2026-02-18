# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service that polls the simulator, normalizes state, serves SSE, and calls Gemini.
- `simulation/`: FastAPI simulator with A* pathfinding and mission engine.
- `frontend/`: Next.js dashboard (`app/`, `components/`, `public/`).
- `docs/`: architecture and system notes.
- `docker-compose.yml`: local multi-service setup.

## Build, Test, and Development Commands
- `docker compose up --build`: run all services together (frontend, backend, simulator).
- `cd simulation && pip install -r requirements.txt && uvicorn simulator:app --port 8001 --reload`: run simulator.
- `cd backend && pip install -r requirements.txt && uvicorn main:app --port 8000 --reload`: run backend.
- `cd frontend && npm install && npm run dev`: run dashboard.
- `cd frontend && npm run build`: production build.
- `cd frontend && npm run lint`: lint frontend code.

## Coding Style & Naming Conventions
- Python: 4-space indentation, snake_case for variables/functions, PascalCase for classes. Keep type hints where present.
- TypeScript/React: 2-space indentation, PascalCase components (`Dashboard.tsx`), camelCase props/state.
- Prefer small, focused modules and keep UI state handling in `components/` rather than `app/`.

## Testing Guidelines
No automated tests are configured in this repo. If you add tests, keep them alongside the service they cover (for example `backend/tests/`, `simulation/tests/`, `frontend/__tests__/`) and update this guide with the command to run them.

## Commit & Pull Request Guidelines
Recent commits use short prefixes like `feat:`, `docs:`, and `Fix:` with one-line summaries. Follow this pattern and keep subjects imperative and concise.
PRs should include:
- A clear description of behavior changes.
- Steps to run or verify (commands).
- Screenshots for UI changes.
- Notes about config changes (env vars, ports, CORS).

## Security & Configuration Tips
- Do not commit `.env` or API keys; use environment variables.
- Frontend/backend CORS are allowlisted; update `FRONTEND_ORIGINS` when needed.
- If you change SSE payloads, update both backend and frontend consumers.

## Architecture Overview
Read `docs/ARCHITECTURE.md` before making cross-service changes to keep data flow and API contracts aligned.
