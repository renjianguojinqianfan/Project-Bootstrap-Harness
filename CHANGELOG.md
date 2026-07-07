# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4] - 2026-07-07

### Added

- **Makefile**：新增 `make format` 目标（`ruff format src/ tests/`），提供确定性的代码格式化命令；与 `make format-check`（检查）形成"应用/检查"对称。同步 `templates/common/Makefile`。

### Fixed

- **`make fix` 空引用**：8 个模板文件（4 个 AGENTS.md、`cli/CLAUDE.md`、`cli/.cursorrules`、`common/README.md`、`common/README.en.md`）引用了不存在的 `make fix` 目标。改为 `make format`（仅 `ruff format`，确定性格式化）；lint 类涉及代码含义的修复不设命令，仍由 Agent 决断（受 AGENTS.md "Auto-fix circuit breaker" 约束）。

### Changed

- **文档同步 `format-check`**：4 个模板 AGENTS.md §9 Commands、`cli/CLAUDE.md`、`cli/.cursorrules`、仓库 `README`/`CONTRIBUTING`/PR 模板的 `make verify` 描述由 "lint + tests + coverage" 更新为 "lint + format-check + tests + coverage"。

### Docs

- **PBH-SPEC §2.3**：将 `project_type`（MAY）与 `harness_version`（SHOULD）补入 `.harness/progress.json` schema，匹配 v2.0.3 起的实际写入行为；配套 PRD 见 `docs/plans/2026-07-07-progress-json-fields-spec-sync.md`。

## [2.0.3] - 2026-07-07

### Added

- **Makefile**：`verify` 依赖链新增 `format-check` 目标（`ruff format --check src/ tests/`），在 lint 与 test 之间强制代码格式门禁；同步 `templates/common/Makefile`，使 `harness-init` 生成的项目开箱即具备格式检查能力。

### Fixed

- **progress.json**：`core.py` 生成 `.harness/progress.json` 时补齐 `project_type` 与 `harness_version` 字段。`project_type` 不再硬编码为 `cli`，改为写入用户传入的 `--template` 实际值（cli/lib/web/notebook）；`harness_version` 通过 `importlib.metadata.version("harness-init")` 动态获取，符合 PBH-SPEC 兼容性机制要求。

## [2.0.2] - 2026-06-15

### Fixed

- **Makefile** `make verify` 输出由 `✅ 验证通过` 改为 ASCII `[OK] verified`，修复 Windows PowerShell 默认控制台下中文 emoji 的乱码问题；同步更新 `templates/common/Makefile`，确保 `harness-init` 生成的项目跨平台输出一致。

### Changed

- **AGENTS.md**：`§1 Project Snapshot` 与 `§6 File Mapping` 同步至 v2.0+ 实际代码结构（覆盖 `validation.py`、`validators/` 包、`_quick.py`、`_ide.py`、`_templates.py`、多类型模板路径与 `docs/spec/PBH-SPEC.md` 入口）。
- **README.md** / **README.en.md**：更新 `make verify` 预期输出示例以匹配新的 ASCII 字符串。

## [2.0.1] - 2026-06-14

### Fixed

- **P0** 修复 `core.py` 与 `validation.py` 超长模块/函数问题：拆分为 `validators/` 包、`_ide.py`、`_quick.py`，确保所有模块 ≤200 行、函数 ≤30 行，符合 AGENTS.md 约束。
- **P1** 修复验证器返回值类型与跨平台路径校验：统一返回 `ValidationResult` TypedDict；禁止项目名包含 `..`、路径分隔符或绝对路径；测试改用相对路径 `tmp_path` chdir 夹具。
- **P2** 修复魔法值与 `_run_init` 参数类型：将项目名/PEP-508 正则与 git 错误信息模板提取为模块常量；为 `_run_init` 增加 `_InitKwargs` TypedDict。

### Changed

- 更新 `README.md` / `README.en.md` 生态表格中 Harness-Lint 规则数量，从 9 条改为 10 条。

## [2.0.0] - 2026-05-23

### Added

