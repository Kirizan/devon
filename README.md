# DEVON - Discovery Engine and Vault for Open Neural models

> *"DEVON manages the models. KITT tests them."*

DEVON is a command-line tool for discovering, downloading, and managing LLM models from HuggingFace and other sources.

## Features

- **Smart Search**: Filter by provider, size, parameters, format
- **Easy Download**: URL or model ID, with resume support
- **Local Vault**: Organized storage with disk usage tracking
- **KITT Integration**: Export model paths for testing
- **Fast**: Built with Python + HuggingFace Hub

## Installation

```bash
git clone https://github.com/nick/devon
cd devon
poetry install
```

## Activating the Environment

DEVON uses Poetry to manage its virtual environment. After running `poetry install`, you need to activate the environment before using the `devon` command directly.

### Option 1: Activate the virtual environment

**Bash / Zsh:**

```bash
eval $(poetry env activate)
```

**Fish:**

```fish
eval (poetry env activate)
```

`poetry env activate` detects your shell and prints the correct activation command. Once activated, you can run devon commands directly:

```bash
devon --version
devon search "llama"
```

To deactivate the environment when you're done:

```bash
deactivate
```

### Option 2: Use `poetry run`

Works in any shell — no activation needed:

```bash
poetry run devon --version
poetry run devon search "llama"
```

## Quick Start

```bash
# Search for models
devon search --provider qwen --params 30b --size "<100gb"

# Download by URL
devon download https://huggingface.co/Qwen/Qwen2.5-32B-Instruct

# List downloaded models
devon list

# Export for KITT
devon export --format kitt -o models.txt
```

## Usage

### Search

```bash
# Basic search
devon search "llama 3"

# Filtered search
devon search --provider qwen --params 30b --format gguf

# Advanced filters
devon search --provider meta-llama --params 70b --size "<150gb" --license apache-2.0
```

### Download

```bash
# By URL (auto-detects source)
devon download https://huggingface.co/Qwen/Qwen2.5-32B-Instruct

# By model ID
devon download Qwen/Qwen2.5-32B-Instruct --source huggingface

# Force re-download
devon download <model> --force
```

### Manage

```bash
# List local models
devon list

# Show details
devon info Qwen/Qwen2.5-32B-Instruct

# Check status
devon status

# Clean up
devon clean --unused --days 30
```

### KITT Integration

```bash
# Export models for KITT
devon export --format kitt -o models.txt

# Use with KITT
kitt run --model-list models.txt --engine vllm --suite standard
```

## Storage

Models are stored in `~/.cache/devon/models/` organized by source and model ID:

```
~/.cache/devon/
├── models/
│   └── huggingface/
│       ├── Qwen/Qwen2.5-32B-Instruct/
│       └── meta-llama/Llama-3.3-70B-Instruct/
└── index.json
```

## Configuration

DEVON loads its configuration from `~/.config/devon/config.yaml`. If the file doesn't exist, built-in defaults are used. You only need to specify the values you want to override.

### Creating the Config File

```bash
mkdir -p ~/.config/devon
$EDITOR ~/.config/devon/config.yaml
```

### Full Configuration Reference

```yaml
# ~/.config/devon/config.yaml

# Storage settings
storage:
  # Where models are downloaded to
  # Default: ~/.cache/devon/models
  base_path: ~/.cache/devon/models

  # Maximum total storage size (null = unlimited)
  # When set, devon will warn before exceeding this limit
  max_size_gb: null

# Download behavior
download:
  # Resume interrupted downloads automatically
  resume: true

  # Verify file checksums after download
  verify_checksums: true

# Model source configuration
sources:
  # Default source when --source is not specified
  default: huggingface

  # List of enabled sources
  enabled:
    - huggingface

# Search defaults
search:
  # Max results returned by default (override with --limit)
  default_limit: 20

  # Sort order for search results
  # Options: downloads, likes, last_modified
  sort_by: downloads

# Display options
display:
  # Enable colored terminal output
  color: true
```

### Configuration Examples

**Use a different storage directory** (e.g., a larger drive):

```yaml
storage:
  base_path: /mnt/data/models
```

**Cap total storage at 500GB**:

```yaml
storage:
  max_size_gb: 500
```

**Show more search results by default**:

```yaml
search:
  default_limit: 50
```

**Disable colored output** (useful for piping/scripting):

```yaml
display:
  color: false
```

**Multiple overrides at once**:

```yaml
storage:
  base_path: /data/llm-models
  max_size_gb: 1000

search:
  default_limit: 30
  sort_by: likes

download:
  verify_checksums: false
```

### How Configuration Merging Works

DEVON deep-merges your config file with the built-in defaults. You only need to include the keys you want to change. For example, this minimal config:

```yaml
storage:
  base_path: /mnt/data/models
```

results in all other settings (download, sources, search, display) keeping their default values.

## License

Apache 2.0 - see [LICENSE](LICENSE) file.

## Related Projects

- [KITT](https://github.com/nick/kitt) - LLM inference testing framework
