# AGENTS.md - {project_name}

> **Principle**: Keep this file to 50 lines. Deep context lives in code comments.

## 1. Project Snapshot

**{project_name}** is a quick-start project. {project_description}

**Maintainer**: {author_name}  
**Type**: quick-start

## 2. Session Protocol

**One session = One atomic task**

1. **Verify Baseline**: Run `make verify` → must pass before any edit
2. **Select Task**: Pick ONE item from open issues / plans
3. **Implement**: Generate code → auto-trigger `make verify`
4. **Commit**: Write descriptive commit

## 3. Three-Role Workflow

Every session MUST declare its role before acting.

- **Planner**: Create plan, define acceptance criteria
- **Generator**: Implement step-by-step, run `make verify` per unit
- **Evaluator**: Review against plan, verify acceptance criteria, loop back if issues found

## 4. File Mapping

| Type | Location | Description |
|------|----------|-------------|
| Source | `src/{package_name}/` | Main application code |
| Tests | `tests/` | Mirror `src/` structure |
| Entry | `src/{package_name}/cli.py` | CLI entry point |

## 5. Commands

- `make verify`: Lint (`ruff`) + tests (`pytest`), coverage >= 85%
- `make fix`: Auto-fix linting; MUST re-run `make verify` after
