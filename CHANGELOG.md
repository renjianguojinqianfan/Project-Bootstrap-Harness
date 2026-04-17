# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-04-17

### Added

- **Agent-Native Workflow Activation (P0)**: Generated projects now include a complete three-role workflow for external agents.
  - `AGENTS.md` template enhanced with mandatory **Planner / Generator / Evaluator** role instructions. Agents must explicitly declare their role before acting.
  - `.harness/templates/plan_template.md`: Standard Markdown plan template with Goal, Steps, Affected Files, Acceptance Criteria, and Rollback Plan sections.
  - `.harness/progress.json`: Now generated with a proper schema (`project_name`, `current_stage`, `plans`, `last_updated`) instead of the previous minimal placeholder.

### Changed

- `README.md` and `README.en.md` updated to reflect the new Agent workflow features.
- Root `AGENTS.md` File Mapping updated to include plan templates.

### Fixed

- `core.py` now generates a valid `progress.json` that external agents can actually read and update (previously it was a hardcoded minimal JSON).

## [0.2.1] - 2026-04-16

### Fixed

- Synced `__version__` with `pyproject.toml`.
- Fixed `.gitignore` inclusion in wheel.

## [0.2.0] - 2026-04-16

### Added

- Added `MANIFEST.in` to include `README.en.md` in distributions.

## [0.1.0] - 2026-04-15

### Added

- Initial release of `harness-init`.
- CLI tool to scaffold complete, harness-ready Python projects.
- Generated projects include: package structure, CLI, tests, Harness runtime, Git init, `make verify` pipeline.
