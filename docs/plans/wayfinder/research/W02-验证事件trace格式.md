# W02 调研笔记：验证事件 trace 格式（OpenTelemetry 对齐）

- 票据：`docs/plans/wayfinder/tickets/W02-验证事件trace格式调研.md`
- 日期：2026-09-01；方法：一手来源优先（opentelemetry.io 规范原文、PyPI 元数据、官方/一手项目），每条论断标注出处
- 调研对象：`harness-init validate --json` + `.harness/trace/validate-<ts>.json` 的落地形态

## TL;DR 结论

**推荐"OTel 语义约定字段 + 普通 JSON"（结构上对齐 OTLP-JSON 子集），不引入任何 OTel Python 依赖。**
一次 `validate` 运行建模为 1 个根 Span + 每个检查项 1 个子 Span，字段直接复用 OTel CI/CD 语义约定
（`cicd.pipeline.result` / `cicd.pipeline.task.run.result` 等），零运行时成本、保留未来升级为完整
OTLP 导出的路径。一句话理由：完整 `opentelemetry-sdk`+OTLP exporter 会引入 `grpcio`/`protobuf`
等重型二进制依赖，与"零依赖协议播种器"定位冲突，而行业先例（pytest-otel、Jenkins 插件、otel-cli）
采用的完整 SDK 路线都是为了**在线导出**，本地落盘场景只需要它们的**语义字段**。

---

## 1. OTel 对"非服务类、本地验证事件"的最小表达：Span / Event / LogRecord

### 1.1 信号类型定位

- OTel 当前支持的信号为 Traces、Metrics、Logs、Baggage；**Events 是 LogRecord 的一种特殊类型**，
  且仍在 proposal 阶段。（来源：opentelemetry.io 《Signals》
  https://opentelemetry.io/docs/concepts/signals/ ，原文："Events, a specific type of log"）
- 结论：三选一里 **Span 是正解**。`validate` 一次运行是"有起止时间、有结果状态、可含子步骤"的
  执行单元，正是 Span 的定义域；Event/LogRecord 只适合挂在 Span 上的瞬时点记录。

### 1.2 Semantic Conventions 已有 build/test/CI 属性：CI/CD 命名空间

- OTel 语义约定 **v1.27.0 起正式纳入 CI/CD 语义**，覆盖 `cicd`、`artifacts`、`vcs`、`test`、
  `deployment` 五个命名空间，由 CI/CD Observability SIG（2023-11 成立）推动，源于 OTEP #223。
  （来源：CNCF 博客《OpenTelemetry Is Expanding Into CI/CD Observability》，Dotan Horovits &
  Adriel Perkins，2024-11-04；中译全文见腾讯云开发者社区
  https://cloud.tencent.com/developer/article/2505754 ，英文一手为 CNCF blog）
- 官方 CI/CD 语义约定文档现为 **Release Candidate** 状态，定义三种信号的约定（spans/metrics/logs）。
  （来源：opentelemetry.io https://opentelemetry.io/docs/specs/semconv/cicd/ ）
- **与 `validate` 直接对应的两个 Span 模型**（来源：
  https://opentelemetry.io/docs/specs/semconv/cicd/cicd-spans/ ，逐字核对）：
  1. **Pipeline run**（对应一次 `harness-init validate` 运行）：
     - Span kind SHOULD 为 `SERVER`；span 名 SHOULD 为 `{action} {pipeline}`
     - `cicd.pipeline.result`（Required）：枚举 `success` / `failure` / `timeout` / `skip` /
       `cancellation` / `error`；`failure` 的定义原文即"due to a compile error or a failing test…
       detected by non-zero exit codes of the tools"——验证失败恰属此类
     - `error.type`（failure/error 时 Conditionally Required，Stable）
     - `cicd.pipeline.action.name`（Opt-In，well-known 值 `BUILD`/`RUN`/`SYNC`，允许自定义值）
  2. **Pipeline task run**（对应单个检查项，如 `validate_agents_md`）：
     - Span kind SHOULD 为 `INTERNAL`
     - `cicd.pipeline.task.name`（Required）：文档示例即 `Run GoLang Linter`、`go-test` 这类验证步骤
     - `cicd.pipeline.task.run.id`（Required，同一 run 内唯一）
     - `cicd.pipeline.task.run.result`（Required，枚举与 pipeline result 相同）
     - `error.type`（Conditionally Required）
- 可选资源属性：`vcs.repository.ref.revision`（git 提交哈希，CI/CD SIG 称其为 DORA 指标的关键
  元数据，同上腾讯云译文）；`service.name`/`service.version` 标识产出方。
