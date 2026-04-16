# AGENTS.md - harness-init

> 这是 `harness-init` 项目本身的 Agent 操作手册。如果你是打开生成后项目的 Agent，请阅读该目录下的 `AGENTS.md`。
> **Principle**: Keep this file to 50-100 lines. Deep context lives in `docs/plans/` and inline code comments.

## 1. Project Snapshot

**harness-init** is a CLI tool to scaffold harness-ready Python projects. It generates non-empty projects that pass `make verify` immediately.

**Maintainer**: harness-init team  
**Type**: cli

## 2. Change Control Matrix (Feedforward)

| Error Type | Rollback Level | Mechanical Guard |
|------------|----------------|------------------|
| Requirement error | Re-clarify in this file / docs | **FROZEN**: No spec change without PRD update in `docs/plans/` |
| Design error | Update architecture decision | No code without ADR in `docs/decisions/` |
| Code error | Fix directly | `make verify` must pass; auto-fix <= 2 attempts |

## 3. Session Protocol (Spec Coding Loop)

**One session = One atomic task**

1. **Orient**: Read this file and `docs/plans/` → understand current state
2. **Verify Baseline**: Run `make verify` → must pass before any edit
3. **Select Task**: Pick ONE item from open issues / plans → mark in progress
4. **Implement**: Generate code → auto-trigger `make verify`
5. **Commit**: Write descriptive commit → update relevant docs

## 4. Agent Rules (DO / DON'T)

- **DO** read `docs/plans/` before making architectural decisions
- **DO** run `make verify` after every change; Evaluator role MUST NOT be skipped
- **DO** keep `cli.py` thin (only argument parsing), put logic in `core.py`
- **DON'T** commit failing code; DON'T fix unrelated code during task
- **DON'T** let `core.py` or any file exceed 200 lines; refactor early
- **DON'T** put deep context in this file

## 5. Key Constraints

- `cli.py` **只负责**参数解析和调用 `core.py`
- `core.py` **处理所有**文件生成和 Git 初始化逻辑
- `templates/` **存放所有**目标项目模板；长模板优先独立文件
- 所有核心逻辑**必须有**单元测试
- 函数 ≤ 30 行，文件 ≤ 200 行
- 测试覆盖率 ≥ 85%，由 `pytest-cov` 强制执行
- **Auto-fix circuit breaker**: Max 2 auto-fix attempts per error, then rollback
- **Agent self-evaluation ban**: ONLY `make verify` output is ground truth

## 6. File Mapping

| Type | Location | Description |
|------|----------|-------------|
| CLI | `src/harness_init/cli.py` | Argument parsing only |
| Core | `src/harness_init/core.py` | Project generation logic |
| Utils | `src/harness_init/_utils.py` | Name validation, template rendering |
| Git helpers | `src/harness_init/_git.py` | Git init and rollback helpers |
| Templates | `src/harness_init/templates/` | Target project templates |
| Tests | `tests/` | Unit tests (mirror `src/` structure) |
| Plans | `docs/plans/` | Design docs and task plans |
| Entry | `README.md` / `README.en.md` | Human-facing documentation |
