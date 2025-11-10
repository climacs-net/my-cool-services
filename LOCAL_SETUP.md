# Local MVP Setup

This guide will help you run and test the service locally using Docker Compose, without needing AWS or Kubernetes.

## Prerequisites

- Docker and Docker Compose installed
- No other services running on ports 8000 and 8181

## Quick Start

1. **Start the services:**
   ```bash
   docker-compose up --build
   ```

2. **Test the service:**
   
   The FastAPI service will be available at `http://localhost:8000`

## Testing Authorization

### GET Request (User Role)

Test with a user token (read-only access):

```bash
curl -H "token: climacs@climacs.net" http://localhost:8000/api/users
```

Expected: Returns list of users (200 OK)

### POST Request (Admin Role)

Test with an admin token (create access):

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "token: climacs@gmail.com" \
  -d '{"name":"Test User","email":"test@example.com"}' \
  http://localhost:8000/api/users
```

Expected: Creates new user (200 OK)

### Test Authorization Failures

Try POST with a user token (should fail):

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "token: climacs@climacs.net" \
  -d '{"name":"Bad User","email":"bad@example.com"}' \
  http://localhost:8000/api/users
```

Expected: 403 Forbidden

Try GET with an invalid token:

```bash
curl -H "token: invalid@example.com" http://localhost:8000/api/users
```

Expected: 403 Forbidden

## Available Tokens

| Token | Role | Permissions |
|-------|------|-------------|
| `climacs@gmail.com` | admin | GET, POST |
| `climacs@climacs.net` | user | GET only |
| `miguelnero.climacosa@gmail.com` | user | GET only |

## Service URLs

- **FastAPI Service:** http://localhost:8000
- **OPA Service:** http://localhost:8181
- **API Endpoints:**
  - GET `/api/users` - List all users
  - POST `/api/users` - Create new user

## Viewing Logs

```bash
# All services
docker-compose logs -f

# FastAPI only
docker-compose logs -f fastapi

# OPA only
docker-compose logs -f opa
```

## Stopping the Services

```bash
docker-compose down
```

To also remove volumes:

```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 8181 are already in use:

```bash
# Find what's using the port
lsof -i :8000
lsof -i :8181

# Kill the process or change ports in docker-compose.yml
```

### OPA Policy Not Loading

Check OPA logs:

```bash
docker-compose logs opa
```

Ensure `fastapi_service/policy.rego` exists and has correct syntax.

### FastAPI Can't Connect to OPA

Check if both services are on the same network:

```bash
docker network inspect my-cool-service_app-network
```

Test OPA directly:

```bash
curl -X POST http://localhost:8181/v1/data/authz/allow \
  -H "Content-Type: application/json" \
  -d '{"input": {"token": "climacs@gmail.com", "method": "POST"}}'
```

Expected: `{"result": true}`

## Development Workflow

1. Make changes to `fastapi_service/app/main.py`
2. Restart the FastAPI service: `docker-compose restart fastapi`
3. For policy changes, edit `fastapi_service/policy.rego` and restart OPA: `docker-compose restart opa`

## Architecture

```
┌─────────────────┐
│   Your Client   │
└────────┬────────┘
         │ HTTP (port 8000)
         ▼
┌─────────────────┐
│  FastAPI Service│
│   (port 8000)   │
└────────┬────────┘
         │ OPA_URL
         ▼
┌─────────────────┐
│   OPA Service   │
│   (port 8181)   │
└─────────────────┘
```

The FastAPI service sends authorization requests to OPA, which evaluates them against `policy.rego`.
