# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.6] - 2026-04-26

### Added

- `docs/DESIGN.md`: 核心设计哲学与架构决策归档。
- `CONTRIBUTING.md`: 贡献指南，将 PBH 协议要求融入贡献流程。

### Changed

- `pyproject.toml` 和 `__init__.py` 版本号同步至 1.1.6。

## [1.1.0] - 2026-04-24

### Changed

- **Positioning Calibration (Phase 1)**: PBH is now strictly a project structure generator, not an agent runtime framework.
  - Removed `harness/`, `agents/`, `tools/` stubs from templates — these were agent runtime facilities outside PBH's scope.
  - Simplified `_create_directories()` and `_create_source_files()` in `core.py` to only create essential directories.
- **AGENTS.md Rewrite**: Converted from manifesto-style (Principle → Protocol → Workflow → File Mapping) to airport-navigation style:
  - Quick Start (30 seconds to get working)
  - Critical Rules (`make verify` gate, coverage ≥85%)
  - File Mapping
  - Common Commands
- **Quick Mode Cleanup**:
  - `pyproject.quick.toml` now only includes `typer + pytest + ruff` (removed `pydantic`, `pyyaml`, `rich`).
  - Updated `_QUICK_MODE_EXCLUSIONS` to remove references to deleted stubs.
- **Template Simplification**:
  - `cli.py` and `cli.quick.py` templates now use a basic `typer` example (hello/version) instead of importing harness modules.
  - `test_cli.py` template updated to match the simplified CLI.

### Removed

- `src/{package_name}/harness/` template files: `runner.py`, `evaluator.py`, `state.py`, `workflow.py`
- `src/{package_name}/agents/` template files: `planner.py`, `generator.py`, `evaluator.py`
- `tests/test_harness.py` template

## [1.0.0] - 2026-04-20

> **Note**: This release consolidates features originally planned for v0.4.0 and v0.5.0 into a single stable release.

### Added

- **Plan Template v2 (Breaking)**: Converted `.harness/templates/plan_template.md` to `plan_template.json` with JSON Schema + YAML front matter for machine-readable plan validation.
- **Approval Workflow**: `AGENTS.md` now enforces explicit `proposed → approved → completed` state machine. Human approval is mandatory before code generation.
- **Security Guidelines**: Added Chinese-language security section to `AGENTS.md` covering: no auto-execution of unreviewed commands, secrets handling, and dependency scanning.
- **DevOps Templates** (originally planned for v0.4.0):
  - `.pre-commit-config.yaml`: Optional pre-commit hooks (ruff, trailing-whitespace, check-yaml).
  - `.github/workflows/ci.yml`: GitHub Actions workflow with Python 3.11/3.12 matrix, `make verify`, and coverage reporting.
  - `scripts/pre-push.sh` + `scripts/pre-push.ps1`: Cross-platform pre-push hooks.
- **IDE Adapter Files** (originally planned for v0.5.0):
  - `CLAUDE.md`: Quick-reference adapter for Claude Code aligned with AGENTS.md workflow.
  - `.cursorrules`: Cursor IDE configuration enforcing project constraints (≤30 lines/function, ≥85% coverage).
- **Documentation Templates**:
  - `docs/PROJECT_MAP.md`: Machine-readable project structure map with YAML front matter.
  - `docs/decisions/ADR_TEMPLATE.md`: Standard ADR template referencing Change Control Matrix.
- **Cross-Platform Fix**: `.sh` scripts now get `0o755` executable permissions on Unix systems automatically.

### Changed

- **AGENTS.md**: Trimmed from 114 → 99 lines while adding approval workflow and security sections. All plan references now point to `.json` format.
- **docs/context.md**: Synchronized to reference `plan_template.json` instead of `.md`.
- **opencode.yaml**: Added note about optional `commands` section without adding the field itself (stays minimal).
- `core.py`: `_create_directories()` now includes `scripts/` and `.github/workflows/`.

### Fixed

- `plan_template.md` removed; all references updated to `plan_template.json`.

## Historical Roadmap (Pre-1.0)

These items were originally planned as incremental releases but were consolidated into v1.0.0:

- **v0.4.0 (planned)**: Git Hook integration (`pre-commit` config, CI workflow, pre-push scripts).
- **v0.5.0 (planned)**: Multi-agent IDE adapters (`CLAUDE.md`, `.cursorrules`).
- **v1.0.0 (actual)**: All of the above + plan template format migration + ADR/PROJECT_MAP + full test coverage.

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

> **Note**: v1.1.1 ~ v1.1.5 为 PyPI 发布流程修复与模板清理，记录待 v1.5.0 发布时补全。