- `harness-init validate` 命令：检查项目是否符合 PBH v2.0 协议规范。
  - 文件存在性检查：`AGENTS.md`、`Makefile`（含 verify target）、`.harness/progress.json`。
  - 内容合规性检查：AGENTS.md 的 5 个必须章节、Quick Start 首步必须是 `make verify`、Critical Rules 三项禁令、progress.json schema 验证。
  - 行为合规性检查：运行 `make verify` 并验证退出码。
- `harness-init doctor` 命令：检查本地开发环境是否满足 PBH 协作前提条件（make、git、python、pip）。
- `src/harness_init/validation.py`：新增合规性验证模块，包含 `validate_project()` 和 `check_doctor()` 核心函数。
- `tests/test_validation.py`：新增 30+ 测试用例覆盖所有验证逻辑。

### Changed

- `src/harness_init/cli.py`：从单命令 `typer.run()` 重构为多命令 `typer.Typer()` 应用，支持 init/validate/doctor 子命令。
- `pyproject.toml`：版本号升级至 2.0.0。
- `docs/spec/PBH-SPEC.md`：协议状态从 Draft 更新为 Released。
- `README.md`：更新路线图，标记 v2.0.0 为已完成。

## [1.5.1] - 2026-04-27

### Fixed

- 补齐缺失的 `templates/lib/` 模板目录，修复 `--template=lib` 参数导致的生成失败。
- 修复 `.gitignore` 中 `lib/` 规则误伤项目源码的 `lib/` 模板目录。

### Changed

- 在 `.gitignore` 中新增 `opencode.json` 和 `.opencode/` 忽略规则，屏蔽个人工具链配置。

## [1.5.0] - 2026-04-27

### Added

- `--template` / `-t` 参数：支持多项目类型模板（`cli`, `lib`, `web`, `notebook`）。
  - `cli`（默认）：命令行工具，含 typer CLI 入口。
  - `lib`：纯 Python 库，含 `__init__.py` 导出示例函数。
  - `web`：FastAPI Web 项目，含 `/health` 端点和 TestClient 测试。
  - `notebook`：Jupyter Notebook 项目，含示例 `.ipynb` 和 `notebooks/` 目录。
- `--ide` 参数：按需生成 IDE 适配文件。
  - `all`（默认）：生成全部 IDE 配置（Cursor、Claude、Trae、Copilot、OpenCode）。
  - `none`：不生成任何 IDE 配置。
  - 支持单独指定：`cursor`, `claude`, `trae`, `copilot`, `opencode`。
- `.harness/known_pitfalls.md`：新增项目常见陷阱记录模板。
- `.trae/rules/rules.md`：Trae IDE 规则适配模板。
- `.github/copilot-instructions.md`：GitHub Copilot 指令适配模板。
- 模板目录重构：`templates/` 拆分为 `common/`（共享文件）+ `cli/`（类型专属）+ `lib/` + `web/` + `notebook/`。
- 多源模板复制：`_templates.py` 支持从 `common/` 和类型目录合并复制。

### Changed

- `README.md`：补充 `--template` 和 `--ide` 使用示例；更新路线图标注 v1.5.0 已完成。
- `AGENTS.md`（全部模板类型）：将硬性数值限制（"Function ≤ 30 lines"）改为原则性阐述，避免与 IDE 适配文件冲突。
- `docs/PROJECT_MAP.md`：更新设计哲学为 "Protocol-first scaffolding"；`.harness/` 注释改为 "Project state tracking"。
- `docs/context.md`：`.harness/` 注释改为 "Project state tracking"。
- `docs/decisions/ADR_TEMPLATE.md`：删除已废弃的 Change Control Matrix 引用块。
- `pyproject.toml`：Development Status 更新为 `5 - Production/Stable`。
- `__init__.py`：回退版本号更新为 `1.5.0`。
- CLI 帮助文本：改进 `--template` 和 `--ide` 的说明，明确列出可选值和默认值。

### Fixed

- `_copy_template_source()` 函数长度：提取 `_place_file()` 辅助函数，确保所有函数 ≤ 30 行。
- IDE 文件过滤逻辑：修复 quick 模式下错误排除 IDE 文件的问题。

## [1.1.7] - 2026-04-27

### Added

- `src/harness_init/_templates.py`: 将模板处理逻辑从 `core.py` 抽取，控制 core.py 行数在 200 行以内。
- `templates/tasks/task_plan.md`: 新增 Spec Coding 任务容器模板。
- `tests/test_templates.py`: 为模板处理模块添加单元测试（16 个测试用例）。
- `tests/test_core.py`: 新增 `test_init_project_creates_tasks_directory` 测试。

