# REST API

DEVON includes a FastAPI-based REST API server that exposes every core
capability over HTTP. Use it when you need to manage models remotely --
for example, from KITT or a CI pipeline -- without installing DEVON on
the client machine.

## Prerequisites

Install the optional API dependencies:

```bash
poetry install --extras api
```

This adds FastAPI and Uvicorn. The standard CLI continues to work without
these extras.

## Starting the Server

```bash
devon serve                             # http://127.0.0.1:8000
devon serve --host 0.0.0.0 --port 9000 # bind to all interfaces
devon serve --reload                    # auto-reload on code changes (dev)
```

!!! tip
    For containerized deployments, see the
    [Docker Deployment](docker.md) guide instead of running `devon serve`
    directly.

## Authentication

Authentication is **optional**. Set the `DEVON_API_KEY` environment variable
to enable bearer token auth on all `/api/v1/*` endpoints. The `/health`
endpoint is always unauthenticated.

```bash
DEVON_API_KEY=my-secret devon serve
```

Clients pass the token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer my-secret" http://localhost:8000/api/v1/models
```

When `DEVON_API_KEY` is unset or empty, all requests are allowed without a
token.

## Endpoint Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth) |
| GET | `/api/v1/search` | Search remote models |
| GET | `/api/v1/models` | List local models |
| GET | `/api/v1/models/{source}/{model_id}` | Model info (local + remote) |
| DELETE | `/api/v1/models/{source}/{model_id}` | Remove a model |
| POST | `/api/v1/downloads` | Download a model |
| GET | `/api/v1/status` | Storage stats |
| POST | `/api/v1/clean` | Clean unused models |
| POST | `/api/v1/export` | Export model list |

See the [REST API Reference](../reference/rest-api.md) for full request and
response schemas.

---

## Usage Examples

### Health check

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "version": "1.0.0"}
```

### Search for models

Query parameters mirror the CLI's `--provider`, `--params`, `--size`,
`--format`, `--task`, `--license`, and `--limit` flags:

```bash
curl "http://localhost:8000/api/v1/search?provider=qwen&params=7b&limit=3"
```

### List local models

```bash
curl http://localhost:8000/api/v1/models
```

Filter by source:

```bash
curl "http://localhost:8000/api/v1/models?source=huggingface"
```

### Get model info

Returns both local storage info and remote metadata:

```bash
curl http://localhost:8000/api/v1/models/huggingface/Qwen/Qwen2.5-7B-Instruct
```

### Download a model

```bash
curl -X POST http://localhost:8000/api/v1/downloads \
  -H "Content-Type: application/json" \
  -d '{"model_id": "Qwen/Qwen2.5-7B-Instruct"}'
```

!!! warning "Long-running request"
    Downloads run synchronously in the request thread. Set a long client
    timeout (e.g., 30 minutes) for large models.

Optional fields in the request body:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model_id` | string | *(required)* | Model identifier |
| `source` | string | `"huggingface"` | Source plugin name |
| `force` | bool | `false` | Re-download even if already present |
| `include_patterns` | list[string] | `null` | Glob patterns to filter files |

### Delete a model

```bash
curl -X DELETE http://localhost:8000/api/v1/models/huggingface/Qwen/Qwen2.5-7B-Instruct
```

### Storage status

```bash
curl http://localhost:8000/api/v1/status
```

### Clean unused models

```bash
curl -X POST http://localhost:8000/api/v1/clean \
  -H "Content-Type: application/json" \
  -d '{"unused": true, "days": 30}'
```

Preview without deleting:

```bash
curl -X POST http://localhost:8000/api/v1/clean \
  -H "Content-Type: application/json" \
  -d '{"unused": true, "days": 30, "dry_run": true}'
```

### Export model list

```bash
curl -X POST http://localhost:8000/api/v1/export \
  -H "Content-Type: application/json" \
  -d '{"format": "kitt"}'
```

---

## Environment Variables

The API server respects these environment variables:

| Variable | Description |
|----------|-------------|
| `DEVON_API_KEY` | Bearer token for authentication (empty = no auth) |
| `DEVON_STORAGE_PATH` | Override the model storage directory |
| `DEVON_CONFIG_PATH` | Override the config file path |
| `HF_TOKEN` | HuggingFace token for gated model access |

---

## Limitations

- **Single worker** — the default runs one Uvicorn worker to avoid race
  conditions on JSON index writes. Do not increase worker count without
  external write coordination.
- **Synchronous downloads** — model downloads block the request thread.
  Background task support may be added in a future release.

---

## Further Reading

- [REST API Reference](../reference/rest-api.md) -- full request/response schemas
- [Docker Deployment](docker.md) -- containerized deployment
- [KITT Integration](kitt-integration.md) -- using the API with KITT
