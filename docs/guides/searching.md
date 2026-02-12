# Searching for Models

DEVON searches HuggingFace for models matching your query and filters.
Results are displayed in a Rich table showing the model ID, size,
download count, and format.

## Basic Search

Pass a keyword or phrase to find matching models:

```bash
devon search "llama 3"
devon search "code generation"
```

## Filtering Results

Filters narrow results before display. Combine any number in one command.

### By Provider

```bash
devon search --provider qwen
devon search --provider meta-llama
```

### By Parameter Count

```bash
devon search --params 30b
devon search --params 70b
```

### By File Size

```bash
devon search --size "<100gb"
devon search --size ">50gb"
```

### By Format

```bash
devon search --format gguf
devon search --format safetensors
```

### By Task

```bash
devon search --task text-generation
```

### By License

```bash
devon search --license apache-2.0
devon search --license mit
```

## Limiting Results

By default DEVON returns 20 results. Use `--limit` to change this:

```bash
devon search "llama" --limit 50
devon search "code" --limit 5
```

You can also set a permanent default in your
[configuration file](configuration.md).

## Source Selection

DEVON currently supports HuggingFace as a model source. The `--source`
flag selects which source to query (defaults to `huggingface`):

```bash
devon search "llama" --source huggingface
```

## Combining Filters

Filters stack with AND logic. Only models matching every filter appear:

```bash
devon search --provider qwen --params 30b --format gguf
devon search "instruct" --provider meta-llama --size "<50gb" --format safetensors
devon search --task text-generation --license apache-2.0 --limit 50
```

## Search Results Display

Results appear in a Rich table with columns for Model ID, Size,
Downloads, and Format. Models are sorted by download count (most popular
first) unless you change `search.sort_by` in your
[configuration file](configuration.md).
