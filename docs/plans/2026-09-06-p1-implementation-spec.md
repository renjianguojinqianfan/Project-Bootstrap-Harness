# PBH P1 实施 Spec（机械执法层 + 可观测性最小闭环）

> **Wayfinder 地图 [#1](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/1) 终点交付物** — 决策完备，可直接交 `/implement` 或 `/to-tickets`
> **综合决议**：[#2](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/2) / [#3](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/3) / [#4](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/4) / [#5](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/5) / [#6](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/6) / [#7](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/7) / [#8](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/8) / [#10](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/10)
> **日期**：2026-09-06
> **纪律**：对标 / 市场只作旁证，裁决以 PBH 三问 + `docs/design.md` 边界为准；三问只否决不背书；每条新规则带生效 / 退役条件

---

## 0. 一页纸总览

**P1 目标**：给生成项目补上「机械执法层 + 可观测性最小闭环」，把 PBH 定位内分从 41 拉到 65（对标报告 §6 P1 目标）。全部产物皆**静态播种物**（目录 / 脚本 / make target / AGENTS.md 条款 / JSON schema），PBH 核心自己从不运行它们。

**P1 交付物一览**：

| # | 交付物 | 来源 | 落点 |
|---|--------|------|------|
| 1 | 分层依赖 lint（grimp + `scripts/lint_deps.py` + `check-deps` target） | #2 #4 | 生成项目 |
| 2 | 状态机推进契约（`progress.json.stage_history` + `scripts/stage.py`） | #5 | 生成项目 |
| 3 | `validate --json` + `--trace` 落盘（OTel 语义字段 JSON） | #3 #6 | 核心 |
| 4 | Secret 扫描门禁（`scripts/scan_secrets.py` + `check-secrets` target） | #7 | 生成项目 |
| 5 | 端到端验证插座（`scripts/verify/` + `make verify-e2e` + CI 可选 job） | #8 | 生成项目 |
| 6 | 事前问神谕（`scripts/verify_action.py` import 半边） | #8 D4 | 生成项目 |
| 7 | 失败侧静态指路牌（每 target 一条 `\|\| echo`） | #8 D6 | 生成项目 |
| 8 | `validate --json` 计数汇总 `summary` 块 + stdout 一行「通过 X/Y」 | #10 D3 | 核心 |
| 9 | 脚本落点统一（`.harness/*.py` → `scripts/*.py`） | #8 D3 移交 | 生成项目 |
| 10 | `docs/design.md` §2 / §4.1 口径修正 | #10 移交 | 本仓库 |

**明确不做**（Out of scope，继承自 #1 地图 + #8 / #10 决议）：

- 合规评分 / 评级 / 徽章 / 看板 / 可视化（#10 D1 永久移出 PBH）
- harness-lint / harness-agent 自建（#10 D2 退役为生态）
- Agent 运行时逻辑（`design.md` §2 红线）
- `create-file` 事前问（#8 D4 缓议进雾区）
- `.harness/permissions.md` 项目风险声明（#7 缓议进雾区）
- `make add-verify`（#8 D5 砍掉）
- PBH 播种 Agent Skills（#1 地图 Out of scope）

**第 0 阶段前置**：P0 正确性缺陷必须先修完（IDE 适配渲染、模板 `make verify` 全绿、`.pre-commit-config.yaml` 合法化等），否则 P1 播种物会种进「开箱即坏」的项目。P0 不进本地图，但**必须先于 P1 阶段 A 完成**。

### 0.1 用户故事（User Stories）

> 4 类 actor：脚手架用户（使用 `harness-init init` 的开发者）、AI Agent（在生成项目中工作的 coding agent）、CI 管线（自动化门禁）、生态消费方（SARIF / trace 下游工具）。

1. As a **脚手架用户**, I want 生成的项目自带分层依赖门禁（`make check-deps`）, so that AI Agent 不能悄悄引入违规跨层 import 而不被发现。
2. As a **脚手架用户**, I want 生成的项目自带 secret 扫描门禁（`make check-secrets`）, so that 硬编码凭据在 `make verify` 阶段即被拦截，不进入 git 历史。
3. As a **脚手架用户**, I want 生成的项目自带状态机推进脚本（`scripts/stage.py`）, so that AI Agent 的阶段推进有前馈拦截，跳级/倒退在门口被拒绝。
4. As a **脚手架用户**, I want `harness-init validate --json` 输出机器可读结果, so that 我可以在 CI 管线中程序化消费合规状态。
5. As a **脚手架用户**, I want 生成的项目自带端到端验证插座（`scripts/verify/` + `make verify-e2e`）, so that 我可以逐步把核心用户路径编码为可执行验证，而非只靠 lint+test。
6. As a **脚手架用户**, I want 所有播种物可拆卸（删除即退役、零残留）, so that 我不被锁死在 PBH 的机制选择上。
7. As an **AI Agent**, I want 分层违规报错携带「违反规则 + 原因 + Fix:」三段式, so that 我不需要猜测修复方向，一次报错即一次教学。
8. As an **AI Agent**, I want 事前问神谕（`scripts/verify_action.py`）在跨包 import 前给我 VALID/INVALID 判定, so that 守规比违规便宜（2 次查询 vs 10 次事后修复）。
9. As an **AI Agent**, I want `make verify` 失败时每个 target 只打印对应那条指路牌（含 AGENTS.md 条款引用）, so that 我能快速定位失败根因，不被无关信息淹没。
10. As an **AI Agent**, I want `progress.json.stage_history` 追加式账本, so that 我的阶段推进历史不可篡改，审计痕迹完整。
11. As a **CI 管线**, I want `validate --json` 输出含 `summary:{total, passed, failed}` 计数块, so that 我可以在 CI dashboard 上展示通过率趋势，无需自建评分逻辑。
12. As a **CI 管线**, I want `--trace` 落盘 `.harness/trace/validate-<ts>.json`（OTel 语义字段、自轮转 10 份）, so that 门禁运行历史可追溯、可聚合。
13. As a **CI 管线**, I want `make verify-e2e` 作为独立 target（不拖慢 `make verify` 快门禁）, so that 重验证可以在 CI 环境中起活服务跑端到端，本地快门禁仍 < 5s。
14. As an **生态消费方**, I want `validate --json` 字段可无损映射 SARIF result（`spec_ref` → `ruleId`、`severity` → `level`、`fix` → `fixes[]`）, so that GitHub Code Scanning / sverklo 等现成工具可直接渲染，PBH 不需自建可视化。
15. As an **生态消费方**, I want `format_version` 字段标注 schema 版本（pip 式 `0.x` 试行 → `1.0` 冻结）, so that 我可以判断兼容性、忽略未知字段。

---

## 1. 第 0 阶段：P0 正确性缺陷修复清单（既定前提）

**来源**：`PBH-harness-engineering-对标报告.md` §5 P0 表 + §6 P0 路线图 + `docs/plans/2026-09-01-harness-engineering-research.md` §6.1 N1 + `docs/plans/v1.1源码审查与问题定位报告.md`。

> **注**：对标报告 §5 P0 表在源 markdown 中部分单元格为空（渲染问题），实施时以本清单 + 对标报告 §5 原文 + v1.1 源码审查报告交叉核对；本清单为 P1 开工前必须闭环的最小集。

| P0# | 问题 | 位置 | 验收 |
|-----|------|------|------|
| P0-1 | AGENTS.md / CLAUDE.md / `docs/PROJECT_MAP.md` 中 `{project_type}` 占位未被替换（v1.1 源码审查 B1 确认的 3 个文件） | `templates/cli/AGENTS.md` / `CLAUDE.md` / `docs/PROJECT_MAP.md`；`_utils.py` 替换字典 | `harness-init x -t lib --ide=claude` 生成的 CLAUDE.md `Type:` 字段显示 `lib` 而非 `{project_type}` |
| P0-2 | 4 模板 × 2 模式（full / quick）并非全部 `make verify` 通过；`templates/notebook/pyproject.toml` 等有缺陷 | `templates/{cli,lib,web,notebook}/` | 4 模板 × 2 模式共 8 组合全部生成后 `make verify` 绿 |
| P0-3 | `.pre-commit-config.yaml` 被注释掉或非法 | `templates/common/.pre-commit-config.yaml` | 解注释后 `pre-commit run --all-files` 通过；或明确删除并在 README 说明 |
| P0-4 | 旧版角色残留（Planner / Generator / Evaluator）与 v1.1「不定义角色」定位冲突 | `templates/cli/.cursorrules` / `CLAUDE.md` | 全文搜无 `Planner` / `Generator` / `Evaluator` 角色定义 |
| P0-5 | `opencode.yaml` 硬编码 `claude-3-5-sonnet` + 4 个第三方 skills，随模板分发且无版本锁定 | `templates/cli/opencode.yaml` | 删除硬编码模型与第三方 skills 段；或提供合法版本 + 测试 |
| P0-6 | 模板 `docs/context.md` / `PROJECT_MAP.md` 仍引用已删除目录（`agents/` / `harness/` / `tools/`） | `templates/common/docs/` | 引用与实际目录一致 |
| P0-7 | 根 Makefile 与模板 Makefile 的 lint 范围不一致（根只 lint `src/`，模板 lint `src/ tests/`） | `Makefile` vs `templates/common/Makefile` | 统一为 `src/ tests/`（或明确记入家规） |
| P0-8 | `configs/dev.yaml` 残留 `runner / evaluator / state` 配置（Agent 运行时残骸） | `templates/common/configs/dev.yaml` | 删除或替换为与「只播种」定位一致的字段 |

**P0 阶段验收**：

- 全部 8 项闭环；
- `harness-init x -t {cli,lib,web,notebook}` × `{full,quick}` 共 8 组合，每组生成后 `cd` 进项目 `make verify` 全绿；
- 本仓库 `make verify` 绿、`pytest tests/` 覆盖率 ≥ 85%。

**P0 不进本地图**：P0 修复属「既定前提」（#1 地图 Notes 已声明），不在 Wayfinder #1 票据链上，但**必须先于 P1 阶段 A 完成**。

---

## 2. 各票决议全文（含生效 / 退役条件）

### 2.1 #2 — W01 分层依赖 lint 执行工具选型（research）

**决议**：选 **grimp + ~50 行胶水脚本 `scripts/lint_deps.py`**。

**理由**：

- grimp 提供一等分层 API `find_illegal_dependencies_for_layers(layers, containers)`，与 `.harness/layers.yaml` 字段一一对应，可声明式直驱；
- 纯静态（源码级解析，不运行代码），实测增量 < 1 秒；
- 报错文案由胶水层自控，可注入「违规 + 原因 + Fix:」三段式；
- 拆卸零残留：删除脚本 + YAML + dev 依赖即退役。

**备选否决**：

- `import-linter`：语义相同但配置格式绑定、报错不可定制、拆卸有残留；
- `deptry`：查依赖声明卫生，不适用分层；
- `ruff TID251 banned-api`：仅全局黑名单，无法表达上下文相关分层，只能作补充。

**`.harness/layers.yaml` 字段（W01 调研草案 → W03 采纳为最简版）**：

- `version`
- `root_packages`
- `options`（`exclude_type_checking_imports: true` 默认开启）
- `contracts[]`（`name`、`containers`、`layers` 高→低序、同层 `siblings.independent`）
- `ignore[]`（豁免必须带 `reason`）

**生效条件**：用户填 `layers.yaml.contracts` 后 `make check-deps` 开始产出真判定；contracts 为空时恒 VALID（与 W03「机制先种、规则后填」一致）。

**退役条件**：删除 `scripts/lint_deps.py` + `.harness/layers.yaml` + 模板 dev 依赖 `grimp` + Makefile `check-deps` target，零残留。

**实现细节**：

- grimp 要求被分析包可定位；胶水脚本用 `sys.path` 注入 `src/`，无需先 editable 安装；
- grimp 缺失时硬失败并给出明确安装指引；
- 间接链违规由 grimp 语义覆盖；`ignore` 豁免由胶水层过滤。

**详细论证**：`docs/plans/wayfinder/research/W01-分层lint工具选型.md`。

---

### 2.2 #3 — W02 验证事件 trace 格式调研（OpenTelemetry 对齐，research）

**决议**：采「**OTel 语义约定字段 + 普通 JSON（OTLP-JSON 结构子集）**，零新增依赖」。

**建模**：一次 `validate` 运行 = 1 个根 Span + 每检查项 1 个子 Span。

**字段**：直接复用 OTel CI/CD 语义约定（semconv v1.27.0+，Release Candidate）：

- `cicd.pipeline.result`
- `cicd.pipeline.task.run.result`
- `error.type`

**否决完整 SDK 的理由**：`opentelemetry-sdk` + OTLP exporter 会引入 grpcio / protobuf 等重型二进制依赖，与零依赖播种器定位冲突；行业先例选完整栈皆为在线导出场景。

**规范兼容性**：OTLP 官方定义 JSON Protobuf Encoding 且接收端 MUST 忽略未知字段；结构对齐后可平滑升级为合法 OTLP/HTTP JSON。

**数据飞轮匹配**：低基数枚举字段支持通过率 / 失败分布聚合。

**生效条件**：随 #6 的 `validate --json` 一并生效。

**退役条件**：删除 `--json` 输出 + `--trace` 落盘逻辑即退役；无新依赖需清理。

**详细论证**：`docs/plans/wayfinder/research/W02-验证事件trace格式.md`。

---

### 2.3 #4 — W03 分层声明协议设计（`.harness/layers.yaml`，grilling）

**决议**（2026-09-01 访谈拍板）：

1. **Schema = 最简版**：采纳 W01 调研草案原样——`version` / `root_packages` / `options` / `contracts[]` / `ignore[]`。**不加生效 / 退役字段**——可拆卸性靠「整个删除 layers.yaml + 脚本 + dev 依赖」实现，零残留即退役。

2. **门禁 = 维持原门禁**：模板 Makefile 新增 `check-deps` target，`verify: lint format-check check-deps test`。分层检查为纯静态扫描（实测增量 < 1 秒，慢的是测试），**不做快慢拆分**。

3. **执行器 = grimp + 胶水**（`scripts/lint_deps.py`，~50 行）：读 `layers.yaml` → grimp 建图 → `find_illegal_dependencies_for_layers` → 报错输出「违反规则 + 原因 + Fix:」三段式（正向修复提示注入点）。

4. **播种形态 = 机制 + 说明书，不做分类型预置**（用户明确要求通用化，不替项目猜结构）：
   - `templates/common/.harness/layers.yaml`：contracts 留空 + 注释示例（占位 `{package_name}`）；
   - `templates/common/scripts/lint_deps.py` 播种 + 模板 dev 依赖加 `grimp`；
   - AGENTS.md 模板增补条款：「项目结构成型后，Agent MUST 起草 `.harness/layers.yaml` 并使 `make verify` 通过」。

5. **SPEC 条款措辞**：留给雾区 SPEC v2.1 票据；本票据只定能力接口（`layers.yaml` 声明 + `check-deps` 入口）。

**生效条件**：出生即生效（种子自带、`make verify` 含 `check-deps`、contracts 空时恒 VALID 不阻断）。

**退役条件**：删除 `.harness/layers.yaml` + `scripts/lint_deps.py` + Makefile `check-deps` 行 + 模板 dev 依赖 `grimp` + AGENTS.md 相应条款，零残留。

---

### 2.4 #5 — W04 状态机推进契约设计（`progress.json` + 检查点，grilling）

**决议**（2026-09-01 访谈拍板）：

1. **留痕 = 追加式账本**：`progress.json` 新增 `stage_history` 数组（只追加，不删改），每条 `{stage, at}`（`at` 为 ISO 8601 时间戳）。账本末条必须与 `current_stage` 一致；`validate` 事后校验该一致性，防手改绕过。

2. **门房形态 = 独立小脚本**：播种 `scripts/stage.py`（约 50 行）**[编注：#5 原文决议落 `.harness/stage.py`，经 #8 D3 收敛迁移至 `scripts/`，见本 spec §5]** 进生成项目，调用方式 `python scripts/stage.py <stage>`。职责严格限于「校验转移合法性 → 落盘 → 追加账本 → 打印结果」，不含任何执行逻辑；非法转移在门口直接拒绝（前馈拦截，不靠事后罚款）。

3. **门禁严格度 = 严格单向顺序**：`init → plan → execute → evaluate → done`，跳级拒绝、倒退拒绝。两条叠加规则：
   - **唯一例外**：允许从任意阶段退回 `plan`（覆盖执行中反复重规划的真实需求，折返轨迹如实记录在账本中）；
   - 进入 `execute` 要求 `plans` 字段非空（没图纸不许动工）。

4. **检查点 = git 零接触**：不打 tag、不建分支、不提示 commit——git 存档点完全由用户自理。`stage_history` 账本是唯一内置审计痕迹，回滚辅助止于「让你知道退到哪」。理由（用户）：git 不应被播种物污染；真实开发不总是从计划文档先 commit 开始，且实施中常多次修改计划。

5. **衔接**：扩展 `validators/progress_json.py` 新增 `stage_history` 校验（存在性、末条与 `current_stage` 一致、相邻条目符合转移规则）；**存量项目缺该字段时降级为警告而非错误**。

**生效条件**：出生即生效（种子自带 `scripts/stage.py`、`progress.json` 模板含 `stage_history: []`、`validators/progress_json.py` 已扩展）。

**退役条件**：删除 `scripts/stage.py` + `progress.json.stage_history` 字段 + `validators/progress_json.py` 相应校验分支，零残留。

---

### 2.5 #6 — W05 `validate --json` 输出 schema 与 trace 落盘设计（grilling）

**决议**（2026-09-01 访谈拍板 + 行业共识调研，笔记：`docs/plans/wayfinder/research/W05-行业机器可读输出共识补充调研.md`）：

**行业共识直接落定（未再访谈）**：

1. **stdout 双轨**：默认维持人可读输出不变，`--json` 显式切机器格式——6 个独立工具（eslint / ruff / pytest-json-report / pip / terraform / semgrep）一致惯例，无反例。
2. **修复提示 = 独立结构化 `fix` 字段**，`message` 只承载人类可读描述（SARIF `fixes[]`、ruff `fix` 对象均如此）。
3. **严重度**：内部模型按 SARIF 3 级词表建模（`note` / `warning` / `error`），当前实际只产出 `error` / `warning` 两级。

**访谈拍板**：

4. **字段改动**：`ValidationResult{check, passed, message}` 之上增 `severity`、`fix` 两字段；另加 `spec_ref` 条款引用字段，落实 `design.md` §4.2 归因锚定原则（每条输出可追溯到 SPEC / AGENTS.md 条款）。

5. **JSON 骨架**：按 #3 定案——1 根 Span + 每检查项 1 子 Span，OTel CI/CD 语义字段，普通 JSON 零依赖；顶层带 `format_version`（semver）。

6. **SARIF 接口**：**不建导出器**，但字段设计保证可无损映射为 SARIF result（ruff 已原生 `--output-format sarif`，生态成熟）——未来接入 GitHub Code Scanning 时零返工。

7. **落盘**：显式 `--trace` 开关才落盘（结果报告类行业共识 = 显式开）；文件名 `.harness/trace/validate-<ts>.json` 时间戳累积，工具自轮转保留最近 10 份（Bazel `--profiles_to_retain` 先例）；默认不落盘。trace 是 CI 式门禁运行记录，**不是 Agent 行为监控**（`design.md` §2 边界）。

8. **doctor**：输出同款 schema 结构化结果，诊断文字进 `message` / `fix` 字段。

9. **稳定性承诺（用户裁决，选 A）**：pip 式——`format_version` 出生即标 `0.x`「实验性」，观察一个 minor 版本后 bump `1.0` 并宣布冻结；承诺措辞照 Terraform（minor 只增字段、消费方忽略未知字段，OTLP 规范背书）。**注：此为用户对 `design.md` §4.3「出生即冻结」先例的显式破例**，理由：当前零消费者，保留一次免费改字段机会。

**生效条件**：出生即生效（`validate --json` / `--trace` 为新增可选开关，默认行为不变；存量 `ValidationResult` 字段保留）。

**退役条件**：删除 `--json` / `--trace` 参数 + `severity` / `fix` / `spec_ref` / `format_version` 字段 + `.harness/trace/` 目录，零残留（无新依赖）。

---

### 2.6 #7 — W06 安全护栏播种设计（权限分级 + secret 扫描，grilling）

**决议**（2026-09-01 访谈拍板，证据驱动；笔记：`docs/plans/wayfinder/research/W06-主流Agent权限与secret扫描现状调研.md`）：

**过程说明**：访谈中用户提出根本性质疑——「权限系统和安全扫描大部分 Agent（opencode / trae / qoder / codex / workbuddy 等）都已自带，这些不应该是 Agent 自己做的事吗？」两轮派研究子代理取证（七家工具逐一核对官方一手来源；二轮复核修正了内置扫描现状）。裁决全部基于证据。

**调研事实基线**：

- 七家均有运行时权限机制；四家支持项目内声明式权限文件（`.claude/settings.json` / `opencode.json` / `.qoder/settings.json` / `.cursor/cli.json`），格式互不相通、各只读自己的；
- **无一家**提供「项目级风险事实声明」（生产库位置、禁区目录、保密数据等）的专门落点；行业公认落点是 AGENTS.md 的 Security considerations 章节（agents.md 标准明确推荐）；各家官方一致承认「文档只塑造行为，不构成权限边界」；
- 内置代码安全扫描已成头部厂商趋势（Qoder L1-L3、Claude Code `/security-review`、Codex Security、Cursor Bugbot），但各家均自定位「纵深防御、不替代既有机械扫描器」；commit 钩 / CI / push protection 等确定性防线独立存在。

**拍板结论**：

1. **项目风险声明（`.harness/permissions.md`）= 缓议，不入雾区票据**：用户裁决——无法保证 Agent 遵守、过于复杂，暂时不再议。证据上该落点是真实空缺（补空缺不冲突），但价值未锐化到可拍板，**记入地图「Not yet specified」**。分型预置与 AGENTS.md 安全措辞两个子项随本项一并缓议。

2. **secret 扫描 = 播种为 make 门禁**：
   - 播种 `scripts/scan_secrets.py` 小脚本（纯 Python，基于 detect-secrets）**[编注：#7 原文决议落 `.harness/scan_secrets.py`，经 #8 D3 收敛迁移至 `scripts/`，见本 spec §5]** + 模板 Makefile 增 `check-secrets` target，进 `make verify`；
   - **不用 pre-commit 形态**：生效需 `pre-commit install` 写入 `.git/hooks`，撞 W04 拍板的「git 零接触」家规，且种子依赖外部 hook 仓库；
   - 与先例同构：照 W03（grimp + `check-deps`）模式——播种机制 + 进门禁 + 模板加一个 dev 依赖；
   - 可拆卸：删除脚本 + target + dev 依赖即退役，零残留。

3. **PBH 三问核验（拍板前逐条过）**：
   - ①不干预 AI 思考——模式匹配扫描代码产物，与 lint / test 同物种；
   - ②不降低「没有 PBH 的痛苦」——与 W03 grimp 门禁先例同构，是播种环境标准而非安慰功能；
   - ③进 `make verify` 即阻断性门禁，让协议更难被忽略。

**生效条件**：出生即生效（种子自带、`make verify` 含 `check-secrets`、模板 dev 依赖含 `detect-secrets`）。

**退役条件**：删除 `scripts/scan_secrets.py` + Makefile `check-secrets` 行 + 模板 dev 依赖 `detect-secrets`，零残留。

---

### 2.7 #8 — W07 预验证脚本骨架设计（`scripts/verify/` + `make add-verify`，grilling）

**决议**（2026-09-06 访谈拍板；用户裁定 D4 = 折中）：

**过程**：本票两个并行会话各出一份草案，比对后合流为单一正本，经多轮通俗化访谈（定位澄清 → 快门禁 vs 重验证 → D4 三选一 → 「随模型能力提升是否还必要」的折旧论证）逐项拍板。判据纪律：**对标只作旁证，裁决以 PBH 三问 + `design.md` 边界为准；三问只否决不背书**（中性项直说不欠人情）。

**定位镜头（贯穿全票）**：PBH 不做 agent 运行时，但全部产物是「给 agent 用的环境」。本票所有产物皆静态物（目录 / 脚本 / make target / AGENTS.md 条款），PBH 自己从不运行它们。

#### 八项决策

**D1 快慢分离**：`make verify` 一字不改（守 < 5s 快门禁 + 「生成项目开箱即过」招牌）；重验证另设 `make verify-e2e` 插座。绑 evaluate 阶段**仅为 AGENTS.md 文字条款，不改 `scripts/stage.py`**（W04 已限其职责，硬塞 = 擦碰运行时边界）。`verify-e2e` 的真正归宿是 **CI**（`templates/common/.github/workflows/` 加可选 job）——本地快门禁容不下重验证，CI 能起活环境；「独立 target 会被忽略」的顾虑由此消解。

**D2 快检查归 pytest，不种可执行分型预置**：`--help` 冒烟等 headless 快检查归 `tests/`（已被 `make verify` 的 test 覆盖），不进 `scripts/verify/`。分型可执行预置否决（违 W03 / W06「不猜结构」、web / notebook 易猜错 = 开箱即坏）。指南给四型各一段**注释态范文**（cli `--help` / web 起服务 + 健康检查 / lib import + 版本 / notebook 执行一格），以说明书形态兑现票据「4 类型预置」ask。

**D3 落点家规**：**可执行种子脚本 → `scripts/`；协议数据 / 文档 → `.harness/`**。`verify_action.py` 落 `scripts/`（与 #4 `lint_deps.py` 共享 grimp 图，同侧合理）。历史不一致（W04 `stage.py`、W06 `scan_secrets.py` 在 `.harness/`）**不重开已关闭的 #5 / #7**，记入本决议**显式移交 #9** 收敛，并给 #9 推荐终局：「所有 PBH 机制脚本统一到 `scripts/`，`.harness/` 只留纯数据 / 文档」。**本 spec §5 落实该收敛**。

**D4 事前问 = 折中（用户裁定）**：种 `scripts/verify_action.py`（~40 行，复用 #4 `layers.yaml` + grimp，**零新依赖**），**只实现 import 查询**（`--action "import A from B"` → 图背书精确判定 → VALID / INVALID + Rule 引用 + Fix）。

- **`create-file` 查询缓议进雾区**：其判定天生启发式、硬编码白名单会猜结构（违 W03）、更贴「塑造 agent 行为」边，且与 import 半边同折旧。
- **软触发**：AGENTS.md 写「跨包 import 前先跑」，**不接进 `make verify`**（门禁无法验证「问过没有」，硬塞变行为监控）。
- **hook-ready 契约**：退出码 VALID=0 / INVALID=1 + 单行原因 + Fix，按「可被 PreToolUse 类 hook 直接消费」设计；README 一句指路；**PBH 不代装任何 hook**（代装 = 进 Agent 运行时 `design.md` §1 + 绑死特定工具 #7，两条红线）。想要强拦截的用户自接插座。
- **如实标注（哑火）**：种子默认态 `layers.yaml` contracts 为空 → import 查询恒 VALID；价值待用户填 `layers.yaml` 后兑现（与 W03「机制先种、规则后填」一致）。
- **诚实定位**：事前问**不是「管得住」的防线**（软触发，AI 可不问）；管得住的是 D1 / #4 的事后查硬门禁。它的价值是「让守规比违规便宜」（Qoder 事后 10 次 vs 事前 2 次），且是**会折旧的 harness 资产**（模型越强边际价值越低）——故只种最小可拆卸版 + 附退役日期。

**D5 砍掉 `make add-verify`**：其作用 = 「复制文件改名」，AI 顺手能干，为一次性动作建机制 = 投机式扩展；占位脚本本身即模板，复制改名写进指南。**票据标题的 `add-verify` 交付物据此收窄、不落地**。

**D6 失败侧指路牌（雾区「lint 报错注入修复指令」毕业于此）**：静态指路牌，做成**「每 target 一条」**（各 `check-*` 挂自己的 `|| echo`，失败只打印对应那条），不解析报错（跨工具版本维护地狱）；每条落到 AGENTS.md / SPEC 条款（归因锚定，对接 #6 `spec_ref`）。分层三段式报错已在 #4 定案，本票只管验证失败侧入口。

**D7 `verify-e2e` 用 pytest 收编**：`make verify-e2e` = `pytest scripts/verify/`（零新机制、跨平台、不写 shell 循环）。种子自带 **skip 状态占位测试**（防 pytest 零收集退出码非 0）；且 **skip 默认静默** → target 跑 `pytest scripts/verify/ -rs`（或末尾 echo 提醒）让「未编码用户路径」**可见**，堵死「静默假绿」。

**D8 生效 / 退役（可拆卸）**：出生即生效（种子自带、`make verify` 未改动、`verify-e2e` skip 占位开箱即过）。**退役 = 零残留删除**：删 `scripts/verify/` + `scripts/verify_action.py` + Makefile 增行（`verify-e2e`、per-target 兜底）+ AGENTS.md 相应条款；无新增依赖需清理（grimp 归 #4）、无 git hook 残留。**退役触发条件（折旧资产 sunset）**：当模型能稳定遵守 `layers.yaml`、事前问神谕不再产生价值时，删除 D4 那半边。

#### PBH 三问终验（逐条，只否决不背书）

- **D1 / D2 / D6 / D7**：①不干预思考 ②不削弱自己 ③更难忽略 → ✅
- **D3 / D5**：三问**中性**（代码卫生 / 简洁优先判断，三问未参与，不欠人情）
- **D4（折中）**：①**不越界**（被动神谕只答 import 结构事实，与「问 lint」同物种，不拦不重试）②**不削弱**（抬门槛，逼动手前自查）③**不完全过**（软触发，AI 可不问）——真实价值 = 让守规比违规便宜，非「更难忽略」。诚实标为全票最弱环；用户在知情（含折旧论证）后裁定保留最小版。

---

### 2.8 #10 — W09 合规评分报告输出归属决策（类 Lighthouse，grilling）

**决议**（2026-09-06 访谈拍板；用户裁定 Q4 = 加、harness-lint 退役）：

**过程**：本票由 #6 雾区毕业。首轮用「物业 / 门禁 + 四层楼（事实 / 汇总 / 评判 / 可视化）」通俗化拆解 A / B / C 三选项代价；用户中途投入关键新事实——「不打算自建 harness-lint，市面上已有更完整的 agent-lint」，据此重判；派生 web 调研证实市场已 commodity 化通用就绪度评分。判据纪律沿 #8：**对标 / 市场只作旁证，裁决以 PBH 三问 + `design.md` 边界为准；三问只否决不背书**。

**证据基线（市场调研，2026-09-06）**：

- **Factory Agent Readiness**（开源 `superduck-ai/agent-readiness`）：9 支柱 / 82 检查项，出 JSON + HTML Dashboard，每项给「具体得分 + rationale」，产物进 `.agent-readiness/`；口号 "The agent is not broken. The environment is."（与 PBH 同源）。
- **sverklo**：「Lint for AI-readiness」，A–F 健康评级 + README 徽章 + 六种输出（markdown / html / json / **sarif** / csv / badge）。
- **Agent Ready（Codex 插件）**：就绪度扫描 + 总体评分 + 整改优先级。
- **关键区分**：这些是「通用 agent 就绪度」工具，读不懂 `.harness/trace/`、不认 PBH-SPEC，给的是「通用就绪度分」，**给不出「PBH 协议专属合规分」**（`layers.yaml` contracts / `progress.json` 状态机 / AGENTS.md 章节 / `spec_ref` 归因只有 PBH 自己懂）。

#### 三项决策

**D1 合规评分报告（Lighthouse 式加权评分 / 评级 / 徽章 / 看板 / 可视化）= 永久移出 PBH 范围**。定性为「市场 commodity，协议层不进」，**非甩给未来的 harness-lint**。锚：PBH = 协议层（对标 JUnit XML）——JUnit XML 自带 `<testsuite tests/failures/errors/skipped>` **计数（事实）**，但**绝不算加权分 / 评级**，那是 CI 看板（生态）的活。

**D2 harness-lint 退役（用户裁定：不自建）**，三条理由：

- 通用那半市场已 commodity 化（Factory / sverklo），重造 = 重复造轮子；
- PBH 专属「发现」层已由 `validate` 覆盖（+ #6 结构化 SARIF-mappable 输出），harness-lint 想加的只剩「渲染」；
- 渲染 / 看板 = 「消费档案的分析器」，踩 `design.md` 红线（架构定位记忆：「坚决不做任何消费档案的代码（看板 / 分析器）」）。
- harness-lint 概念降级为「生态 / 第三方未来可在 PBH 的 SARIF-mappable trace 上自建」，**非 PBH 承诺 / P1 交付物**。**harness-agent（自动修复）同理**——是 runtime、「干预 AI 思考」正中心，本就在 `design.md` §2「坚决不做」里。整个「生态三角」从来是生态的事。
- **回头建的触发条件（折旧纪律）**：当「PBH 专属合规可视化」出现真实、反复需求，且市场通用工具 + SARIF 桥确实接不住时，再作为**独立项目**（非 P1、非核心）议。当前无此证据。

**D3 PBH 核心承载 = 协议专属事实 + 计数汇总（JUnit testsuite 式）**。Q4 用户裁定「加」：

- `validate --json` 增顶层 `summary:{total, passed, failed}` 块——复用 #6 的 `severity` / `spec_ref` / `format_version`，是 #6 结构化结果的**无损计数汇总**（#3 早定 trace 低基数字段支持「通过率 / 失败分布聚合」）；
- stdout 末尾增一行「通过 X/Y」（人可读，与现有逐项 ✅ / ❌ 同物种）；
- `doctor` 同款 schema（沿 #6）；
- **守死边界**：「只计数、不加权、不评级、不画图」——一旦开始定权重 / 百分制 / 评级即滑向被否决的 D1；
- **可拆卸**：删 `summary` 块 + 那一行 stdout 即退役，零残留（无新依赖、无新文件）。
- **生态闭环靠 SARIF 桥**：PBH 出 SARIF-mappable 事实（#6 已定），市场现成消费方（GitHub Code Scanning、sverklo 式看板）渲染，**PBH 不写 consumer 代码**。

#### PBH 三问终验（拍板前逐条，只否决不背书）

- **①干预 AI 思考？** 计数 = 事实陈述、不游戏化 → **不否决**（加权 Lighthouse 分才触发，已移出 D1）。
- **②降低「没有 PBH 的痛苦」？** 诚实标注：计数汇总**中性**（用户自己也能数勾叉，同 #8 D3 / D5 中性纪律）；但「拒不自建看板 / 评分」恰恰守住「不靠安慰性 / 展示性功能削弱自己」 → **不否决**。
- **③让协议更难被忽略？** 计数 + 失败清单 + `spec_ref` 弱正向；真正硬防线仍是 `make verify` 阻断门禁，本决策不削弱它；评分移出反而保住「难忽略靠门禁而非靠分数」 → **不否决**。
- **结论**：最终方案**无一被三问毙掉**；真正驱动力 = `design.md` §3.3 / §4.1 边界 + 架构红线「不做分析器」+ 市场 commodity 化证据。

**生效条件**：出生即生效（`validate --json` 默认含 `summary` 块；stdout 末尾「通过 X/Y」一行）。

**退役条件**：删除 `summary` 块 + stdout 那一行，零残留（无新依赖、无新文件）。

---

## 3. 实施顺序与验收标准

**编排原则**：P0 先于 P1；P1 内部按「依赖图 + 风险递增」排序；每阶段独立可交付、独立可回滚；每阶段验收含「生成项目 `make verify` 通过」+ 可观测性项「输出可解析」。

### 3.0 测试策略与 Seams

**Seam 选择**（优先复用现有 seam，不新建）：

| Seam | 位置 | 覆盖阶段 | 先例 |
|------|------|---------|------|
| 模板渲染层 | `tests/test_templates.py` | B / C / E / F | 现有 `test_init_project_creates_*` 系列 |
| Validator 单元层 | `tests/test_validation.py` | B（layers_yaml）/ C（progress_json 扩展）/ D（--json schema）/ G（summary） | 现有 `test_validate_*` / `test_doctor_*` 系列 |
| 生成项目行为层 | 手动 / CI 集成测试 | A / B / C / E / F | 8 组合（4 模板 × 2 模式）生成后 `make verify` |
| CLI 层 | `tests/test_cli.py` | D（--json / --trace 开关）/ G（stdout 一行） | 现有 `test_validate_cli_*` 系列 |

**好测试标准**：
- 只测外部行为（输出 / 退出码 / 文件存在性），不测实现细节（内部函数调用链）；
- 每个 seam 的测试独立于其他 seam（模板渲染测试不依赖 validator 逻辑）；
- 生成项目行为层测试 = 「开箱即过」招牌的守卫（任何阶段改动后 8 组合仍绿）。

**覆盖率要求**：≥ 85%（`pytest-cov` 强制执行，沿现有家规）。

### 3.1 阶段 A：P0 正确性缺陷修复（前置，不进本地图）

**内容**：第 1 节 P0-1 ~ P0-8 全部闭环。

**验收**：

- 8 组合（4 模板 × 2 模式）生成后 `make verify` 全绿；
- 本仓库 `make verify` 绿、`pytest tests/` 覆盖率 ≥ 85%；
- `harness-init x -t lib --ide=claude` 生成的 CLAUDE.md `Type:` 字段正确渲染。

**回滚**：`git reset --hard`（每 P0 项独立 commit）。

---

### 3.2 阶段 B：分层依赖 lint（W01 + W03，#2 + #4）

**内容**：

- 播种 `templates/common/.harness/layers.yaml`（最简 schema，contracts 空 + 注释示例）；
- 播种 `templates/common/scripts/lint_deps.py`（~50 行 grimp 胶水）；
- 模板 Makefile 增 `check-deps` target，`verify: lint format-check check-deps test`；
- 模板 dev 依赖加 `grimp`；
- AGENTS.md 模板增补条款「项目结构成型后，Agent MUST 起草 `.harness/layers.yaml` 并使 `make verify` 通过」；
- 核心侧：`src/harness_init/validators/` 增 `layers_yaml.py`（schema 存在性 + contracts 结构校验）。**[编注：此项非 #4 原文决议，系 spec 编者基于 PBH `validate` 职责推导的补充——#4 只定「播种进生成项目 + 模板 Makefile 增 check-deps」，未决定核心侧新增校验器。实施时可酌情裁剪；若保留，layers.yaml 不存在时 → skip（不报 error），与 contracts 空时恒 VALID 同理]**

**验收**：

- 生成项目 `make verify` 通过（contracts 空时 `check-deps` 恒 VALID）；
- 手填一条 contract 后，违规 import 触发三段式报错「违反规则 + 原因 + Fix:」；
- 删除 `layers.yaml` + `lint_deps.py` + Makefile 行 + dev 依赖后，`make verify` 仍绿（退役零残留）。

**回滚**：`git revert` 阶段 B commit。

---

### 3.3 阶段 C：状态机推进契约（W04，#5）

**内容**：

- `progress.json` 模板增 `stage_history: []` 字段；
- 播种 `templates/common/scripts/stage.py`（~50 行，**注意：原决议落 `.harness/stage.py`，本阶段按 #8 D3 收敛落 `scripts/`，见本 spec §5**）；
- 扩展 `src/harness_init/validators/progress_json.py`：校验 `stage_history` 存在性、末条与 `current_stage` 一致、相邻条目符合转移规则（存量项目缺字段时降级警告）；
- AGENTS.md 模板增补条款「阶段推进 MUST 经 `python scripts/stage.py <stage>`，禁止手改 `progress.json.current_stage`」。

**验收**：

- 生成项目 `python scripts/stage.py plan` 从 `init` 推进成功，`stage_history` 追加一条；
- `python scripts/stage.py evaluate` 从 `init` 跳级被拒绝（退出码非 0 + 明确报错）；
- `python scripts/stage.py plan` 从 `execute` 退回成功（唯一例外）；
- 进入 `execute` 时 `plans` 为空被拒绝；
- `validate` 事后校验 `stage_history` 末条与 `current_stage` 一致；
- 删除 `scripts/stage.py` + `stage_history` 字段后，`make verify` 仍绿。

**回滚**：`git revert` 阶段 C commit。

---

### 3.4 阶段 D：`validate --json` + trace 落盘（W02 + W05，#3 + #6）

**内容**：

- `ValidationResult` 增 `severity` / `fix` / `spec_ref` 字段（`src/harness_init/validators/_base.py`）；
- `validate` CLI 增 `--json` / `--trace` 开关；
- JSON 骨架：1 根 Span + 每检查项 1 子 Span，OTel CI/CD 语义字段（`cicd.pipeline.result` / `cicd.pipeline.task.run.result` / `error.type`），顶层 `format_version: "0.1.0"` **[编注：#6 只定「出生即标 0.x」，具体初始值 `0.1.0` 由本 spec 确定]**；
- `--trace` 落盘 `.harness/trace/validate-<ts>.json`，工具自轮转保留最近 10 份；
- `doctor` 同款 schema；
- stdout 双轨：默认人可读不变，`--json` 切机器格式。

**验收**：

- `harness-init validate --json` 输出合法 JSON，含 `format_version` / 根 Span / 子 Span 数组 / 每子 Span 含 `severity` / `fix` / `spec_ref`；
- `harness-init validate --trace` 落盘 `.harness/trace/validate-<ts>.json`，连续跑 11 次后目录只剩最近 10 份；
- `harness-init doctor --json` 同款 schema；
- 字段可无损映射 SARIF result（手工核对 `ruleId` ← `spec_ref`、`message.text` ← `message`、`fixes[]` ← `fix`、`level` ← `severity`）；
- 默认 stdout 行为与 v2.0.4 完全一致（向后兼容）；
- 删除 `--json` / `--trace` 参数 + 新字段后，`make verify` 仍绿。

**回滚**：`git revert` 阶段 D commit。

---

### 3.5 阶段 E：Secret 扫描门禁（W06，#7）

**内容**：

- 播种 `templates/common/scripts/scan_secrets.py`（纯 Python，基于 detect-secrets；**注意：原决议落 `.harness/scan_secrets.py`，本阶段按 #8 D3 收敛落 `scripts/`，见本 spec §5**）；
- 模板 Makefile 在阶段 B 已改的 `verify` 依赖链上追加 `check-secrets`（即 `verify: lint format-check check-deps check-secrets test`）；
- 模板 dev 依赖加 `detect-secrets`；
- **不播种** `.harness/permissions.md`（#7 缓议进雾区）；
- **不播种** pre-commit 形态（撞 W04 git 零接触家规）。

**验收**：

- 生成项目 `make verify` 通过（无 secret 时 `check-secrets` 绿）；
- 手植一条假 API key 后 `make check-secrets` 失败并给出文件 + 行号；
- 删除 `scripts/scan_secrets.py` + Makefile 行 + dev 依赖后，`make verify` 仍绿。

**回滚**：`git revert` 阶段 E commit。

---

### 3.6 阶段 F：端到端验证插座 + 事前问神谕（W07，#8）

**内容**：

- 播种 `templates/common/scripts/verify/` 目录 + skip 状态占位测试（`test_smoke.py` 含 `pytest.skip("TODO: encode user path")`）；
- 播种 `templates/common/scripts/verify/README.md`（四型注释态范文：cli `--help` / web 起服务 + 健康检查 / lib import + 版本 / notebook 执行一格）；
- 模板 Makefile 增 `verify-e2e` target：`pytest scripts/verify/ -rs`；
- **`make verify` 一字不改**（守 < 5s 快门禁，D1）；
- 播种 `templates/common/scripts/verify_action.py`（~40 行，**只实现 import 查询**，复用 #4 `layers.yaml` + grimp，零新依赖，D4）；
- AGENTS.md 模板增补条款：
  - 「跨包 import 前先跑 `python scripts/verify_action.py --action "import A from B"`」（软触发，不接进 `make verify`，D4）；
  - 「evaluate 阶段 MUST 跑 `make verify-e2e`」（仅文字条款，不改 `scripts/stage.py`，D1）；
- 失败侧静态指路牌（D6）：各 `check-*` target 挂自己的 `|| echo "Fix: see AGENTS.md §X.Y"`，失败只打印对应那条；
- CI 可选 job：`templates/common/.github/workflows/ci.yml` 增 `verify-e2e` job（注释态，用户按需启用，D1）。**[编注：job 名 / trigger / 内容由实施者按项目 CI 现状定，spec 只要求「注释态可选」]**；
- **砍掉 `make add-verify`**（D5）。

**验收**：

- 生成项目 `make verify` 通过（`verify-e2e` 不在 `verify` 依赖链上，快门禁 < 5s）；
- `make verify-e2e` 跑 skip 占位测试，退出码 0，`-rs` 打印 skip 原因（堵死「静默假绿」，D7）；
- `python scripts/verify_action.py --action "import core from cli"` 在 contracts 空时输出 `VALID`（哑火态如实标注，D4）；
- 手填一条 contract 后，违规 import 查询输出 `INVALID` + Rule 引用 + Fix，退出码 1（hook-ready 契约，D4）；
- 各 `check-*` target（`check-deps` / `check-secrets`）失败时各自只打印对应那条指路牌，不打印其他 target 的（D6）；
- 删除 `scripts/verify/` + `scripts/verify_action.py` + Makefile 增行 + AGENTS.md 条款后，`make verify` 仍绿（D8）。

**回滚**：`git revert` 阶段 F commit。

---

### 3.7 阶段 G：`validate --json` 计数汇总（W09，#10）

> **拆分理由**：`summary` 块逻辑上可与阶段 D 一次做完，但 #6（schema）与 #10（计数汇总）是独立票据、独立决议，分阶段便于独立回滚（删 `summary` 不影响 `--json` 本体）。

**内容**：

- `validate --json` 输出增顶层 `summary: {total, passed, failed}` 块（复用 #6 `severity` / `spec_ref` / `format_version`）；
- stdout 末尾增一行「通过 X/Y」（人可读，与现有逐项 ✅ / ❌ 同物种）；
- `doctor --json` 同款；
- **守死边界**：只计数、不加权、不评级、不画图（#10 D3）。

**验收**：

- `harness-init validate --json` 输出含 `summary.total` / `summary.passed` / `summary.failed`，三数满足 `total = passed + failed`；
- stdout 末尾出现「通过 X/Y」一行；
- `harness-init doctor --json` 同款；
- 删除 `summary` 块 + stdout 那一行后，`make verify` 仍绿。

**回滚**：`git revert` 阶段 G commit。

---

### 3.8 阶段 H：脚本落点核对与文档同步（#8 D3 收敛，本 spec §5）

**内容**：核对 + 文档同步（迁移已在阶段 C / E 播种时内联完成，本阶段无代码迁移动作）：

- 核对生成项目 `.harness/` 下无 `.py` 文件；
- 核对所有 PBH 机制脚本位于 `scripts/`；
- AGENTS.md / README / SPEC / Makefile 中引用路径与实际落点一致（如旧文档仍写 `.harness/stage.py` 则修正为 `scripts/stage.py`）。

**验收**：

- 生成项目 `.harness/` 下无 `.py` 文件（只有数据 / 文档）；
- 所有 PBH 机制脚本位于 `scripts/`；
- AGENTS.md / README / SPEC / Makefile 引用路径同步更新；
- `make verify` 绿。

**回滚**：`git revert` 阶段 H commit。

---

### 3.9 阶段 I：`docs/design.md` 口径修正（#10 移交，本 spec §7）

**内容**：按本 spec §7 修正 §2 / §4.1 第 3 条。

**验收**：

- `docs/design.md` §2 不再点名「Harness-Lint / Harness-Test」为 PBH 生态工具；
- §4.1 第 3 条改为「可视化 / 评分归市场生态（含 SARIF 消费方如 GitHub Code Scanning），PBH 只出机器可读事实」；
- 本仓库 `make verify` 绿（文档改动不影响代码门禁）。

**回滚**：`git revert` 阶段 I commit。

---

### 3.10 阶段 J：地图收尾（本 spec §6）

> **状态：已随本 spec 交付执行完毕（2026-09-06）**。#9 已关闭、#1 已回写、票据板全勾选。以下保留为记录。

**内容**：回写 #1 Decisions-so-far + 关闭 #9 + 确认无遗留开放票据。

**验收**：

- #1 Decisions-so-far 含 #9 条目；
- #9 关闭；
- #1 票据板全部勾选；
- 地图雾区「脚本落点统一」条目出雾（随阶段 H 落定）；
- 地图 Out of scope 含「PBH 自建 harness-lint / harness-agent」退役条（#10 已写入）。

**回滚**：N/A（地图操作不可逆，但可重开 #9）。

---

## 4. 雾区交接

以下条目**不在 P1 范围**，但 P1 决议为其留下已知约束。实施 P1 时**不得**顺手解决这些条目；未来毕业为票据时，须以本节约束为前提。

### 4.1 SPEC v2.1 协议条款

**已知约束**：

- P1 新能力（分层声明、预验证接口、状态机推进接口、trace 格式）写入协议的措辞与版本策略；
- 需 P1 设计全部落定后才锐化；
- 继承自 #4：「SPEC 条款措辞留给雾区 SPEC v2.1 票据；本票据只定能力接口」；
- 继承自 #6：`format_version` 试行 `0.x` 再冻结（pip 式，用户对「出生即冻结」家规的显式破例）；
- 继承自 #8：`verify_action.py` hook-ready 契约（退出码 VALID=0 / INVALID=1）须写入 SPEC 作为生态接口；
- 继承自 #10：`summary` 块 schema 须写入 SPEC，并明确「只计数、不加权、不评级」边界。

**毕业触发**：P1 阶段 B ~ G 全部落地 + SPEC v2.1 措辞锐化（注：`format_version` 的「一个 minor 版本观察期」是 #6 自身的冻结条件，非本条毕业触发）。

---

### 4.2 生态闭环接口

**已知约束**：

- `.harness/trace/` 格式与稳定性承诺已随 #6 定案（`format_version` + SARIF-mappable）；
- #10 定 harness-lint / harness-agent 退役为生态（非 PBH 交付物）；
- 通用评分 / 看板归市场现成工具（Factory Agent Readiness / sverklo）；
- PBH 只出机器可读事实、由市场消费方经 SARIF 桥渲染；
- **PBH 侧已无待定项**，余为生态第三方自建时的事（出本地图范围）。

**毕业触发**：N/A（已出本地图范围）。

---

### 4.3 记忆三分目录

**已知约束**：

- `.harness/memory/{episodic,procedural,failures}.md`，报告 P2 项；
- 与 trace 格式强耦合，等 #3 结论消化后重估；
- 继承自 #6：trace 是 CI 式门禁运行记录，**不是 Agent 行为监控**（`design.md` §2 边界）——记忆三分若引入，须明确区分「门禁运行痕迹」与「Agent 行为痕迹」，后者不进 PBH。

**毕业触发**：P2 规划启动 + trace 格式冻结（`format_version` bump `1.0`）。

---

### 4.4 事前问 `create-file` 半边（#8 D4 缓议）

**已知约束**：

- `verify_action.py` 当前只落地 import 查询（grimp 图背书、精确）；
- `create-file`（新位置建文件）判定天生启发式、硬编码白名单会猜结构（违 W03）、更贴「塑造 agent 行为」边，且与 import 半边同折旧；
- 待「先登记再动工」对文档防腐的价值锐化再毕业；
- **退役触发同 D4**：模型能稳定遵守 `layers.yaml` 时整块删除（含 import 半边）。

**毕业触发**：「先登记再动工」对文档防腐的价值锐化 + 用户明确指令。

---

### 4.5 项目风险声明（`permissions.md`，#7 缓议）

**已知约束**：

- 证据证实七家 Agent 均无「项目级风险事实声明」专门落点（行业惯例是 AGENTS.md 安全章节）；
- 用户裁定「无法保证 Agent 遵守、过于复杂」；
- 待「跨工具公共信息源」价值锐化或 AGENTS.md 行数预算吃紧时重估；
- 一手证据：`docs/plans/wayfinder/research/W06-主流Agent权限与secret扫描现状调研.md`。

**毕业触发**：「跨工具公共信息源」价值锐化 或 AGENTS.md 行数预算吃紧。

---

### 4.6 脚本落点统一（#8 D3 显式移交本 spec）

**状态**：**已出雾**，随本 spec §5 落定。

---

## 5. 脚本落点统一（#8 D3 收敛）

### 5.1 家规（终局）

> **可执行种子脚本 → `scripts/`；协议数据 / 文档 → `.harness/`**

**理由**：

- `scripts/` 是行业通用可执行脚本落点（GitHub / GitLab / 开源项目惯例）；
- `.harness/` 作为 PBH 协议专属目录，只承载「协议数据 + 协议文档」，语义纯粹；
- 历史不一致（W04 `stage.py`、W06 `scan_secrets.py` 在 `.harness/`）源于各票独立设计，未跨票对齐；
- #8 D3 显式移交本 spec 收敛，不重开已关闭的 #5 / #7。

### 5.2 迁移清单

| 脚本 | 原决议落点 | 终局落点 | 来源票 | 迁移动作 |
|------|-----------|---------|--------|---------|
| `lint_deps.py` | `scripts/lint_deps.py` | `scripts/lint_deps.py` | #4 | 无变动（已符合家规） |
| `stage.py` | `.harness/stage.py` | `scripts/stage.py` | #5 | **阶段 C 播种时直接落 `scripts/`**；AGENTS.md 条款引用路径同步 |
| `scan_secrets.py` | `.harness/scan_secrets.py` | `scripts/scan_secrets.py` | #7 | **阶段 E 播种时直接落 `scripts/`**；Makefile `check-secrets` target 引用路径同步 |
| `verify_action.py` | `scripts/verify_action.py` | `scripts/verify_action.py` | #8 | 无变动（已符合家规） |
| `verify/` 目录 | `scripts/verify/` | `scripts/verify/` | #8 | 无变动（已符合家规） |

### 5.3 `.harness/` 保留内容（纯数据 / 文档）

| 路径 | 类型 | 来源 |
|------|------|------|
| `.harness/layers.yaml` | 数据（声明式配置） | #4 |
| `.harness/progress.json` | 数据（状态机快照 + 账本） | #5 |
| `.harness/known_pitfalls.md` | 文档（项目特定陷阱记录） | 既有 |
| `.harness/templates/plan_template.json` | 数据（计划模板） | 既有 |
| `.harness/trace/validate-<ts>.json` | 数据（门禁运行痕迹） | #6 |
| `.harness/memory/{episodic,procedural,failures}.md` | 数据（记忆三分，P2 雾区） | 雾区 §4.3 |

### 5.4 验收

- 生成项目 `.harness/` 下无 `.py` 文件；
- 所有 PBH 机制脚本位于 `scripts/`；
- AGENTS.md / README / SPEC / Makefile 引用路径同步更新；
- `make verify` 绿。

### 5.5 可拆卸性

删除 `scripts/` 下相应脚本 + Makefile target + AGENTS.md 条款 + 模板 dev 依赖，零残留。`.harness/` 下数据 / 文档随脚本删除一并清理（或保留为「死数据」，由用户自行决定）。

---

## 6. 地图收尾

### 6.1 回写 #1 Decisions-so-far

在 #1 地图正文 `## Decisions so far` 段追加：

```markdown
- [W08 终点综合：P1 实施 spec 撰写](#9) — 产出 `docs/plans/2026-09-06-p1-implementation-spec.md`，决策完备，含 P0 修复清单 / 8 票决议全文 / 10 阶段实施顺序 / 雾区交接 / 脚本落点统一（#8 D3 收敛：可执行→scripts/、数据→.harness/）/ design.md §2 §4.1 口径修正（#10 移交：harness-lint / harness-agent 退役为生态、可视化归市场 + SARIF 桥）；地图终点达成
```

### 6.2 关闭 #9

- 附 resolution comment（内容 = 本 spec 路径 + 一句话摘要）；
- 关闭 #9；
- #1 票据板 `#9` 勾选。

### 6.3 确认无遗留开放票据

- #1 子 issue 全部关闭（#2 ~ #10）；
- 地图雾区「脚本落点统一」条目出雾（随阶段 H 落定，本 spec §5）；
- 地图 Out of scope 含「PBH 自建 harness-lint / harness-agent」退役条（#10 已写入）；
- 地图 Notes 无待办。

### 6.4 地图终点达成

**Destination 原文**：「产出一份**决策完备的 P1 实施 spec**（机械执法层 + 可观测性最小闭环），保存到仓库 `docs/plans/`，可直接交给 `/implement` 或 `/to-tickets` 执行。地图完成标准：spec 中不再有「待定」的设计取舍。」

**达成判定**：

- ✅ spec 已产出（本文件）；
- ✅ 保存到 `docs/plans/2026-09-06-p1-implementation-spec.md`；
- ✅ 决策完备（7 项必备内容全含，无「待定」设计取舍）；
- ✅ 可直接交 `/implement` 或 `/to-tickets`（第 3 节 10 阶段每阶段独立可交付、独立可回滚）；
- ✅ 地图所有票据关闭；
- ✅ 雾区交接清晰（第 4 节 5 条缓议项 + 已知约束 + 毕业触发）。

**地图 #1 可关闭**（或保留为历史档案，由用户裁定）。

---

## 7. `docs/design.md` §2 / §4.1 口径修正（#10 移交）

### 7.1 修正背景

#10 决议：harness-lint / harness-agent 退役为生态（非 PBH 交付物）；可视化 / 评分归市场生态（含 SARIF 消费方如 GitHub Code Scanning），PBH 只出机器可读事实。

照 #8 D3 先例，#10 未擅改 `design.md`，显式移交本 spec 随终点一并收敛。

### 7.2 §2 架构分层 修正

**原文**（`docs/design.md` §2 架构分层末段）：

> 让协议「动起来」是生态工具（Harness-Lint、Harness-Test 等）的职责。

**改为**：

> 让协议「动起来」由生态承担——含 SARIF 消费方（如 GitHub Code Scanning）、市场通用就绪度工具（如 Factory Agent Readiness / sverklo）、以及第三方在 PBH 的 SARIF-mappable trace 上自建的渲染器 / 分析器。PBH 核心只出机器可读事实（`validate --json` + `.harness/trace/`），不写 consumer 代码。

**理由**：

- 原点名「Harness-Lint / Harness-Test」暗示 PBH 会自建这两个工具，与 #10 D2 退役决议冲突；
- 新措辞明确「生态 = 市场现成工具 + SARIF 桥 + 第三方自建」，与 #10 D3「PBH 出事实、市场渲染」分工一致；
- 保留「PBH 核心只播种」边界（`design.md` §2 主旨不变）。

### 7.3 §4.1 三层防腐机制 第 3 条 修正

**原文**（`docs/design.md` §4.1 三层防腐机制 第 3 条）：

> 3. **生态工具让失败可见**：Harness-Lint 将协议遵守情况转化为可视化报告

**改为**：

> 3. **生态工具让失败可见**：可视化 / 评分归市场生态（含 SARIF 消费方如 GitHub Code Scanning、市场通用就绪度工具如 Factory Agent Readiness / sverklo），PBH 只出机器可读事实（`validate --json` + `.harness/trace/`，SARIF-mappable，见 #6 / #10 决议）

**理由**：

- 原点名「Harness-Lint」暗示 PBH 自建可视化报告，与 #10 D1 / D2 决议冲突（评分 / 评级 / 看板 / 可视化永久移出 PBH）；
- 新措辞明确「可视化归市场、PBH 出事实」，与 #10 D3 一致；
- 保留「三层防腐」结构（§4.1 主旨不变），只修正第 3 条的承载方。

### 7.4 地图雾区「生态闭环接口」重述

#10 已执行（见 #1 地图正文 `## Not yet specified` 段）：

> **生态闭环接口**：`.harness/trace/` 格式与稳定性承诺已随 #6 定案（`format_version` + SARIF-mappable）；#10 定 harness-lint / harness-agent 退役为生态（非 PBH 交付物），通用评分 / 看板归市场现成工具（Factory Agent Readiness / sverklo），PBH 只出机器可读事实、由市场消费方经 SARIF 桥渲染——**PBH 侧已无待定项**，余为生态第三方自建时的事（出本地图范围）

本 spec §4.2 原样收录。

### 7.5 验收

- `docs/design.md` §2 架构分层末段修正完成；
- §4.1 三层防腐机制第 3 条修正完成；
- 本仓库 `make verify` 绿（文档改动不影响代码门禁）；
- #1 地图雾区「生态闭环接口」条目已重述（#10 已执行，本 spec 核对）。

### 7.6 可拆卸性

N/A（文档修正，无代码可拆卸）。若未来 #10 决议被推翻（harness-lint 回头建），须同步回滚 §2 / §4.1 措辞。

---

## 8. 附录：可拆卸性总表

**纪律**：每条新规则必须带生效条件与退役条件（一手调研证实这是行业共识，见 `docs/plans/2026-09-01-harness-engineering-research.md` 机制 #22）。

| 交付物 | 生效条件 | 退役条件 | 退役动作 |
|--------|---------|---------|---------|
| 分层 lint（#2 #4） | 出生即生效；contracts 空时恒 VALID | 用户主动删除 | 删 `scripts/lint_deps.py` + `.harness/layers.yaml` + Makefile `check-deps` 行 + dev 依赖 `grimp` + AGENTS.md 条款 |
| 状态机契约（#5） | 出生即生效；`progress.json` 含 `stage_history: []` | 用户主动删除 | 删 `scripts/stage.py` + `stage_history` 字段 + `validators/progress_json.py` 相应分支 + AGENTS.md 条款 |
| `validate --json` + trace（#3 #6） | 出生即生效；`--json` / `--trace` 为可选开关 | 用户主动删除 | 删 `--json` / `--trace` 参数 + `severity` / `fix` / `spec_ref` / `format_version` 字段 + `.harness/trace/` 目录 |
| Secret 扫描（#7） | 出生即生效；`make verify` 含 `check-secrets` | 用户主动删除 | 删 `scripts/scan_secrets.py` + Makefile `check-secrets` 行 + dev 依赖 `detect-secrets` |
| 端到端验证插座（#8 D1 D2 D7） | 出生即生效；`verify-e2e` skip 占位开箱即过 | 用户主动删除 | 删 `scripts/verify/` + Makefile `verify-e2e` 行 + AGENTS.md 条款 + CI job |
| 事前问神谕（#8 D4） | 出生即生效；contracts 空时恒 VALID（哑火态如实标注） | **折旧触发**：模型能稳定遵守 `layers.yaml` 时 | 删 `scripts/verify_action.py` + AGENTS.md 条款 |
| 失败侧指路牌（#8 D6） | 出生即生效；各 `check-*` 挂 `\|\| echo` | 用户主动删除 | 删 Makefile 各 `\|\| echo` 行 |
| `validate --json` 计数汇总（#10） | 出生即生效；`summary` 块 + stdout 一行 | 用户主动删除 | 删 `summary` 块 + stdout 那一行 |
| 脚本落点统一（#8 D3） | 出生即生效；`.harness/` 无 `.py` | N/A（家规，非交付物） | N/A |
| `design.md` 口径修正（#10） | 出生即生效；§2 / §4.1 修正 | N/A（文档修正） | 若 #10 决议被推翻，回滚措辞 |

**退役触发条件分类**：

- **用户主动删除**：大多数交付物，用户按需拆卸；
- **折旧触发**：事前问神谕（#8 D4），随模型能力提升边际价值递减，附退役日期；
- **N/A**：家规 / 文档修正，非可拆卸交付物。

---

## 9. 附录：PBH 三问终验汇总

**纪律**：对标 / 市场只作旁证，裁决以 PBH 三问 + `design.md` 边界为准；三问只否决不背书（中性项直说不欠人情）。

| 交付物 | ①干预 AI 思考？ | ②降低「没有 PBH 的痛苦」？ | ③让协议更难被忽略？ | 结论 |
|--------|---------------|------------------------|------------------|------|
| 分层 lint（#2 #4） | 否（静态扫描） | 否（播种环境标准） | 是（`make verify` 阻断） | ✅ |
| 状态机契约（#5） | 否（只校验转移） | 否（播种契约） | 是（前馈拦截） | ✅ |
| `validate --json` + trace（#3 #6） | 否（只输出事实） | 否（播种可观测性） | 是（机器可读门禁） | ✅ |
| Secret 扫描（#7） | 否（模式匹配） | 否（播种门禁） | 是（`make verify` 阻断） | ✅ |
| 端到端验证插座（#8 D1 D2 D7） | 否（只种插座） | 否（播种环境） | 是（CI 归宿） | ✅ |
| 事前问神谕（#8 D4） | 否（被动神谕） | 否（抬门槛） | **不完全**（软触发） | ⚠️ 全票最弱环，用户知情后裁定保留最小版 |
| 失败侧指路牌（#8 D6） | 否（静态指路） | 否（播种教学） | 是（归因锚定） | ✅ |
| `validate --json` 计数汇总（#10） | 否（计数 = 事实） | **中性**（用户自己也能数） | 弱正向 | ✅（驱动力 = `design.md` 边界 + 市场 commodity 化证据） |
| 脚本落点统一（#8 D3） | N/A（代码卫生） | N/A | N/A | 三问中性 |
| `design.md` 口径修正（#10） | N/A（文档修正） | N/A | N/A | 三问中性 |

---

## 10. 附录：一手来源索引

| 来源 | 路径 | 用途 |
|------|------|------|
| 对标报告 | `PBH-harness-engineering-对标报告.md` | P0 / P1 / P2 清单 + 评分卡 + 改进路线图 |
| 一手调研 | `docs/plans/2026-09-01-harness-engineering-research.md` | 9 篇一手来源核实 + 机制 #22 可拆卸 + 路线图 §6.1 ~ §6.3 |
| W01 调研笔记 | `docs/plans/wayfinder/research/W01-分层lint工具选型.md` | grimp vs import-linter vs deptry vs ruff 对比 |
| W02 调研笔记 | `docs/plans/wayfinder/research/W02-验证事件trace格式.md` | OTel 语义约定 + OTLP-JSON 结构子集 |
| W05 调研笔记 | `docs/plans/wayfinder/research/W05-行业机器可读输出共识补充调研.md` | SARIF 2.1.0 / GitHub / Bazel / pytest / coverage.py / eslint / pip / Terraform / OTLP + ruff 0.15.20 实测 |
| W06 调研笔记 | `docs/plans/wayfinder/research/W06-主流Agent权限与secret扫描现状调研.md` | 七家 Agent 权限 + secret 扫描现状 |
| PBH-SPEC | `docs/spec/PBH-SPEC.zh-CN.md` | 协议标准（驱动 `validate` / `doctor`） |
| design.md | `docs/design.md` | 架构定位 + PBH 三问 + 三层防腐 + 归因锚定 |
| Wayfinder 地图 | GitHub Issue #1 | 决策地图正本 |
| 票据决议 | GitHub Issue #2 ~ #10 | 各票 resolution comment |

---

## 11. 附录：实施 checklist（交 `/implement` 或 `/to-tickets`）

**阶段 A：P0 修复**
- [ ] P0-1 IDE 适配文件按 `project_type` 渲染
- [ ] P0-2 4 模板 × 2 模式全部 `make verify` 通过
- [ ] P0-3 `.pre-commit-config.yaml` 合法化或删除
- [ ] P0-4 旧版角色残留清理
- [ ] P0-5 `opencode.yaml` 硬编码清理
- [ ] P0-6 模板 `docs/` 引用与实际目录一致
- [ ] P0-7 根 Makefile 与模板 Makefile lint 范围统一
- [ ] P0-8 `configs/dev.yaml` Agent 运行时残骸清理

**阶段 B：分层依赖 lint**
- [ ] 播种 `templates/common/.harness/layers.yaml`
- [ ] 播种 `templates/common/scripts/lint_deps.py`
- [ ] 模板 Makefile 增 `check-deps` target
- [ ] 模板 dev 依赖加 `grimp`
- [ ] AGENTS.md 模板增补条款
- [ ] 核心侧 `validators/layers_yaml.py`

**阶段 C：状态机推进契约**
- [ ] `progress.json` 模板增 `stage_history: []`
- [ ] 播种 `templates/common/scripts/stage.py`（**注意落 `scripts/`，非 `.harness/`**）
- [ ] 扩展 `validators/progress_json.py`
- [ ] AGENTS.md 模板增补条款

**阶段 D：`validate --json` + trace**
- [ ] `ValidationResult` 增 `severity` / `fix` / `spec_ref`
- [ ] `validate` CLI 增 `--json` / `--trace`
- [ ] JSON 骨架（OTel 语义字段）
- [ ] trace 落盘 + 轮转（保留 10 份）
- [ ] `doctor` 同款 schema
- [ ] stdout 双轨

**阶段 E：Secret 扫描门禁**
- [ ] 播种 `templates/common/scripts/scan_secrets.py`（**注意落 `scripts/`，非 `.harness/`**）
- [ ] 模板 Makefile 增 `check-secrets` target
- [ ] 模板 dev 依赖加 `detect-secrets`

**阶段 F：端到端验证插座 + 事前问神谕**
- [ ] 播种 `templates/common/scripts/verify/` + skip 占位测试
- [ ] 播种 `templates/common/scripts/verify/README.md`（四型注释态范文）
- [ ] 模板 Makefile 增 `verify-e2e` target
- [ ] 播种 `templates/common/scripts/verify_action.py`（只 import 查询）
- [ ] AGENTS.md 模板增补条款（软触发 + evaluate 阶段）
- [ ] 失败侧静态指路牌（每 target 一条 `|| echo`）
- [ ] CI 可选 job（注释态）
- [ ] **砍掉 `make add-verify`**

**阶段 G：`validate --json` 计数汇总**
- [ ] `validate --json` 增 `summary` 块
- [ ] stdout 末尾增「通过 X/Y」一行
- [ ] `doctor --json` 同款

**阶段 H：脚本落点统一**
- [ ] 核对 `.harness/` 下无 `.py` 文件
- [ ] 核对所有 PBH 机制脚本位于 `scripts/`
- [ ] AGENTS.md / README / SPEC / Makefile 引用路径同步

**阶段 I：`design.md` 口径修正**
- [ ] §2 L31 修正
- [ ] §4.1 L64 修正

**阶段 J：地图收尾**
- [ ] 回写 #1 Decisions-so-far
- [ ] 关闭 #9
- [ ] #1 票据板全部勾选
- [ ] 地图雾区「脚本落点统一」出雾
- [ ] 地图 Out of scope 核对

---

**Spec 终点**。本文件决策完备，无「待定」设计取舍，可直接交 `/implement` 或 `/to-tickets` 执行。
