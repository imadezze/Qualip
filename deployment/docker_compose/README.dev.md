# Development Mode with Volume Mounts

This guide explains how to use volume mounts for local development without rebuilding Docker images for every code change.

## Overview

There are three configuration files for development:

1. **docker-compose.prod.yml** - Base production configuration
2. **docker-compose.dev-local.yml** - Backend development with hot reload
3. **docker-compose.dev-web.yml** - Web frontend development with hot reload (optional)

## Quick Start

### Backend Development Only (Recommended)

If you only work on the Python backend:

```bash
cd deployment/docker_compose

# Initial build (required once)
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml up -d --build

# After initial build, just use:
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml up -d

# View logs
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml logs -f api_server
```

**What this does:**
- Mounts your local `backend/onyx`, `backend/ee`, etc. into containers
- Enables uvicorn hot reload - changes appear instantly
- Web server still uses production build (requires rebuild for web changes)

### Full Stack Development (Backend + Web)

If you also work on the Next.js frontend:

```bash
cd deployment/docker_compose

# Initial build (required once)
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml -f docker-compose.dev-web.yml up -d --build

# After initial build:
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml -f docker-compose.dev-web.yml up -d

# View logs
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml -f docker-compose.dev-web.yml logs -f web_server
```

**What this does:**
- Everything from backend development mode
- Runs Next.js in development mode with Fast Refresh
- Changes to `web/src` appear instantly in browser
- Note: Dev mode is slower than production build

## What Gets Mounted

### Backend Services (api_server, background)
- ✅ `/app/onyx` - Main application code
- ✅ `/app/ee` - Enterprise edition code
- ✅ `/app/alembic` - Database migrations
- ✅ `/app/scripts` - Utility scripts
- ✅ `/app/shared_configs` - Configuration files
- ❌ `/app/requirements` - NOT mounted (baked into image)
- ❌ `/app/static` - NOT mounted (baked into image)

### Web Service (web_server) - Only with dev-web.yml
- ✅ `/app/src` - React/Next.js source code
- ✅ `/app/public` - Static assets
- ✅ `/app/lib` - Shared libraries
- ✅ Configuration files (tsconfig.json, etc.)
- ❌ `/app/node_modules` - NOT mounted (anonymous volume)
- ❌ `/app/.next` - NOT mounted (anonymous volume)

## Important Notes

### When You MUST Rebuild

You must rebuild the image when:
- Adding/removing Python dependencies (`requirements/*.txt`)
- Adding/removing Node dependencies (`package.json`)
- Changing Dockerfile itself
- Changing system dependencies

```bash
# Rebuild backend
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml build api_server background

# Rebuild web (if using dev-web)
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml -f docker-compose.dev-web.yml build web_server
```

### When You DON'T Need to Rebuild

Code changes to these files are instant:
- ✅ Any Python file in `backend/onyx/`, `backend/ee/`
- ✅ Database migrations in `backend/alembic/`
- ✅ Any React/TypeScript file in `web/src/` (with dev-web.yml)
- ✅ Configuration changes (ENV variables)

### Performance Considerations

**macOS Users:**
- Volume mounts use `:ro` (read-only) for better performance
- If you experience slowness, consider using Docker Desktop with VirtioFS

**File Permissions:**
- All mounts are read-only (`:ro`) to avoid permission issues
- Container runs as user `onyx` (UID 1001) for backend
- Container runs as user `nextjs` (UID 1001) for web

### Hot Reload Behavior

**Backend (uvicorn --reload):**
- Watches `/app/onyx` and `/app/ee` directories
- Automatically restarts on file changes
- Takes ~1-2 seconds to reload

**Web (Next.js Fast Refresh):**
- Only works with `docker-compose.dev-web.yml`
- Instant updates in browser (no page reload for React components)
- Full page reload for route changes

## Troubleshooting

### "Module not found" errors
- You probably changed dependencies
- Rebuild the image: `docker compose ... build <service>`

### "Permission denied" errors
- Volumes are mounted read-only (`:ro`)
- If you need to write files, remove `:ro` flag (not recommended)

### Changes not appearing
- Check if the file is actually mounted: `docker compose exec api_server ls -la /app/onyx`
- Verify hot reload is working: `docker compose logs api_server | grep reload`
- For web: ensure you're using `docker-compose.dev-web.yml`

### Slow performance on macOS
- Consider using VirtioFS in Docker Desktop settings
- Or use `:delegated` instead of `:ro` (trades consistency for speed)

### Web server fails to start in dev mode
- Check Node version matches Dockerfile.dev (node:20-alpine)
- Ensure `npm ci` completed in build: `docker compose build --no-cache web_server`

## Production Deployment

**⚠️ NEVER use development volumes in production!**

For production, always use:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The dev configurations are for local development only.

## Useful Commands

```bash
# Stop all services
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml down

# Restart single service (keeps volumes)
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml restart api_server

# View logs for specific service
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml logs -f api_server

# Execute command in running container
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml exec api_server bash

# Check mounted volumes
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml exec api_server ls -la /app/onyx

# Force rebuild (if dependencies changed)
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml build --no-cache api_server
```

## Advanced: Custom Configuration

You can create your own override file for specific needs:

```yaml
# docker-compose.dev-custom.yml
services:
  api_server:
    environment:
      - LOG_LEVEL=debug
      - SOME_CUSTOM_VAR=value
```

Then use:
```bash
docker compose -f docker-compose.prod.yml -f docker-compose.dev-local.yml -f docker-compose.dev-custom.yml up -d
```
