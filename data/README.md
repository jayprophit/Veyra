# Local Data

This directory is reserved for local-only runtime state.

- `veyra_local.db` is the default SQLite database when the API runs directly on the host.
- `logs/` stores local launcher logs.
- `runtime/` stores transient PID state for the local launcher.

Database files, logs, and runtime state are ignored by git.
