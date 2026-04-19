# docs/context.md - {project_name}

## 1. Project Metadata

```yaml
name: {project_name}
version: 0.1.0
type: cli
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
│   ├── agents/                  # Planner, Generator, Evaluator agents
│   ├── harness/                 # Core workflow runner and evaluator
│   └── cli.py                   # CLI entry point
├── tests/                       # Unit and integration tests
├── .harness/                    # Harness runtime artifacts
│   ├── plans/                   # JSON execution plans
│   ├── eval_feedback/           # Evaluation reports
│   └── progress.json            # Source of truth for session state
├── docs/
│   ├── context.md               # Deep context (this file)
│   └── decisions/               # Architecture decision records (ADR)
└── AGENTS.md                    # Quick agent map
```

The project follows a layered design. The CLI layer parses arguments and delegates to the harness core. The harness core loads plans, orchestrates agents, and evaluates results. Agents live under `src/{package_name}/agents/` and implement the three core roles.

## 3. Key Conventions

### 3.1 Code Organization
- All agent implementations go in `src/{package_name}/agents/`
- All harness core logic goes in `src/{package_name}/harness/`
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
3. Check `.harness/plans/` for pending execution plans.
4. Follow the seven-stage workflow: Feedback → Triage → Clarify → Plan → Execute → Evaluate → Done.
5. Run `make verify` before every commit. It must pass.

## 5. Common Tasks

### 5.1 Adding a New Feature

```bash
# 1. Create or pick a plan
python -m {package_name} run .harness/plans/feature_001.json

# 2. Review evaluation feedback
ls .harness/eval_feedback/

# 3. Verify before committing
make verify
```

### 5.2 Fixing a Bug

```bash
# 1. Run the bugfix plan
python -m {package_name} run .harness/plans/bugfix_001.json

# 2. Evaluate a specific result path if needed
python -m {package_name} evaluate .harness/eval_feedback/latest.json

# 3. Check project status
python -m {package_name} status

# 4. Verify before committing
make verify
```

## 6. Important Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent quick-reference map (50-100 lines) |
| `docs/context.md` | Deep project context (this file) |
| `docs/decisions/` | Architecture decision records (ADR) |
| `src/{package_name}/agents/` | Agent implementations |
| `src/{package_name}/harness/runner.py` | Plan execution engine |
| `src/{package_name}/harness/evaluator.py` | Result evaluation engine |
| `.harness/plans/` | JSON execution plans |
| `.harness/progress.json` | Session state source of truth |
| `.harness/eval_feedback/` | Evaluation output |
| `tests/` | Test suites |
| `Makefile` | `make verify`, `make test`, `make lint` |