- 注意：`cicd.*` 目前是 Release Candidate 而非 Stable，字段名未来可能微调——这是选择
  "手写字段名（可集中常量管理）"而非依赖 `opentelemetry-semantic-conventions` 包的又一理由。

## 2. 完整 `opentelemetry-sdk` 对零依赖 CLI 是否过重：依赖成本对比

以下依赖清单全部取自 PyPI JSON API 元数据（`https://pypi.org/pypi/<name>/json`，2026-09-01 拉取）：

| 路线 | 包 | 传递依赖（仅运行时） | 评估 |
| --- | --- | --- | --- |
| 手写 JSON | 无 | 无 | 零依赖，字段名为字符串常量 |
| 仅 API | `opentelemetry-api` 1.44.0 | `typing-extensions>=4.5.0` | 轻，但 API 本身**不能导出**任何数据，无实际收益 |
| 完整 SDK | `opentelemetry-sdk` 1.44.0 | `opentelemetry-api`、`opentelemetry-semantic-conventions` 0.65b0、`typing-extensions` | 中等，纯 Python；但 SDK 的价值在处理器/导出器管线，只落盘用不到 |
| 完整导出 | `opentelemetry-exporter-otlp` 1.44.0 | 在以上基础上叠加 `opentelemetry-exporter-otlp-proto-grpc`/`-proto-http`，grpc 变体拉入 **`grpcio>=1.63.2`、`googleapis-common-protos`、`opentelemetry-proto`（protobuf 生成代码）** | 重：`grpcio`/`protobuf` 是平台相关二进制轮子，显著增大安装面，与"纯本地、无服务端"场景完全错配 |

（来源：PyPI JSON API，包版本 1.44.0，`requires_dist` 字段；
`opentelemetry-exporter-otlp-proto-grpc` 的依赖清单含 `grpcio<2.0.0,>=1.63.2` 等）

结论：**对"无服务端、结果落本地文件"的播种器，完整栈是错配的**。完整栈的适用前提是存在
OTLP endpoint（collector/后端），这正是行业先例（见 §3）选择它的原因。

### 2.1 "手写 JSON"是否被社区认可

- OTLP 官方规范明确定义了 **OTLP/HTTP JSON Protobuf Encoding**：proto3 JSON Mapping + 三条偏差
  （`traceId`/`spanId` 用十六进制字符串而非 base64、枚举必须编码为整数、JSON 键为
  lowerCamelCase）。即"用 JSON 表达 span"本身就是协议的一等公民，不是民间发明。
  （来源：OTLP 规范 https://opentelemetry.io/docs/specs/otlp/ ，"JSON Protobuf Encoding" 一节，
  官方示例见 opentelemetry-proto 仓库 examples）
- 规范同时要求 OTLP/JSON 接收端 **MUST 忽略未知字段**，因此自定义扩展字段与接收端兼容。
  （同上，原文："OTLP/JSON receivers MUST ignore message fields with unknown names"）
- 语义约定侧：semconv 对 well-known 枚举值均声明"otherwise, a custom value MAY be used"，
  自定义属性遵循通用命名规则即可。（来源：上述 cicd-spans 规范原文多处）
- 因此"只采纳语义约定字段名 + 普通 JSON（OTLP-JSON 结构子集）"是规范兼容的最小路径；
  未来如需在线导出，可由外部工具（如 `otel-cli`、collector 的 filelog receiver）消费该文件，
  或届时再加 SDK，**字段名不用改**。

## 3. 行业先例：把 lint/test/构建结果导出为 OTel 的工具

