# DEVON - Discovery Engine and Vault for Open Neural models

> *"DEVON manages the models. KITT tests them."*

CLI tool and REST API for discovering, downloading, and managing LLM models from HuggingFace and other sources.

[**Full Documentation**](https://kirizan.github.io/devon/) | [**CLI Reference**](https://kirizan.github.io/devon/reference/cli/)

## Features

- **Smart search** — filter by provider, size, parameters, format, task, license
- **Easy download** — by URL or model ID with automatic resume
- **Local vault** — organized storage with disk usage tracking
- **KITT integration** — export model paths for inference testing
- **Source plugins** — extensible architecture for model sources
- **YAML configuration** — deep-merged config with sensible defaults
- **REST API** — FastAPI server for remote model management
- **Docker ready** — containerize with a single volume mount

## Quick Start

```bash
# Install
poetry install
eval $(poetry env activate)

# Search for models
devon search --provider qwen --params 30b --format gguf

# Download by URL
devon download https://huggingface.co/Qwen/Qwen2.5-32B-Instruct

# List downloaded models
devon list

# Export for KITT
devon export --format kitt -o models.txt
```

## Commands

| Command | Description |
|---|---|
| `devon search` | Search for models with filters ([filter guide](https://kirizan.github.io/devon/guides/searching/)) |
| `devon download` | Download a model by URL or ID |
| `devon list` | List downloaded models |
| `devon info` | Show model details |
| `devon status` | Storage usage summary |
| `devon clean` | Remove old or unused models |
| `devon remove` | Delete a specific model |
| `devon export` | Export paths for KITT |
| `devon serve` | Start the REST API server |

### Search Filters

The `search` command supports these filters (combine freely, AND logic):

```bash
devon search "query"                          # text search
devon search --provider qwen                  # by author/org (-p)
devon search --params 30b                     # by parameter count (±20% tolerance)
devon search --size "<100gb"                  # by file size (<, <=, >, >=)
devon search --format gguf                    # by format (-f: gguf, safetensors, pytorch, onnx)
devon search --task text-generation           # by pipeline tag (-t)
devon search --license apache-2.0             # by license (-l)
devon search --limit 50                       # max results (default 20)
```

Filters also work inline: `devon search "qwen 30b gguf"` auto-extracts params and format.

See the [full filter guide](https://kirizan.github.io/devon/guides/searching/) for detailed examples and sample output.

## Documentation

| Section | Description |
|---|---|
| [Getting Started](https://kirizan.github.io/devon/getting-started/) | Installation and first model tutorial |
| [Guides](https://kirizan.github.io/devon/guides/) | Searching, downloading, managing, configuration |
| [Reference](https://kirizan.github.io/devon/reference/) | CLI reference, config schema, data models |
| [Concepts](https://kirizan.github.io/devon/concepts/) | Architecture, source plugins, storage design |

## Configuration

Config file at `~/.config/devon/config.yaml`. Only override what you need:

```yaml
storage:
  base_path: /mnt/data/models
  max_size_gb: 500
```

See the [full configuration guide](https://kirizan.github.io/devon/guides/configuration/) for all options.

## REST API

Install the API extras, then start the server:

```bash
poetry install --extras api
devon serve                       # http://127.0.0.1:8000
devon serve --host 0.0.0.0 --port 9000
```

### Endpoints

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

### Authentication

Set the `DEVON_API_KEY` environment variable to require bearer token auth on all `/api/v1/*` endpoints. When unset, requests are unauthenticated.

```bash
DEVON_API_KEY=secret devon serve
curl -H "Authorization: Bearer secret" http://localhost:8000/api/v1/models
```

### Quick Examples

```bash
# Health check
curl http://localhost:8000/health

# Search for models
curl "http://localhost:8000/api/v1/search?provider=qwen&limit=3"

# List local models
curl http://localhost:8000/api/v1/models

# Download a model
curl -X POST http://localhost:8000/api/v1/downloads \
  -H "Content-Type: application/json" \
  -d '{"model_id": "Qwen/Qwen2.5-1.5B"}'

# Storage status
curl http://localhost:8000/api/v1/status
```

## Docker

### Build and run

```bash
docker compose up -d
curl http://localhost:8000/health
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVON_PORT` | `8000` | Host port mapping |
| `DEVON_DATA_PATH` | `devon-data` (named volume) | Host path for model storage |
| `DEVON_API_KEY` | *(empty — no auth)* | Bearer token for API endpoints |
| `HF_TOKEN` | *(empty)* | HuggingFace token for gated models |

Mount your existing models directory:

```bash
DEVON_DATA_PATH=/mnt/models docker compose up -d
```

The container stores models at `/data/models/`, the index at `/data/index.json`, and config at `/data/config.yaml`. A single `-v /your/path:/data` covers everything.

**Note:** The default configuration runs a single uvicorn worker to avoid race conditions on the JSON index file.

## Related Projects

- [KITT](https://github.com/kirizan/kitt) — LLM inference testing suite ([docs](https://kirizan.github.io/kitt/))

## License

Apache 2.0
