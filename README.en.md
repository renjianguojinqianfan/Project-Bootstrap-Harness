# 🚀 harness-init

[![PyPI version](https://badge.fury.io/py/harness-init.svg)](https://badge.fury.io/py/harness-init)
[![Python Version](https://img.shields.io/pypi/pyversions/harness-init.svg)](https://pypi.org/project/harness-init/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **A Python project scaffold for AI Agents.**
> Not just another code generator, but a **"collaboration contract"** that any AI tool can read and follow.

---

## 🤔 Why do you need this tool?

When coding with Claude Code, Codex, or Cursor, have you ever run into these situations:

- AI writes code but never runs tests, letting small issues snowball?
- After starting a new session, the AI completely forgets previous decisions, forcing you to repeatedly "feed" it context?
- Everyone on the team commands AI differently, leading to chaotic code styles?

**The problem isn't that AI isn't smart enough — it's that we haven't given it a clear, persistent, and verifiable "work environment."**

`harness-init` plants **AI work instructions, quality gates, and a state management system** into the project the very first second it's created. From then on, any AI tool entering the project knows: what workflow to follow, how to hand off tasks, and what "done" actually means.

---

## ✨ Core Features

- **🤖 Agent-Native Design**: The generated `AGENTS.md` defines a mandatory three-role workflow — Planner → Generator → Evaluator — teaching AI to "collaborate by division of labor."
- **✅ Generate-and-Verify**: Built-in `make verify` pipeline enforcing ruff linting + pytest tests with a coverage threshold of **≥85%**. If quality doesn't pass, the project isn't considered successfully generated.
- **🛡️ Constraints as Code**: Automatically provides Git Hook scripts and GitHub Actions CI configuration (optional), making conventions hard constraints that cannot be bypassed.
- **📋 Standardized Handoff Protocol**: Plan templates, progress state files, and handoff summaries let AI "seamlessly pick up the baton" even in a brand-new session.
- **🌍 Bilingual Documentation**: Auto-generates Chinese and English `README.md` files, lowering the collaboration barrier for international teams.
- **🎯 Python-Focused, Deliberately Lightweight**: Doesn't implement a complex agent runtime — it does one thing well: define a universal collaboration spec.

---

## 📦 Installation

```bash
pip install harness-init
```

Requires Python 3.11 or higher.

---

## 🚀 Quick Start

### 1. Create a New Project

```bash
harness-init my-awesome-project
```

Follow the prompts to enter project description and author info (or use `--yes` to skip).

### 2. Enter the Project and Install Dependencies

```bash
cd my-awesome-project
pip install -e ".[dev]"
```

### 3. Run the Verification Pipeline

```bash
make verify
```

If everything is fine, you'll see `✔ Verification passed`.

### 4. Invite AI In

Open the project with Claude Code, Cursor, or Codex, and tell the AI:

> "Please read `AGENTS.md` and act as the Planner to help me plan a feature: add a CLI command that displays system information."

The AI will automatically read the workflow definition and complete the task following the **Plan → Generate → Evaluate** rhythm.

---

## 📁 Generated Project Structure

```
my-awesome-project/
├── .harness/                 # Agent workspace
│   ├── plans/                # Plan files
│   ├── state/                # State persistence
│   ├── templates/            # Plan templates, etc.
│   ├── logs/                 # Runtime logs
│   └── progress.json         # Task progress tracking
├── configs/                  # Multi-environment configuration
├── docs/                     # Documentation (includes context.md)
├── src/my_awesome_project/   # Main package
│   ├── cli.py                # CLI entry point
│   ├── harness/              # Core engine (runner/evaluator/state/workflow)
│   ├── agents/               # Agent stubs (planner/generator/evaluator)
│   ├── tools/                # Tool functions
│   └── utils/                # Utility helpers
├── tests/                    # Test suite
├── .gitignore
├── AGENTS.md                 # AI workflow mandatory guide
├── opencode.yaml             # Codex configuration (includes custom commands)
├── Makefile                  # Verification and automation tasks
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Chinese documentation
└── README.en.md              # English documentation
```

---

## 🛠️ CLI Options

| Option | Short | Description |
| :--- | :--- | :--- |
| `--force` | `-f` | Force overwrite of an existing directory (old one is auto-backed up) |
| `--no-git` | | Skip Git initialization |
| `--yes` | `-y` | Skip all interactive prompts and use defaults |
| `--ci <platform>` | | Generate CI configuration files (currently supports `github`) |
| `--version` | `-v` | Show version number |

---

## 🗺️ Roadmap

### ✅ Completed (v0.3.0)
- [x] Enhanced `AGENTS.md`: mandatory three-stage workflow instructions
- [x] Standardized plan template `.harness/templates/plan_template.md`
- [x] State file `progress.json` schema definition

### 🔨 In Progress (v0.4.0)
- [ ] Provide Git Hook scripts (`pre-commit`) with optional manual enablement
- [ ] Optional GitHub Actions CI configuration generation (`--ci github`)
- [ ] Optimize post-generation "next steps" hints

### 📅 Planned
- [ ] Support more AI tools: `CLAUDE.md`, `.cursorrules` generation
- [ ] Project map `docs/PROJECT_MAP.md` (machine-readable)
- [ ] Explore multi-tech-stack support (Node.js / Go)

> ⏰ This project is maintained in my spare time. The roadmap does not promise specific release dates and is dynamically adjusted based on feature priority and community feedback.

---

## 📅 Maintenance Cadence

- 🐛 **Bug Fixes**: Usually responded to within one week.
- ✨ **New Features**: A minor version is released every **2-4 weeks**, following the roadmap.
- 💬 **Issue Replies**: Best effort to reply within 48 hours.

Thank you for your patience and understanding! Discussions via Issues and Discussions are welcome.

---

## 🤝 Contributing

Contributions of any kind are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for development conventions and submission workflow.

---

## 📄 License

MIT License © [renjianguojinqianfan](https://github.com/renjianguojinqianfan)

---

## 🙏 Acknowledgments

- [Typer](https://typer.tiangolo.com/) — Elegant CLI framework
- [Ruff](https://docs.astral.sh/ruff/) — Blazing-fast Python linter
- [Pytest](https://docs.pytest.org/) — Reliable testing framework
- Inspiration: Anthropic's GAN-style three-agent architecture, OpenAI's "code repository as a system of record" practice, and Martin Fowler's Harness Engineering discourse.

---

**[Chinese Version](README.md)**
