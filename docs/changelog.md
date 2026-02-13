# Changelog

All notable changes to DEVON are documented in this file.

## 1.1.0

- **REST API** — FastAPI server exposed via `devon serve`
    - Endpoints: health, search, models (list/info/delete), downloads, storage (status/clean/export)
    - Optional bearer token authentication via `DEVON_API_KEY`
    - App factory with lifespan for shared Settings and ModelStorage
- **Docker support** — multi-stage Dockerfile and docker-compose.yml
    - Single `/data` volume mount for models, index, and config
    - Non-root `devon` user, built-in healthcheck
    - Configurable via `DEVON_PORT`, `DEVON_DATA_PATH`, `DEVON_API_KEY`, `HF_TOKEN`
- **`devon serve` command** — start the API server from the CLI
    - `--host`, `--port`, `--reload` options
    - Graceful error if API extras are not installed
- **Optional `api` extras** — `poetry install --extras api` adds FastAPI and Uvicorn without affecting CLI-only installs

## 1.0.0

- Initial release
- HuggingFace model search with filters (provider, params, size, format, task, license)
- Model download by URL or ID with resume support
- Local vault with JSON index and disk usage tracking
- KITT integration via `devon export --format kitt`
- YAML configuration with deep merge
- Source plugin architecture
