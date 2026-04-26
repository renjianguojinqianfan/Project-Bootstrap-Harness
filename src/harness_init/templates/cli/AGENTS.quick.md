# AGENTS.md - {project_name}

> Keep this file to 50 lines or fewer.

## 1. Project Snapshot

**{project_name}** — {project_description}

## 2. Quick Start

1. `make verify`
2. Run the tests
3. Locate the entry point

## 3. Multi-Agent

Multiple agents may work here concurrently. Use independent git worktrees. Check `.harness/progress.json` before starting.

## 4. Working Guidelines

- State your plan before coding: what, why, and expected impact
- One task per session
- Run `make verify` after changes
- Check `docs/decisions/` when unsure about design choices
- Follow existing code style; do not over-engineer

## 5. Critical Rules

- Never commit code that fails `make verify`
- Maintain test coverage threshold
- Follow the project's existing code style
- One atomic task per session

## 6. File Mapping

| Location | Purpose |
|----------|---------|
| `src/` | Main code |
| `tests/` | Tests |
| `tasks/` | Task breakdown |
| `.harness/` | Project state |