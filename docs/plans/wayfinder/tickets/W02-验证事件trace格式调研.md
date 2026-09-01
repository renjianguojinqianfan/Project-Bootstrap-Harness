---
id: W02
title: 验证事件 trace 格式调研（OpenTelemetry 对齐）
type: research
status: closed
blocked_by: []
assignee: research-subagent
map: ../MAP-p1-机械执法层.md
---

## Question

用户已决定可观测性方向是**对齐 OpenTelemetry**。本票据调研落地形态：

1. OpenTelemetry 对"非服务类、本地构建/验证事件"的最小表达是什么（Span？Event？LogRecord？Semantic Conventions 里有没有 build/test 相关属性，如 `code.*` / CI 语义）
2. 对 CLI 工具（如 `harness-init validate`）而言，完整的 OTel SDK 是否过重？最小依赖路径（OTLP JSON 导出？还是只用其 schema/语义约定手写 JSON）
3. 行业先例：有没有工具把 lint/test/verify 结果落盘为 OTel 兼容格式（如 GitHub Actions OTel exporter、pytest-otel 等）
4. 给 `validate --json` + `.harness/trace/validate-<ts>.json` 的格式建议：完整 OTLP-JSON 还是"OTel 语义约定字段 + 普通 JSON"

产出：格式建议 + 依赖成本对比 + 与一手调研文档中"数据飞轮"目标的匹配度评估。调研笔记写入 `docs/plans/wayfinder/research/W02-*.md`。

## Resolution

结论：**"OTel 语义约定字段 + 普通 JSON（OTLP-JSON 结构子集）"，零新增依赖**。一次 `validate` 运行建模为 1 个根 Span + 每检查项 1 个子 Span，字段直接复用 OTel CI/CD 语义约定（`cicd.pipeline.result` / `cicd.pipeline.task.run.result` / `error.type`，semconv v1.27.0+，Release Candidate）。完整 `opentelemetry-sdk`+OTLP exporter 会引入 grpcio/protobuf 等重型二进制依赖，与零依赖播种器定位冲突（行业先例选完整栈皆为在线导出场景）。手写 JSON 路线规范兼容：OTLP 官方定义 JSON Protobuf Encoding 且接收端 MUST 忽略未知字段；结构对齐后可平滑升级为合法 OTLP/HTTP JSON。与数据飞轮匹配：低基数枚举字段支持通过率/失败分布聚合，详见调研笔记。
