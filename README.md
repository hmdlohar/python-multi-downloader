# hget

A high-performance, parallel downloader CLI and library.

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
hget https://example.com/file1.zip https://example.com/file2.zip -d ./downloads
hget https://example.com/model.safetensors:/content/models/vae
```

### Library

```python
import hget

hget.download([
    "https://example.com/file1.zip",
    ["https://example.com/file2.zip", "./custom_dir"],
    {"url": "https://example.com/file3.zip", "dir": "./another_dir"}
])
```
