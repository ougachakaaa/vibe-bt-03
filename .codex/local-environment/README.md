# Codex local environment

Use these scripts to prepare a stable local Codex workspace for this project.

## Setup

Windows:

```powershell
.\.codex\local-environment\setup.ps1
```

Linux/macOS:

```sh
sh .codex/local-environment/setup.sh
```

The setup script:

- reads the Python version from `.python-version`
- keeps uv-managed Python downloads in `.uv-python`
- keeps uv cache in `.uv-cache`
- runs `uv python install`
- runs `uv sync --all-groups --frozen`

If you intentionally changed dependencies and need to update `uv.lock`, use:

```powershell
.\.codex\local-environment\setup.ps1 -AllowLockUpdate
```

or:

```sh
CODEX_UV_ALLOW_LOCK_UPDATE=1 sh .codex/local-environment/setup.sh
```

## Verify

Windows:

```powershell
.\.codex\local-environment\verify.ps1
```

Linux/macOS:

```sh
sh .codex/local-environment/verify.sh
```

The verify script runs bytecode compilation and the test suite.
