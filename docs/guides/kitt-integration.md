# KITT Integration

DEVON and KITT are companion tools. DEVON manages the models. KITT tests
them. Together they form a workflow for downloading models and running
inference benchmarks.

## Overview

[KITT](https://kirizan.github.io/kitt/) is an inference engine testing
suite that measures model performance across different serving backends.
DEVON's export command produces output in formats that KITT can consume
directly.

## Exporting for KITT

Generate a text file listing local model paths, one per line:

```bash
devon export --format kitt -o models.txt
```

The resulting `models.txt` file contains absolute paths to each
downloaded model directory, ready for KITT to read.

## Exporting as JSON

For programmatic consumption, export the full model index as JSON:

```bash
devon export --format json -o models.json
```

The JSON output includes model IDs, sources, file sizes, download dates,
and local paths.

## Using the Export with KITT

Pass the exported file to KITT's `--model-list` flag along with your
desired engine and test suite:

```bash
kitt run --model-list models.txt --engine vllm --suite standard
```

KITT reads each path from the file and runs the specified test suite
against every model in sequence.

## Full Workflow Example

A typical workflow from discovery to testing:

```bash
# 1. Search for candidate models
devon search "qwen instruct" --params 7b --format gguf

# 2. Download the ones you want
devon download Qwen/Qwen2.5-7B-Instruct

# 3. Export paths for KITT
devon export --format kitt -o models.txt

# 4. Run inference tests
kitt run --model-list models.txt --engine vllm --suite standard
```

This pattern scales to any number of models. Download as many as you
need, export once, and KITT tests them all.

## Further Reading

- [KITT documentation](https://kirizan.github.io/kitt/)
- [Searching for models](searching.md)
- [Downloading models](downloading.md)
- [Managing local models](managing.md)
