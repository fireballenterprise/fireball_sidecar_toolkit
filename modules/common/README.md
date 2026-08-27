# Common Utilities Module

Shared utilities and helper functions used across all modules in the template_python repository.

## Overview

This module provides common functionality that is used by other modules throughout the repository, including configuration parsing and utility functions.

## Files

- `utils.py` — console output helpers: `success()`, `error()`, `warning()`, `info()` (✅/❌/⚠️/ℹ️
  prefixed)
- `properties.py` — reads `properties.yml`: `get_repo_root()`, `get_repo_local()`,
  `get_repo_remote()`, `get_template_local()`, `get_template_remote()`
- `cli.py` — Click-like CLI compatibility helpers backed by `argparse` (`echo`, `secho`, `prompt`,
  `confirm`, `is_tty`, `Choice`, `command`/`option` decorators) — TUI-safe, no external dependency
- `README.md` — this file

## Dependencies

This module depends on:
- Standard library: `pathlib`, `argparse`, `subprocess`
- `pyyaml` — for reading `properties.yml`

## Architecture

The common module follows these principles:
- **Shared utilities only** - Functions used by multiple modules
- **No business logic** - Pure utility functions
- **Minimal dependencies** - Only depends on standard library and config
- **Clear error messages** - User-friendly output with emojis
- **Type hints** - Full type annotations for all functions

## Integration

Other modules import from common:

```python
from modules.common.utils import success, error, warning, info
```
