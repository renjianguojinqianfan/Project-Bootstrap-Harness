# {project_name}

{project_description}

## Quick Start

```bash
pip install -e ".[dev]"
make verify
```

## Commands

| Command | Description |
|---------|-------------|
| `make verify` | lint + tests + coverage |
| `make test` | run tests |
| `make lint` | code style check |
| `make fix` | auto-fix style issues |

## Project Structure

```
{project_name}/
├── src/{package_name}/   # Main code
├── tests/                # Tests
├── tasks/                # Task breakdown
├── docs/                 # Documentation
├── AGENTS.md             # AI collaboration protocol
├── Makefile
└── pyproject.toml
```

## AI Collaboration

This project follows the PBH protocol. AI assistants should read `AGENTS.md` for project rules and working guidelines.

## License

MIT