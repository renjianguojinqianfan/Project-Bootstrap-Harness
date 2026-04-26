# AGENTS.md - {project_name}

> Keep this file to 80 lines or fewer. For deeper context, see `docs/context.md`.

## 1. Project Snapshot

**{project_name}** — {project_description}

**Maintainer**: {author_name}
**Type**: {project_type}

## 2. Quick Start (30 seconds)

1. Run `make verify` — confirm your environment is working
2. Run the test command — ensure existing tests pass
3. Locate the entry point — understand how the program runs

## 3. Multi-Agent Notice

- Use independent git worktrees when multiple agents are active
- Check `.harness/progress.json` before starting work

## 4. Working Guidelines

- Read `.harness/progress.json` before starting
- Run `make verify` — baseline must be clean
- State your plan before modifying code (what, why, affected parts)
- One session = one atomic task
- Verify against acceptance criteria, run `make verify` before finishing
- Check `docs/decisions/` and `docs/context.md` when unsure
- All public APIs need type hints and docstrings
- Follow existing code style; no abstractions for single-use cases

## 5. Critical Rules

- **Never commit code that fails `make verify`**
- One session = one atomic task
- **Auto-fix circuit breaker**: Max 2 attempts per error, then step back
- **Self-evaluation ban**: Only `make verify` output is ground truth
- Never hardcode secrets; use env vars or `.env`
- Review all shell commands before execution
- Function ≤ 30 lines, file ≤ 200 lines
- Use atomic write-then-rename for persistent files

## 8. File Mapping

| Location | Purpose |
|----------|---------|
| `src/` | Main application code |
| `tests/` | Tests (mirrors `src/` structure) |
| `docs/` | Documentation and architecture decisions |
| `tasks/` | Task breakdown (Spec Coding container) |
| `.harness/` | Project phase tracking and workspace isolation |

## 9. Commands

| Command | What it does |
|---------|--------------|
| `make verify` | Full quality check (lint + tests + coverage). Must pass before commit |
| `make test` | Run tests only |
| `make lint` | Run code style checks only |
| `make fix` | Auto-fix style issues where possible |