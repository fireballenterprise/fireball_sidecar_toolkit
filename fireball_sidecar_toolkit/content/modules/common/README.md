# Common Utilities Module
Shared utilities and helper functions used across all modules in the ai_vault repository.

## Overview
This module provides common functionality that is used by other modules throughout the repository, including configuration parsing and utility functions.

## Modules
### Screenshot utilities (moved out)
The screenshot workflow lives in `modules/toolkit/screenshots/` (`configure.py`, `view.py`, `clean.py`).

### `utils.py`
Common utility functions for console output, error handling, and shared operations.

**Functions:**
- `success(message)` - Print success messages with ✅ emoji
- `error(message)` - Print error messages with ❌ emoji  
- `warning(message)` - Print warning messages with ⚠️ emoji
- `info(message)` - Print info messages with ℹ️ emoji

## Dependencies
This module depends on:
- `common.properties` - For reading configuration from `properties.yml`
- Standard library: `pathlib`, `shutil`
- Internal CLI helper: `modules/toolkit/common/cli.py` (TUI-safe prompt/confirm/option handling)

## Configuration
Uses `properties.yml` at repository root:

```yaml
screenshots:
  location: "${repo_local}/screenshots"
  latest_file: "latest.png"
  preserve_files:
    - "latest.png"
  cleanup_patterns:
    - "*.png"
    - "*.jpg"
    - "*.jpeg"
```

## Architecture
The common module follows these principles:
- **Shared utilities only** - Functions used by multiple modules
- **No business logic** - Pure utility functions
- **Minimal dependencies** - Only depends on standard library and config
- **Clear error messages** - User-friendly output with emojis
- **Type hints** - Full type annotations for all functions

## Integration
Every other module imports from `common/`:

```python
from modules.common import cli
from modules.toolkit.common.properties import get_repo_local, get_screenshots_location
from modules.toolkit.common.utils import success, error, warning, info
from modules.toolkit.common.route_utils import build_env, find_repo_root
```
