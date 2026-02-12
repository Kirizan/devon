# DEVON - Discovery Engine and Vault for Open Neural models

> *"DEVON manages the models. KITT tests them."*

CLI tool for discovering, downloading, and managing LLM models from HuggingFace and other sources.

[**Full Documentation**](https://kirizan.github.io/devon/) | [**CLI Reference**](https://kirizan.github.io/devon/reference/cli/)

## Features

- **Smart search** — filter by provider, size, parameters, format, task, license
- **Easy download** — by URL or model ID with automatic resume
- **Local vault** — organized storage with disk usage tracking
- **KITT integration** — export model paths for inference testing
- **Source plugins** — extensible architecture for model sources
- **YAML configuration** — deep-merged config with sensible defaults

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

## Related Projects

- [KITT](https://github.com/kirizan/kitt) — LLM inference testing suite ([docs](https://kirizan.github.io/kitt/))

## License

Apache 2.0
