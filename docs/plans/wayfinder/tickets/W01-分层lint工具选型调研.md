---
id: W01
title: 分层依赖 lint 执行工具选型调研
type: research
status: closed
blocked_by: []
assignee: research-subagent
map: ../MAP-p1-机械执法层.md
---

## Question

分层依赖规则已定为**声明式配置**形态（`.harness/layers.yaml` 声明层与依赖方向）。本票据调研：用哪个现成工具来**执行**这份声明的校验？候选：

- `import-linter`（成熟，`.importlinter` 契约式配置）
- `grimp` / `deptry`（依赖图分析库）
- ruff 自定义规则 / `ruff` 生态能否表达分层约束
- 自写 ~50 行校验脚本（零依赖）

评估维度：能否从声明式 `layers.yaml` 驱动（而非工具自有配置格式）、纯静态（不运行代码）、安装成本、错误信息是否可被注入修复提示、可拆卸性（用户移除后无残留）。

产出：候选对比表 + 推荐选型 + `.harness/layers.yaml` schema 应包含哪些字段才能适配该工具。调研笔记写入 `docs/plans/wayfinder/research/W01-*.md`。

## Resolution

推荐 **grimp + ~50 行胶水脚本 `scripts/lint_deps.py`**：grimp 提供一等分层 API `find_illegal_dependencies_for_layers(layers, containers)`，与 layers.yaml 字段一一对应，可声明式直驱、纯静态（源码级解析）、报错文案由胶水层自控（可注入"违规 + 原因 + Fix:"三段式）、删除脚本+YAML+dev 依赖后零残留。
import-linter 作为备选（语义相同但配置格式绑定、报错不可定制、拆卸有残留）；deptry 查的是依赖声明卫生不适用；ruff TID251 banned-api 仅全局黑名单，无法表达上下文相关的分层约束，只能作补充。
`.harness/layers.yaml` 建议字段：`version` / `root_packages` / `options`（exclude_type_checking_imports 等）/ `contracts[]`（name、containers、layers 高→低序、同层 siblings.independent）/ `ignore[]`（带 reason 的豁免）。注意：grimp 要求被分析包可被定位（src 布局需先 editable 安装或将 `src/` 加入 `sys.path`）。
详细论证与候选对比表见 `docs/plans/wayfinder/research/W01-分层lint工具选型.md`。
