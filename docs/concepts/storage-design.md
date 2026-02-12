# Storage Design

DEVON stores downloaded models on disk and tracks them with a JSON index.
This page explains the directory layout, index format, and the design
decisions behind them.

## Directory Structure

Models are organized under the configured `storage.base_path` (default
`~/.cache/devon/models/`) using the pattern:

```
models/{source}/{author}/{model}/
```

For example:

```
~/.cache/devon/
├── index.json
└── models/
    └── huggingface/
        ├── Qwen/
        │   └── Qwen2.5-32B-Instruct/
        └── meta-llama/
            └── Llama-3-70B-Instruct/
```

This layout mirrors the `author/model` convention used by HuggingFace and
keeps models from different sources cleanly separated.

## JSON Index

The index file lives at `{base_path}/../index.json` -- a sibling of the
`models/` directory. It is a single JSON object where each key is a model
identifier in the format:

```
{source}::{model_id}
```

For example: `huggingface::Qwen/Qwen2.5-32B-Instruct`.

See the [Storage Index reference](../reference/storage-index.md) for the
full entry schema.

## Why a Flat JSON File

- **Simplicity.** No external database to install, configure, or migrate.
  The index is a single portable file.
- **Transparency.** Users can inspect and even hand-edit the index with any
  text editor or JSON tool.
- **Portability.** Copying the `~/.cache/devon/` directory to another
  machine is enough to move the entire vault.

The trade-off is that concurrent writes from multiple processes are not
safe without coordination, but DEVON is a single-user CLI tool where this
is not a practical concern.

## Atomic Operations

The `ModelStorage` class uses a **read-modify-write** pattern with file
locking:

1. Read the entire index into memory.
2. Apply the change (add, update, or remove an entry).
3. Write the full index back to disk.

This keeps the index consistent even if the process is interrupted, because
the write replaces the file atomically.

## Size Tracking

Each index entry records a `size_bytes` value that is calculated at
registration time by summing the sizes of all downloaded files. The
`get_total_size()` method sums across every entry to report overall vault
usage, which powers the `devon status` command.

## Last-Used Tracking

Every index entry includes a `last_used` timestamp that is updated each
time the model is accessed (for example, by `devon info` or
`devon export`). The `devon clean --unused --days N` command uses this
timestamp to identify models that have not been touched in `N` days,
making it easy to reclaim disk space without manually deciding which models
to keep.
