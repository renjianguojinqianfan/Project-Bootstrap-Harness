# Project-Bootstrap-Harness (PBH)

> A **project protocol template** designed for AI-assisted development.
>
> We don't tell AI how to think. We give it the best environment to work in.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/pypi-harness--init-green.svg)](https://pypi.org/project/harness-init/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why This Exists

When coding with Claude Code, Cursor, or OpenCode, you've likely hit these friction points:

- **Repeating rules in every new session**: "Remember to run tests", "Don't touch unrelated files", "Plan before coding"
- **AI writes code but never verifies it**: Small errors snowball, and humans end up cleaning the mess
- **Context lost when switching tools**: What Claude Code understood, Cursor doesn't know

**The problem isn't that AI isn't smart enough. It's that the project itself lacks a default collaboration protocol.**

PBH plants that protocol, quality gates, and state tracking into your project the moment you run `harness-init my-project`. From then on, any AI tool opening this project knows within 30 seconds: how to run tests, where the quality baseline sits, and what phase the project is in.

---

## What It Is (and Isn't)

### ✅ PBH Is

- **A universal collaboration protocol**: `AGENTS.md` serves as the common entry point for all AI tools, defining critical rules, working guidelines, and project structure
- **Quality gate infrastructure**: `make verify` works out of the box — lint, tests, and coverage in one command
- **An observable Agent behavior benchmark**: The same `AGENTS.md` lets you observe how different AI tools follow rules and perform
- **A Spec Coding container**: Provides the `tasks/` directory for you to break down work; content is entirely up to you
- **A "protocol seeder"**: Seeds rules on project creation so constraints travel with the project, not the developer.
- **An ecosystem protocol standard**: See `docs/spec/PBH-SPEC.md` — defines universal conventions for AI project collaboration, implementable in any language.
### ❌ PBH Is NOT

- **Not an Agent framework**: Does not define AI roles or implement multi-agent orchestration
- **Not a code generator**: Does not generate business logic from natural language
- **Not a Spec Coding workflow tool**: Does not generate PRDs, SPECs, or constraints.md — only provides directories for them

---

## Quick Start

```bash
pip install harness-init

# Full mode (default CLI template)
harness-init my-awesome-project

# Choose project type
harness-init my-library --template=lib --yes
harness-init my-api --template=web --yes
harness-init my-analysis --template=notebook --yes

# Choose IDE config (default: all)
harness-init my-project --ide=cursor --yes    # Cursor only
harness-init my-project --ide=none --yes      # No IDE configs

# Quick mode (minimal, 5-minute onboarding)
harness-init my-project --quick --yes
```

Enter the project and verify:

```bash
cd my-awesome-project
pip install -e ".[dev]"
make verify        # Should output ✅ Verification passed
```

### 💡 If make is not available

Windows users may not have make installed. If you see 'make' is not recognized, you can:

**Install make:**

- Windows: Install [GnuWin32 Make](https://gnuwin32.sourceforge.net/packages/make.htm) or run `winget install GnuWin32.Make`
- macOS: `xcode-select --install`
- Linux: `sudo apt install make` or equivalent

**Or run equivalent commands directly:**

```bash
# Code style check
ruff check src/ tests/

# Run tests + coverage
pytest tests/ -v --cov=src --cov-fail-under=85
```

Invite AI to the party:

> "Please read AGENTS.md to understand the project rules, then help me get started."

---

## Generated Project Structure

```text
my-awesome-project/
├── .harness/
│   ├── progress.json         # Project phase state (AI's first stop in new sessions)
│   └── workspaces/           # Multi-agent workspace isolation (reserved)
├── docs/
│   ├── context.md            # Deep context (architecture, conventions, tasks)
│   └── decisions/            # Architecture Decision Records (ADR)
├── src/my_awesome_project/
│   └── cli.py                # CLI entry point (replaceable as needed)
├── tests/                    # Test suite (mirrors src/ structure)
├── tasks/                    # Task breakdown (Spec Coding container)
├── AGENTS.md                 # AI collaboration protocol (common entry for all tools)
├── Makefile                  # verify / test / lint / fix
├── pyproject.toml            # Dependencies + tool configs
└── README.md
```

---

## AGENTS.md: The Common Entry Point for All AI Tools

The core file PBH generates is `AGENTS.md`, structured as an "airport navigation" guide that helps AI understand the project in 30 seconds:

- **Quick Start**: First steps, how to run verification
- **Multi-Agent Notice**: Supports multiple AIs working concurrently; recommends independent git worktrees
- **Working Guidelines**: Flexible guidance — state your plan before coding, focus on atomic tasks, verify after completion
- **Critical Rules**: Non-negotiable quality baseline
- **Security Guidelines**: No hardcoded secrets, command review, etc.
- **File Mapping**: At-a-glance directory reference

PBH does not define AI roles or enforce specific workflows. It provides a universal protocol that all AI tools can understand.

---

## Mode Comparison

| Feature | Full Mode | Quick Mode (--quick) |
|---------|-----------|---------------------|
| AGENTS.md | Full (≤80 lines) | Minimal (≤50 lines) |
| CI/CD | ✅ GitHub Actions | ❌ |
| Documentation | ✅ context.md / ADR | ❌ |
| Dependencies | typer + pytest + ruff, etc. | typer only |

Both modes include: `AGENTS.md`, `Makefile` (verify/test/lint), `tests/` directory, `tasks/` directory, `progress.json`.

---

## Use Cases

**Good for:**

- Individual developers using multiple AI tools who want unified project-level collaboration rules
- Small teams standardizing AI collaboration practices
- AI-assisted development workflows that need verifiability and handoff clarity
- Observing and comparing how different AI tools behave in the same project

**Not ideal for:**

- Multi-agent autonomous orchestration → Use a dedicated Agent framework
- Deterministic unattended pipelines → PBH does not lock down Agent behavior
- Non-Python projects → Current templates only support Python 3.11+

---

## Roadmap

- **v1.1.0**: Remove out-of-scope features, rewrite AGENTS.md as "airport navigation", establish clear boundaries
- **v1.5.0** ✅: `--ide` parameter (on-demand IDE adapter files), `--template` parameter (cli/lib/web/notebook project types), `.harness/known_pitfalls.md`
- **v2.0.0**: Cross-language support based on PBH-SPEC, ecosystem interfaces (Harness-Lint), official universal protocol announcement

This project is maintained by an individual in spare time. The roadmap adjusts dynamically based on priorities.

---

## Ecosystem

| Tool | Description |
|------|-------------|
| [Harness-Lint](https://github.com/renjianguojinqianfan/harness-lint) | Protocol verifier for PBH ecosystem, covering 7 AI code defect rules with attribution-anchored reports |
| [PBH-SPEC](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/blob/master/docs/spec/PBH-SPEC.md) | AI project collaboration protocol standard draft (EN/ZH), community contributions welcome |

## Acknowledgments

- [Typer](https://typer.tiangolo.com/) — Elegant CLI framework
- [Ruff](https://docs.astral.sh/ruff/) — Blazingly fast Python linter
- [Pytest](https://docs.pytest.org/) — Reliable testing framework

Inspiration: Anthropic's Agentic Workflow and Context Engineering practices, OpenAI's Harness Engineering philosophy and Symphony project

## License

MIT © renjianguojinqianfan