| 工具 | 场景 | 选择的形态 | 来源 |
| --- | --- | --- | --- |
| **pytest-otel** 2.4.0（PyPI） | pytest 测试结果 → OTel traces | **完整栈**：依赖 `opentelemetry-api`+`opentelemetry-sdk`+`opentelemetry-exporter-otlp`，经 `--otel-endpoint` 在线导出，测试执行建模为 span（主 span 名由 `--otel-session-name` 指定） | PyPI https://pypi.org/project/pytest-otel/ （JSON API `requires_dist` 与 README 逐字核对）；Elastic 官方文档亦收录："pytest-otel is a pytest plugin for sending Python test results as OpenTelemetry traces"（https://www.elastic.co/docs/solutions/observability/cicd ） |
| **Jenkins OpenTelemetry 插件** | 构建/流水线 → traces & metrics | 插件内嵌 SDK，pipeline/阶段/步骤建模为 span 层级 | Jenkins 插件仓库（转述一致来源：https://m.blog.csdn.net/gitblog_00669/article/details/147291523 ；一手为 jenkinsci/opentelemetry-plugin 仓库） |
| **corentinmusard/otel-cicd-action** | GitHub Actions workflow → OTLP trace | GitHub Actions **无原生 OTel 输出**；该 action 在 `workflow_run: completed` 后拉取 API 元数据，把 run→jobs→steps 还原为 span 树后导出（即"事后重建"模式） | Dash0 官方指南 https://www.dash0.com/guides/github-actions-observability-opentelemetry-tracing （含完整 workflow YAML） |
| **Thoth（opentelemetry-bash/shell/github）** | shell 命令与 GitHub Actions → traces/metrics/logs | 自研 "SDK for shell"，每条命令一个 span，自动注入 `traceparent`；GitHub Actions 提供工作流级（事后拉 API）与任务级（首个 step 注入）两种集成 | 项目介绍（多源一致转述：https://m.blog.csdn.net/weixin_30591519/article/details/160485976 ） |
| **otel-cli** | 任意 shell 命令 → 单个 OTel trace | Go 编写的独立命令行包装器，"observe shell commands as OpenTelemetry traces" | Jenkins OTel 插件文档并列提及（同上转述来源）；一手为 equinix-labs/otel-cli 仓库 |
| **Bazel JSON trace profile**（对照项） | 构建性能分析落盘 | **没有选 OTel**：默认落盘 `command.profile.gz`，为 **Chrome trace event 格式**（`traceEvents` + `otherData` 元数据），供 `chrome://tracing` 与 Bazel Invocation Analyzer 消费 | Bazel 官方文档（一手）：https://bazel.build/advanced/performance/json-trace-profile |
| **Honeycomb《Monitoring Unit Tests with OpenTelemetry》** | 单元测试 → spans | 示范"一次测试运行一个根 span + 每个测试一个子 span"的层级（.NET 实现），并给出 `test.run_id` 等自定义属性 | 一手博客：https://www.honeycomb.io/blog/monitoring-unit-tests-opentelemetry |

先例归纳：
1. **在线导出场景一律选"完整 SDK + span 层级"**（pytest-otel、Jenkins、otel-cicd-action）；
2. **无后端场景的工具（Bazel）干脆用自己的 JSON 格式**——没有任何先例要求本地落盘必须走完整
   OTLP-JSON；
3. 所有 span 化的先例都采用**"运行=根/父 span，步骤=子 span"**的两级结构，这为
   `validate`（run → checks）提供了直接的形态模板。

## 4. 结论建议：`validate --json` 的具体格式方向

### 4.1 推荐方案：OTel 语义约定字段 + 普通 JSON（OTLP-JSON 结构子集）

- **形态**：一次 `validate` 运行 = 1 个根 span + 每个 validator 检查项 = 1 个子 span；
  落盘为单个 JSON 文件 `.harness/trace/validate-<ts>.json`。
- **结构**：借鉴 OTLP-JSON 的 lowerCamelCase 风格与 `resourceSpans→scopeSpans→spans` 层级（但
  只保留必要骨架），使未来可用约 20 行转换脚本升级为合法 OTLP/HTTP JSON（OTLP 规范 §JSON
  Protobuf Encoding，见 §2.1）。
- **字段映射**（现有结构见 `src/harness_init/validators/_base.py` 的 `ValidationResult{check,
  passed, message}`，改动极小——只需序列化层）：

| 现有概念 | 建议字段 | 依据 |
| --- | --- | --- |
| 一次 `validate` 运行 | 根 span；`cicd.pipeline.result` = `success`/`failure`；`cicd.pipeline.name` = `harness-init validate`；`cicd.pipeline.action.name` = `RUN`（或自定义 `VERIFY`） | cicd-spans §Pipeline run |
| 单个检查项 | 子 span；`cicd.pipeline.task.name` = check 名；`cicd.pipeline.task.run.id` = check 名（同 run 内唯一）；`cicd.pipeline.task.run.result` = `success`/`failure`；失败时 `error.type` + 现有 `message` 作为事件/属性 | cicd-spans §Pipeline task run |
| 产出方标识 | `resource.attributes`：`service.name`=`harness-init`、`service.version` | resource semconv 惯例（同上规范引用） |
| 代码修订（可选） | `vcs.repository.ref.revision`（有 git 时） | CI/CD SIG 博客（§1.2 来源） |
| 时间 | `startTimeUnixNano` / `endTimeUnixNano`（OTLP 字段名） | OTLP proto 消息字段 |
| 版本声明 | 顶层 `semconvVersion`（如 `v1.31.0`）或 `schemaUrl` | OTLP/semconv 的 schema_url 惯例（opentelemetry.io instrumentation libraries 文档） |

