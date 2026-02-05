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
pip install devon-ai
```

Or from source:

```bash
git clone https://github.com/nick/devon
cd devon
poetry install
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

Edit `~/.config/devon/config.yaml` to customize settings.

## License

Apache 2.0 - see [LICENSE](LICENSE) file.

## Related Projects

- [KITT](https://github.com/nick/kitt) - LLM inference testing framework
