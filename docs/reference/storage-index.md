# Storage Index

DEVON tracks all locally downloaded models in a JSON index file. This page
documents the index location, format, and the methods available for
interacting with it.

## File Location

```
~/.cache/devon/index.json
```

The index file sits as a sibling to the `models/` directory inside the
configured `storage.base_path` parent:

```
~/.cache/devon/
├── index.json       # Model index
└── models/          # Downloaded model files
    └── huggingface/
        └── Qwen/
            └── Qwen2.5-32B-Instruct/
```

## Key Format

Each entry is keyed by `{source}::{model_id}`:

```
huggingface::Qwen/Qwen2.5-32B-Instruct
```

## Entry Schema

```json
{
  "source": "huggingface",
  "model_id": "Qwen/Qwen2.5-32B-Instruct",
  "path": "/home/user/.cache/devon/models/huggingface/Qwen/Qwen2.5-32B-Instruct",
  "metadata": { },
  "files": ["model.safetensors", "config.json"],
  "downloaded_at": "2025-02-12T14:30:00.123456",
  "last_used": "2025-02-12T15:00:00.123456",
  "size_bytes": 67108864000
}
```

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Source plugin that provided the model |
| `model_id` | string | Full model identifier |
| `path` | string | Absolute path to the model directory on disk |
| `metadata` | object | Serialized `ModelMetadata` (see [Model Metadata](model-metadata.md)) |
| `files` | list[string] | Filenames stored in the model directory |
| `downloaded_at` | string | ISO 8601 timestamp of when the download completed |
| `last_used` | string | ISO 8601 timestamp updated each time the model is accessed |
| `size_bytes` | int | Total size in bytes, calculated at registration time |

## ModelStorage Methods

The `ModelStorage` class in `devon.storage.organizer` provides the
following methods for managing the index:

| Method | Description |
|--------|-------------|
| `register_model(metadata, path, files)` | Add a new entry to the index after download |
| `list_local_models()` | Return all entries in the index |
| `is_downloaded(source, model_id)` | Check whether a model key exists |
| `get_model_entry(source, model_id)` | Retrieve a single entry by key |
| `delete_model(source, model_id)` | Remove the entry and its files from disk |
| `get_total_size()` | Sum `size_bytes` across all entries |
| `mark_used(source, model_id)` | Update `last_used` to the current timestamp |