- **明确不采用**：完整 `opentelemetry-sdk`/OTLP exporter（依赖成本见 §2，与零依赖定位冲突）；
  以及纯自造字段（放弃与数据飞轮下游工具互操作的可能）。
- **风险提示**：`cicd.*` 语义约定为 Release Candidate，需把字段名集中为常量并在
  CHANGELOG/SPEC 记录所对齐的 semconv 版本，以便跟进修订。

### 4.2 与"数据飞轮"目标的匹配度

一手调研文档（`docs/plans/2026-09-01-harness-engineering-research.md`）的相关锚点：
- §6.2 N3："`validate --json` + 落盘 `.harness/trace/validate-<ts>.json`（在 `ValidationResult`
  之上加序列化，改动极小）"——本方案正是其落地形态；
- 机制 #18（对照表）：trace 落盘的定位是"验证失败结构化存储"，为 Critic→Refiner 自我进化回路
  （机制 #19）与"失败记忆"（机制 #11/#17）供数；一手出处为 Qoder（2.8 §10）"每次验证失败都被
  结构化地保存到 `harness/trace/failures/`，Critic 脚本定期分析这些记录，找出模式和根因"。

匹配度评估：
1. **聚合通过率**：`cicd.pipeline.task.run.result` 是低基数枚举，Critic 脚本用 `json.load` +
   按字段分组即可算出各检查项通过率/失败分布——与普通 JSON 无障碍，与完整 OTLP-JSON 相比
   反而更省解析成本（无需理解 protobuf 嵌套与 base64/hex 编码）；
2. **失败分布**：失败项携带 `error.type`（低基数，规范要求"SHOULD be predictable"），
   天然支持按错误类聚类的失败模式分析；
3. **跨仓库可比性**：语义约定字段名使不同项目（乃至未来的生态工具 harness-lint）产出的
   trace 可直接合并统计，这是自造格式做不到的；
4. **升级路径**：若飞轮后续接入真实后端（collector/SigNoz/Jaeger），文件结构已对齐
   OTLP-JSON 子集，可平滑切换为在线导出（届时再引入 `opentelemetry-exporter-otlp-proto-http`
   纯 Python 变体，仍可避开 grpcio）。

## 5. 来源清单

一手：
- OTel《Signals》https://opentelemetry.io/docs/concepts/signals/
- OTel CI/CD semconv 索引与 spans 规范：
  https://opentelemetry.io/docs/specs/semconv/cicd/ 、
  https://opentelemetry.io/docs/specs/semconv/cicd/cicd-spans/ （全文已逐字核对并存档）
- OTLP 规范（JSON Protobuf Encoding）：https://opentelemetry.io/docs/specs/otlp/
- PyPI JSON API（1.44.0 元数据）：`opentelemetry-api`、`opentelemetry-sdk`、
  `opentelemetry-exporter-otlp`、`opentelemetry-exporter-otlp-proto-grpc`、`pytest-otel` 2.4.0
- Bazel《JSON trace profile》 https://bazel.build/advanced/performance/json-trace-profile
- Honeycomb《Monitoring Unit Tests with OpenTelemetry》
  https://www.honeycomb.io/blog/monitoring-unit-tests-opentelemetry
- Dash0《Enhancing GitHub Actions Observability with OpenTelemetry Tracing》
  https://www.dash0.com/guides/github-actions-observability-opentelemetry-tracing
- Elastic CI/CD 文档（pytest-otel 官方收录描述）
  https://www.elastic.co/docs/solutions/observability/cicd

准一手/多源一致转述：
- CNCF 博客《OpenTelemetry Is Expanding Into CI/CD Observability》（2024-11-04）中译：
  https://cloud.tencent.com/developer/article/2505754
- Thoth（opentelemetry-shell/github）项目介绍：
  https://m.blog.csdn.net/weixin_30591519/article/details/160485976
- Jenkins OpenTelemetry 插件生态综述（含 otel-cli、pytest-otel 并列）：
  https://m.blog.csdn.net/gitblog_00669/article/details/147291523

仓库内部上下文：
- `docs/plans/2026-09-01-harness-engineering-research.md` §6.2 N3、机制对照表 #18/#19、2.8 §10
- `src/harness_init/validators/_base.py`（`ValidationResult` 现有结构）
