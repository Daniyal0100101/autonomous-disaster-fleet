# RescueRoute AI Frontend

Next.js dashboard for live mission control.

## Run
```bash
cd frontend
npm install
npm run dev
```

## Environment
- Create a `.env.local` file with `NEXT_PUBLIC_API_BASE_URL=...` (no quotes). Restart dev server after changes.

Common values:
- `NEXT_PUBLIC_API_BASE_URL=http://localhost` when routing through a reverse proxy host.
- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` when calling the backend directly in local development.

## Notes
- Dashboard connects via SSE to `/api/v1/stream`.
- If map appears static, verify backend can reach simulator (`:8001`).
- Event log panel reflects real stream activity and mission status transitions.
