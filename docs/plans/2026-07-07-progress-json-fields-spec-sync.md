# PRD: progress.json 字段纳入 PBH-SPEC §2.3

> 日期：2026-07-07
> 关联版本：v2.0.4
> 状态：已实施

## 背景

v2.0.3 起，`harness-init` 在生成 `.harness/progress.json` 时写入两个新字段：

- `project_type`：取用户传入的 `--template` 实际值（cli/lib/web/notebook）
- `harness_version`：通过 `importlib.metadata.version("harness-init")` 动态获取

`harness_version` 已在 PBH-SPEC §4.2 声明为 SHOULD，但 §2.3 的 schema 块未列出；`project_type` 在规范中完全未文档化（仅 §1 Project Snapshot 定义了类型概念）。

## 决策

将 `project_type`（MAY）与 `harness_version`（SHOULD，引用 §4.2）补入 PBH-SPEC §2.3 的 schema 定义与字段表，作为可选字段。

## 合规性影响

- 仅新增可选字段，不引入新的 MUST 要求
- 现有项目的 `progress.json`（不含这两个字段）仍通过 `harness-init validate`
- `validators/progress_json.py` 不变（不强制校验这两个字段）

## 涉及文件

- `docs/spec/PBH-SPEC.md` §2.3
- `docs/spec/PBH-SPEC.zh-CN.md` §2.3