### Changed

- `core.py`: 重构 `_copy_templates()`，拆分超长函数，行数从 227 降至 153。
- `core.py`: 新增 `_init_git_safe()`，安全处理 Git 初始化失败回滚。
- `core.py _create_directories()`: 新增 `tasks/` 目录创建。
- `templates/configs/test.yaml`: 移除 `runner`/`evaluator`/`state` 过时配置段。
- `templates/configs/prod.yaml`: 移除 `runner`/`evaluator`/`state` 过时配置段。

## [1.1.6] - 2026-04-26

### Added

- `docs/DESIGN.md`: 核心设计哲学与架构决策归档。
- `CONTRIBUTING.md`: 贡献指南，将 PBH 协议要求融入贡献流程。

### Changed

- `pyproject.toml` 和 `__init__.py` 版本号同步至 1.1.6。

## [1.1.5] - 2026-04-25

### Fixed

- 修复 `publish.yml` 中 `skip-existing: true` 导致跳过上传的问题，正式发布到 PyPI。

## [1.1.4] - 2026-04-25

### Fixed

- 修复 AGENTS.md 模板变量 `{project_type}` 未替换的残留问题。
- 修复 `.cursorrules` 和 `CLAUDE.md` 模板中遗留的旧版三角色工作流描述。

## [1.1.3] - 2026-04-25

### Fixed

- 修复 PyPI 发布中由 TestPyPI 与正式版状态不一致导致的 400 Bad Request 错误。

## [1.1.2] - 2026-04-24

### Fixed

- 修复版本冲突导致的发布失败问题。

## [1.1.1] - 2026-04-24

### Fixed

- 补充 v1.1.0 遗漏的模板文件，确保生成项目完整性。

## [1.1.0] - 2026-04-24

### Changed

- **Positioning Calibration (Phase 1)**: PBH is now strictly a project structure generator, not an agent runtime framework.
  - Removed `harness/`, `agents/`, `tools/` stubs from templates — these were agent runtime facilities outside PBH's scope.
  - Simplified `_create_directories()` and `_create_source_files()` in `core.py` to only create essential directories.
- **AGENTS.md Rewrite**: Converted from manifesto-style (Principle → Protocol → Workflow → File Mapping) to airport-navigation style.
- **Quick Mode Cleanup**: Updated `_QUICK_MODE_EXCLUSIONS` and `pyproject.quick.toml`.
- **Template Simplification**: `cli.py` and test templates now use basic `typer` example.

### Removed

- `src/{package_name}/harness/` template files: `runner.py`, `evaluator.py`, `state.py`, `workflow.py`
- `src/{package_name}/agents/` template files: `planner.py`, `generator.py`, `evaluator.py`
- `tests/test_harness.py` template

## [1.0.0] - 2026-04-20

> **Note**: This release consolidates features originally planned for v0.4.0 and v0.5.0 into a single stable release.

### Added

- Plan Template v2 (JSON Schema)
- Approval Workflow, Security Guidelines
- DevOps templates (CI, pre-push hooks)
- IDE Adapter files (CLAUDE.md, .cursorrules)
- Documentation templates (PROJECT_MAP.md, ADR_TEMPLATE.md)
- Cross-platform `.sh` executable permissions

### Changed

- AGENTS.md trimmed from 114 → 99 lines
- `core.py` now creates `scripts/` and `.github/workflows/` directories

### Fixed

- `plan_template.md` removed; all references updated to `plan_template.json`.

## Historical Roadmap (Pre-1.0)

- **v0.4.0 (planned)**: Git Hook integration
- **v0.5.0 (planned)**: Multi-agent IDE adapters
- **v1.0.0 (actual)**: All of the above consolidated

## [0.3.0] - 2026-04-17

### Added

- Agent-Native Workflow Activation with Planner/Generator/Evaluator roles
- Standard plan template and proper `progress.json` schema

### Changed

- README files updated to reflect new Agent workflow features
- Root AGENTS.md File Mapping updated

### Fixed

- `core.py` now generates a valid `progress.json`

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