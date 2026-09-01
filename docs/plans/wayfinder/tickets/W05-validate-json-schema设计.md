---
id: W05
title: validate --json 输出 schema 与 trace 落盘设计
type: grilling
status: open
blocked_by: [W02]
assignee: ""
map: ../MAP-p1-机械执法层.md
---

## Question

基于 W02 的格式调研结论，敲定可观测性最小闭环的全部设计：

- `harness-init validate --json` 的输出 schema：维度、严重级、修复提示字段（对齐报告维度 8 "最低成本改进"建议，但按用户决定对齐 OTel 语义）
- 落盘策略：`.harness/trace/validate-<ts>.json` 的命名、保留策略（轮转/清理由谁负责）、是否默认开启还是 `--trace` 显式开启
- `doctor` 是否同样输出结构化结果
- 现有 `validators/_base.py` 结果结构到 JSON 的映射，改动是否破坏现有 stdout 契约（向后兼容策略）
- 为雾区预留：生态闭环接口（`harness-lint`/`harness-agent` 消费该格式）需要什么稳定性承诺

前置：须先读 W02 结论。

## Resolution

（待解决）
