# Quick Start: Development Mode

## Starting the App

```bash
cd deployment/docker_compose

# Backend dev + production frontend (FAST, recommended)
make dev-backend-fast

# OR: Backend dev + frontend dev with hot reload (SLOW first load)
make dev-backend-hot
```

## Accessing the App

| URL | What it is |
|-----|------------|
| **http://localhost** (port 80) | **Use this one!** Goes through nginx, API calls work |
| http://localhost:8080 | Backend API directly |
| http://localhost:3000 | Frontend only (no API proxy — don't use for testing) |

**Test credentials:** `test@example.com` / `test1234`

## When Code Changes

| What you changed | What to do |
|------------------|------------|
| **Python** (`backend/onyx/`, `backend/ee/`) | **Nothing** — auto-reloads instantly |
| **Frontend** (`web/src/`) in `dev-backend-fast` mode | Run `make rebuild-web` |
| **Frontend** (`web/src/`) in `dev-backend-hot` mode | **Nothing** — hot reloads instantly |
| **Python dependencies** (`requirements/*.txt`) | Run `make dev-backend-fast` (full rebuild) |
| **Node dependencies** (`web/package.json`) | Run `make dev-backend-fast` (full rebuild) |

## Useful Commands

```bash
# Stop all containers (keeps data)
make down

# Stop and delete all data
make down-volumes

# Restart just the API server
make restart-api

# Restart just the web server
make restart-web

# Rebuild only the web frontend
make rebuild-web

# View logs
make logs              # all services
make logs-api          # API server only
make logs-web          # web server only

# Check container status
docker compose -p onyx ps
```

## Troubleshooting

- **"Backend is currently unavailable"** — Make sure you're accessing **http://localhost** (port 80), not port 3000
- **Containers crash on startup** — Check logs with `make logs`
- **Python changes not detected** — Files are mounted read-only; check `docker compose -p onyx exec api_server ls -la /app/onyx`
