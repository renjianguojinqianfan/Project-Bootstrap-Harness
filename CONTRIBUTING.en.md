# Contributing Guide (CONTRIBUTING.en.md)

Welcome! Please read the project's [AGENTS.md](AGENTS.md) to understand the collaboration protocol before contributing.

## Quick Start

This project was initialized by PBH itself, so please confirm you have understood the project's AGENTS.md before starting.

```bash
make verify    # Ensure the environment is ready
pytest tests/  # Ensure all existing tests pass
```

## Contribution Workflow

1. Fork this repository and create a feature branch
2. Declare your task plan in `tasks/` before modifying code
3. Follow the working guidelines in AGENTS.md: state your plan before coding
4. Ensure `make verify` passes (lint + test + coverage ≥ 85%)
5. Submit a PR, referencing relevant AGENTS.md clauses in the description

## What Contributions Are Welcome

- New `--ide` adapters (AI tool-specific guide files)
- New `--template` skeletons (project type templates)
- Template placeholder omission fixes
- Factual error corrections in documentation
- Harness-Lint rule proposals (must include an explanation of "Which AI defect does this catch?")

## What Contributions Are Politely Declined

- Adding Agent runtime logic to the PBH core
- Adding specific Agent role definitions to templates
- Defining machine-readable rule files (e.g., `rules.yaml`)
- Any change that shifts PBH from "seeding" to "executing"

(See [DESIGN.md](DESIGN.md) for the design decisions behind these boundaries)

## Code of Conduct

This project uses AGENTS.md to define collaboration rules. By contributing, you agree to follow these rules in all interactions.

If you find room for improvement in AGENTS.md itself, you are welcome to submit a PR — this is the practice of PBH's "attribution anchoring" philosophy in action.
