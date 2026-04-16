# {project_name}

{project_description}

## Features

- Complete Python project structure, ready to develop immediately after generation
- Built-in `make verify` pipeline (lint + tests, coverage >= 85%)
- Agent-friendly: includes `AGENTS.md`, `docs/context.md`, and `opencode.yaml`
- Supports external agents (e.g., OpenCode) collaborating in Planner / Generator / Evaluator roles

## Quick Start

```bash
pip install -e ".[dev]"
make verify
```

## Installation

```bash
# Install from source
pip install -e ".[dev]"
```

## CLI Usage

After installation, use the `{project_name}` CLI:

```bash
# Run an execution plan
{project_name} run [plan_path]

# Evaluate a result
{project_name} evaluate [result_path]

# Show project status
{project_name} status
```

## Development Commands

| Command | Description |
|---------|-------------|
| `make verify` | Run lint + tests with coverage gate (>= 85%) |
| `make test` | Run pytest |
| `make lint` | Run ruff check |
| `make install` | Install the package in editable mode |

## Directory Structure

```
{project_name}/
├── src/{package_name}/          # Main source code
│   ├── cli.py                   # CLI entry point
│   └── ...
├── tests/                       # Tests (mirror src/ structure)
├── .harness/                    # Runtime artifacts
│   ├── plans/                   # JSON execution plans
│   ├── eval_feedback/           # Evaluation feedback
│   └── progress.json            # Source of truth for session state
├── configs/                     # Configuration files
├── docs/
│   ├── context.md               # Architecture and conventions
│   └── decisions/               # Architecture decision records (ADR)
├── AGENTS.md                    # Quick agent reference
├── opencode.yaml                # Agent workflow configuration
├── Makefile
├── pyproject.toml
└── README.md                    # Chinese README
```

## Architecture

This project follows a layered design:

- **CLI layer** (`cli.py`): Parses arguments and delegates to core logic
- **Core layer** (`src/{package_name}/`): Business implementation
- **Test layer** (`tests/`): Unit and integration tests

For detailed architecture conventions and common tasks, see `docs/context.md`.

## License

MIT
