# vibe-bt-03

Python project initialized with `uv`.

## Requirements

- Python 3.13.13
- uv

## Usage

```powershell
uv sync
uv run vibe-bt-03
```

## Database manage API

Database management helpers are exported from `vibe_bt_03.database.api`.

```python
from vibe_bt_03.database.api import (
    configure_database,
    create_all_tables,
    get_database_health,
)

configure_database("sqlite+pysqlite:///research.db")
create_all_tables()

health = get_database_health()
assert health.ok
```

## Codex local environment

Prepare this project for Codex or a fresh local worktree:

```powershell
.\.codex\local-environment\setup.ps1
```

On macOS:

```sh
sh .codex/local-environment/setup.macos.sh
```

Run validation:

```powershell
.\.codex\local-environment\verify.ps1
```

On macOS:

```sh
sh .codex/local-environment/verify.macos.sh
```

Clean all local generated environment artifacts:

```powershell
.\.codex\local-environment\clean.ps1
```

On macOS:

```sh
sh .codex/local-environment/clean.macos.sh
```
