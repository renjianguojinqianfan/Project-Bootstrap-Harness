# harness-init

A CLI tool to scaffold complete, ready-to-run Python projects that follow **Harness Engineering** conventions. Every generated project ships with a working harness core, agent stubs, test suites, and a validation pipeline — it passes `make verify` immediately after creation.

## Features

- **One-command scaffolding**: Package structure, CLI, tests, harness runtime, and Git initialization, all done automatically
- **Generate-and-verify**: Every project includes `make verify` (ruff + pytest with coverage >= 85%)
- **Agent-friendly**: Generated projects come with `AGENTS.md`, `docs/context.md`, and `opencode.yaml`, so external agents (e.g., OpenCode) can understand the structure and workflow right away
- **Safe and robust**: Project name validation, path traversal protection, automatic rollback on Git failure, and atomic state writes

## Installation

```bash
pip install harness-init
```

Or install from source:

```bash
git clone https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness.git
cd Project-Bootstrap-Harness
pip install -e ".[dev]"
```

## Quick Start

```bash
# Create a new project
harness-init my-project

# Enter and verify
cd my-project
pip install -e ".[dev]"
make verify
```

After execution, `my-project/` will be created with:

- Full Python package structure (`src/my_project/`)
- Harness core engine: `runner.py` (task execution), `evaluator.py` (result evaluation), `state.py` (state persistence), `workflow.py` (workflow definition)
- Agent stubs: `planner.py`, `generator.py`, `evaluator.py`
- Runtime directories: `.harness/plans/`, `.harness/eval_feedback/`, `.harness/state/`
- Multi-command CLI: `run`, `evaluate`, `status`
- `configs/` (dev/test/prod), `docs/context.md`, `AGENTS.md`, `opencode.yaml`
- `pyproject.toml`, `Makefile`, `.gitignore`
- Auto-initialized Git repository with an initial commit

## CLI Options

```bash
# Show version
harness-init --version

# Force overwrite an existing directory (old directory is backed up as my-project.bak-YYYYMMDDhhmmss)
# Warning: --force moves the entire existing directory and replaces it with templates; not suitable for incremental migration of existing repos
harness-init my-project --force

# Skip Git initialization
harness-init my-project --no-git
```

## Project Name Rules

To produce a valid Python package, the project name must:
- Start with a letter or underscore
- Contain only letters, digits, hyphens (`-`), and underscores (`_`)
- Not be empty, contain spaces, path separators, or `..`

**Valid examples**: `my-project`, `my_project`, `harness_v2`  
**Invalid examples**: `123project` (starts with a digit), `my project` (contains a space), `foo/../bar` (path traversal)

## Development Commands (for harness-init itself)

| Command | Description |
|---------|-------------|
| `make verify` | Run ruff + pytest (coverage >= 85%) |
| `make test` | Run pytest |
| `make lint` | Run ruff |
| `make install` | `pip install -e .` |

## Why Generated Projects Are Agent-Friendly

Generated projects are designed for external agents:

- **`AGENTS.md`**: Quick map so agents can understand the project role, workflow, and key constraints at a glance
- **`docs/context.md`**: Deep context with architecture details, naming conventions, and common task examples
- **`opencode.yaml`**: Explicit seven-stage workflow configuration
- **`make verify`**: Unified validation entry point; agents get immediate quality feedback after any change
- **`.harness/` runtime directories**: Plans, eval feedback, and state are separated to support multi-turn conversation breakpoints

## Architecture

- `src/harness_init/cli.py` — CLI entry point (argument parsing)
- `src/harness_init/core.py` — Core project generation logic (validation, copying, rendering, Git initialization, rollback)
- `src/harness_init/templates/` — Template files for the generated project

## License

MIT
