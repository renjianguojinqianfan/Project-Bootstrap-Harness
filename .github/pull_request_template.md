<!--
  此模板用于本仓库的 PR 描述。GitHub 创建 PR 时会自动填充。
  按需删除不适用的章节，不要把空清单留下来。
-->

## 改动概述

<!-- 一两句话说清楚做了什么、为什么 -->

## 改动类型

- [ ] feat (新功能)
- [ ] fix (Bug 修复)
- [ ] docs (文档)
- [ ] refactor (重构)
- [ ] ci (CI/CD)
- [ ] release (发版)
- [ ] chore (其他)

## 自检清单

- [ ] `make verify` 通过（lint + 格式检查 + 测试 + 覆盖率 ≥ 85%）
- [ ] 改了 `src/` 结构 → `AGENTS.md` §6 File Mapping 已同步
- [ ] 改了 CLI 命令/参数 → `README.md` + `README.en.md` + `AGENTS.md` §1 已同步
- [ ] 改了 `templates/` → 顶层 `Makefile` 与模板 `Makefile` 已对齐
- [ ] 用户可感知变化 → `CHANGELOG.md` 已更新

## 发版 PR 专用（仅当改动类型是 release 时）

- [ ] 已读 `docs/RELEASE.md`
- [ ] `pyproject.toml` 与 `src/harness_init/__init__.py` 版本号一致
- [ ] **未误改** `templates/*/pyproject.toml` 与 `core.py` 中的 `0.1.0` 模板字符串
- [ ] 已用 `pip index versions harness-init` 确认目标版本号未被占用
