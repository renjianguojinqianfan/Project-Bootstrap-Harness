# docs/context.md - {project_name}

## 1. Project Metadata

```yaml
name: {project_name}
version: 0.1.0
type: {project_type}
tech_stack:
  language: Python 3.11
  cli_framework: typer
  testing: pytest + pytest-cov
  linting: ruff
```

## 2. Architecture Overview

```
{project_name}/
├── src/{package_name}/          # Application source code
│   └── cli.py                   # CLI entry point
├── tests/                       # Unit and integration tests
├── .harness/                    # Harness runtime artifacts
│   ├── templates/               # Agent plan templates
│   └── progress.json            # Source of truth for session state
├── docs/
│   ├── context.md               # Deep context (this file)
│   └── decisions/               # Architecture decision records (ADR)
└── AGENTS.md                    # Quick agent map
```

The project follows a layered design. The CLI layer parses arguments and delegates to the core logic.

## 3. Key Conventions

### 3.1 Code Organization
- All tests mirror the `src/` structure under `tests/`
- Configuration files live in `configs/`

### 3.2 Naming Conventions
- Module names: `snake_case`
- Class names: `PascalCase`
- Function and variable names: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### 3.3 Commit Format
```
<type>: <subject>

<body>

types: feat, fix, docs, test, refactor, chore
```

### 3.4 Plan File Format

Plans are JSON files following the schema at `.harness/templates/plan_template.json`.

## 4. Development Workflow

1. Read `AGENTS.md` for the quick project map.
2. Consult this file (`docs/context.md`) for architecture details and conventions.
3. Run `make verify` before every commit. It must pass.

## 5. Common Tasks

### 5.1 Adding a New Feature

```bash
# 1. Write or update code in src/{package_name}/
# 2. Add tests in tests/
# 3. Verify before committing
make verify
```

### 5.2 Fixing a Bug

```bash
# 1. Reproduce the bug with a test
# 2. Fix the code in src/{package_name}/
# 3. Run tests to confirm the fix
make test

# 4. Verify before committing
make verify
```

## 6. Important Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent quick-reference map (50-100 lines) |
| `docs/context.md` | Deep project context (this file) |
| `docs/decisions/` | Architecture decision records (ADR) |
| `src/{package_name}/` | Application source code |
| `.harness/progress.json` | Session state source of truth |
| `tests/` | Test suites |
| `Makefile` | `make verify`, `make test`, `make lint` |
