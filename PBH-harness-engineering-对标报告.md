# PBH-harness-engineering-对标报告

# Project-Bootstrap-Harness（PBH）× 大厂 Harness Engineering 规范对标报告

> 分析对象：`renjianguojinqianfan/Project-Bootstrap-Harness`（master 分支，最后提交 2026-07-07，v2.0.4）  
>     对标基线：腾讯云开发者社区、阿里云开发者社区、字节系（DeerFlow 2.0 / TRAE，二手）公开分享，以及 OpenAI Codex、Anthropic、LangChain、Stripe、Martin Fowler / Thoughtworks、上海 AI Lab Self-Harness 的原始材料  
>     报告日期：2026-09-01

---

## 0. 一页纸结论

### 0.1 评分卡

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| 1. 知识供给与渐进式披露 |  |  |  |  |
|  | 15% | 30 |  | 大 |
| 3. 验证闭环（build→lint→test→verify） |  | 50 | 85 | 中 |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  | 20 | 70 |  |
|  |  |  |  |  |
| 8. 可观测性与度量 |  | 5 | 55 | 大 |
|  |  |  |  |  |
|  |  |  |  |  |

加权总分：PBH 33 / 100，行业基线 76 / 100。

考虑到 PBH 自我定位是"协议播种器"（`docs/design.md` 明确不碰 Agent 运行时），剔除维度 5、7、8 中属于"运行时职责"的部分后，定位内得分 41 / 100 —— 套用阿里云 Qoder 的审计口径（0–20 裸奔 / 21–70 有基础但有缺口 / 71+ 健康），PBH 落在 "有基础、但缺口明显"区间的中段偏下。

### 0.2 一句话结论

> PBH 已经做对了 Harness 里最容易做、也最容易同质化的那一层（AGENTS.md 入口 + 统一质量门禁 + 协议标准化），但恰恰缺了 2026 年行业共识里价值最高的那一层：确定性机械约束（分层依赖 lint、预验证脚本、端到端 verify）与可自我进化的闭环（trace → critic → refiner）。它现在是一份"写得很好的说明书"，而大厂规范要的是一套"会执法、会学习、会留痕的执行系统"。

### 0.3 Top 5 必做（按 ROI 排序）

| # | 动作 | 为什么 | 对标条目 |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

---

## 1. 研究范围、方法与可信度声明

### 1.1 资料来源

| 类别 |  | 状态 |
| --- | --- | --- |
| 腾讯云开发者社区 | 《Agent 系列（三）：Harness Engineering》[2647887](https://cloud.tencent.com/developer/article/2647887)、《Agent Harness：2026 年 AI 工程的核心范式》[2698416](https://cloud.tencent.com/developer/article/2698416)、《Harness Engineering：Agent 工程新范式》[2684699](https://developer.cloud.tencent.com/article/2684699)、《AI 编程工程化的三次进化》[2699549](https://cloud.tencent.cn/developer/article/2699549)、《别卷模型了》[2648322](https://cloud.tencent.com.cn/developer/article/2648322)、宋振华《后端学 agent harness》17 篇专栏（[入口](https://cloud.tencent.cn/developer/column/108078)，重点第 9 篇 [2719793](https://cloud.tencent.cn/developer/article/2719793) 上下文管理、第 11 篇 [2721630](https://cloud.tencent.cn/developer/article/2721630) 错误处理、第 12 篇 [2722076](https://cloud.tencent.cn/developer/article/2722076) 安全、第 13 篇 [2722191](https://cloud.tencent.cn/developer/article/2722191) 验证循环） | ✅ 一手，信息密度最高 |
| 阿里云开发者社区 | 《Qoder 工程实践：Harness Engineering 指南》[1724843](https://developer.aliyun.com/article/1724843)、《Agent Harness 的核心组成》[1740482](https://developer.aliyun.com/article/1740482)、《一些 Harness Engineering 的实践》[1718179](https://developer.aliyun.com/article/1718179)、《用 AGENTS/ARCHITECTURE 实战》[1745097](https://developer.aliyun.com/article/1745097)、《如何给 Agent 写一份行为规范》[1744762](https://developer.aliyun.com/article/1744762) |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

可信度声明：本报告中所有数字均标注了出处。凡标 ⚠️ 的来源，其数字用于判断量级与方向，不建议直接引用到对外材料。

### 1.2 分析对象快照

|  |  |
| --- | --- |
|  | `renjianguojinqianfan/Project-Bootstrap-Harness`，Python，MIT |
|  |  |
|  | 4 / 1 / 0 |
|  |  |
|  |  |
| Topics | harness-engineering、ai-coding、claude-code、codex、opencode、trae |

---

## 2. 行业规范基线：2026 年 Harness Engineering 的共识清单

### 2.1 范式定义

核心公式：`Agent = Model + Harness`（Martin Fowler，2026-02；腾讯云将其译为"线束工程"）。Harness 是所有不属于模型本身的代码、配置与执行逻辑——系统提示、工具/MCP 及其描述、文件系统与沙箱、编排逻辑、以及用于确定性执行的钩子/中间件。

三代演进（腾讯云 [2699549](https://cloud.tencent.cn/developer/article/2699549)）：

| 阶段 | 时间 | 解决什么 |  |
| --- | --- | --- | --- |
| Prompt Engineering | 2022–2024 |  | 单次交互质量，无法承载长链路 |
|  |  |  |  |
|  |  |  |  |

最强的一条证据：LangChain 在 Terminal-Bench 2.0 上不换模型（同为 gpt-5.2-codex），只改 Harness，得分 52.8% → 66.5%（+13.7pp），排名从 30 名开外跃至前 5。上海 AI Lab Self-Harness 同样是只改 Harness：Qwen3.5-35B-A3B +104%、MiniMax M2.5 +28%、GLM-5 +24%。

> 这意味着：PBH 所在的赛道是正确的，且天花板很高。问题不在方向，在深度。

### 2.2 大厂实践矩阵

|  |  |  |
| --- | --- | --- |
|  |  |  |
| Anthropic |  | Initializer Agent（首轮搭环境：`init.sh` + `claude-progress.txt` + feature list + 首个 commit）/ Coding Agent（每轮只做 1 个 feature，JSON 而非 Markdown 存 feature list，>200 项）；每轮开工 7 步固定动作；端到端验证走 Puppeteer MCP 真实用户路径 |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

### 2.3 可执行的行业 checklist（25 条）

|  |  |  |  |
| --- | --- | --- | --- |
| 1 |  | ~100 行，只做地图指向 `docs/`；Codex 上限 32 KiB | OpenAI |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
| 5 | 本地门禁 \<5 秒 |  |  |
|  |  |  |  |
|  |  |  |  |
| 8 | 完成前拦截 | PreCompletionChecklist，最多强制验证 3 次 |  |
| 9 |  | 协调者只规划委派，执行者干净上下文 | Qoder / OpenAI |
| 10 | 子代理隔离 | worktree（小团队）/ 预热 devbox（大规模） | Qoder / Stripe |
|  |  |  |  |
| 12 |  |  | Qoder / Anthropic |
|  | 检查点 |  |  |
|  |  |  |  |
| 15 | 自我进化回路 | Weakness Mining → Harness Proposal → Validation，门控 held-in/held-out 一升一不降 | Self-Harness / Qoder |
| 16 | 记忆三分 | 情景（含 Errors and Fixes）/ 程序（成功步骤）/ 失败 | Qoder / Anthropic |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
| 21 |  | Input（WAF）→ Tool（API 网关，最关键）→ Output（4 阶段） |  |
|  |  |  |  |
|  |  |  |  |
| 24 | 断路器 | 瞬态指数退避；用户可修复只暂停；CI 2 轮硬熔断；LoopDetection 软熔断 | Stripe / 腾讯云 |
| 25 | 垃圾回收 | doc-gardening agent + 偏差扫描 agent | OpenAI / Fowler（janitor army） |

---

## 3. PBH 项目解剖

### 3.1 定位边界（这是理解一切的前提）

`docs/design.md` 里写了三条自检标准（"PBH 三问"）：

1. 这是不是在干预 AI 思考？→ 是，就拒绝

2. 这是不是在降低"没有 PBH 的痛苦"？→ 是，就在削弱自己

3. 这是不是让协议更难被忽略？→ 否，就没价值

并明确：PBH 核心不包含也不会包含 Agent 运行时、代码生成、行为监控。v1.1.0 主动删除了 `harness/{runner,evaluator,state,workflow}.py` 与 `agents/{planner,generator,evaluator}.py`。

评价：这个边界划得很漂亮，也确实让项目保持了克制与可解释性。 但要注意一个副作用——"不越界"正在被当成"不补位"的挡箭牌。行业要的不是 PBH 自己去做 Agent 运行时，而是 PBH 把运行时需要的地基（分层规则、预验证脚本、verify 骨架、状态机、trace 目录）种进项目里。这些全都是"播种"而非"执行"，完全不违反 PBH 三问。这是本报告最重要的一个判断。

### 3.2 生成物清单

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
| `docs/context.md`、`PROJECT_MAP.md`、`decisions/ADR_TEMPLATE.md` | 深层上下文三件套 | ⚠️ 骨架尚可，内容为空壳 |
|  |  |  |
|  |  |  |
| `.github/workflows/ci.yml` | CI | ⚠️ 只有 lint + test，type-check 整段注释 |
|  |  |  |

### 3.3 已做对的 5 件事（值得保留并发扬）

1. 统一门禁语义：`make verify` 一个命令覆盖 lint + format-check + test + coverage，并对齐"自评估禁令"（唯一 ground truth）。这正中行业共识——Boris Cherny：给模型一种验证自己工作的方法，质量可提升 2–3 倍。

2. AGENTS.md 行数硬约束（≤80 行）：比 OpenAI 的 ~100 行更严格，且 SPEC 里用 MUST/MAY 明确章节必要性，可机器校验。

3. 5 阶段生命周期状态机：`init → plan → execute → evaluate → done`，每阶段定义 Agent 行为预期（如 execute 阶段"抑制风格噪声"）。这个抽象在行业里是稀缺的——Anthropic 用 `feature_list.json` 表达的是任务级状态，PBH 表达的是项目阶段级状态，两者正交，有成为协议差异化条款的潜力。

4. 协议与实现解耦（PBH-SPEC v2.0 双语 + 独立版本号）：这是从"工具"升级为"标准"的正确姿势，也是最难被复制的部分。

5. 生态三角（harness-init 播种 / harness-lint 校验 / harness-agent 修复）：方向对，缺的是三者之间的数据闭环。

### 3.4 工程质量实测

| 项 | 现状 |
| --- | --- |
|  | 7 文件约 122 用例（test_core 44 / test_validation 32 / test_templates 16 / test_cli 12 / test_core_validation 11 / test_core_git 6 / test_utils 1） |
| CI | 仅 `windows-latest` × py3.11/3.12/3.13，跑 `pip install -e ".[dev]"` + `make verify`；无 Linux/macOS，无安全扫描 |
| 发布 | `v*.*.*` tag → make verify → build + twine check → PyPI Trusted Publishing ✅ |
|  |  |
|  |  |
| 验证器 |  |

---

## 4. 差距分析（逐维度）

### 维度 1｜知识供给与渐进式披露 — PBH 55 / 基线 80

|  | PBH 现状 | 证据 |
| --- | --- | --- |
| AGENTS.md ~100 行做索引，详细内容放 `docs/` 按需加载 |  | `templates/cli/AGENTS.md` |
| docs 目录提供高密度架构/约定/业务上下文 | ⚠️ `context.md` 是骨架模板（metadata/架构/命名/commit 格式/常见任务），信息密度尚可但无项目特有内容填充机制；`PROJECT_MAP.md`、`ADR_TEMPLATE.md` 近乎空白 | `templates/common/docs/` |
|  |  |  |
|  |  | OpenAI |
|  |  | Anthropic |

差距等级：中。 骨架对了，缺"密度"和"新鲜度"。

### 维度 2｜确定性机械约束 — PBH 30 / 基线 85 ⚠️ 最大短板

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
| lint 报错注入修复指令 | ❌ 无（ruff 原生报错，无项目语义） |  |
|  |  |  |

差距等级：大。这是当前 PBH 与"大厂规范"最刺眼的一处断裂。 阿里云 Qoder 的原话是：层级违反是 Agent 翻车的头号原因；事后 10 次 tool call 才能修复的事前 2 次交互就能避免。

### 维度 3｜验证闭环 — PBH 50 / 基线 85

|  |  |
| --- | --- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

差距等级：中偏大。 门禁本身立住了，但"验证通过"的定义太窄——只证明"代码能编译、测试能过"，没证明"功能是对的"。

### 维度 4｜状态、检查点与恢复 — PBH 32 / 基线 75 ⚠️ 最可惜

|  |  |
| --- | --- |
|  |  |
| 状态被自动推进 |  |
|  |  |
| 检查点 / 回滚 | ❌ 无（仅 AGENTS.md 文字建议使用 git worktree） |
|  |  |

差距等级：大，但修复成本低。 PBH 有一个行业里少见的好抽象（阶段级状态机），却没给它接上任何一根线。这是全项目投入产出比最高的一处。

### 维度 5｜运行时与编排 — PBH 8 / 基线 70（定位外，仅作参照）

PBH 主动不做 Agent 运行时，这一维度不应扣分，但需要在报告里说清两件事：

- ✅ 不该做的：子代理调度、上下文压缩、模型路由——这些确实属于 Agent 运行时，PBH 做就是越界。

- ❌ 应该做却没做的（仍属播种范畴）：worktree 隔离的脚本化支持（现在只是 AGENTS.md 里一句话）、`harness/` 目录骨架（trace/memory/tasks 三件套，Qoder 的标准布局）、上下文预算声明（如"AGENTS.md ≤80 行"已有，但可推广为"每次注入上下文预算 X tokens"）。

### 维度 6｜安全护栏与权限分级 — PBH 20 / 基线 70

|  |  |
| --- | --- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

差距等级：大。 考虑到 PBH 是"协议"而非"运行时"，不可能自己实现沙箱，但完全可以播种一份 `harness/permissions.md`（命令分级白/黑名单）+ 一个 secret 扫描钩子，成本极低。

### 维度 7｜自我进化与经验沉淀 — PBH 12 / 基线 60

| 行业做法 | PBH 现状 |
| --- | --- |
|  |  |
| Critic 分析模式 → Refiner 更新规则 |  |
| 记忆三分（情景/程序/失败） |  |
| 轨迹编译为确定性脚本（`make add-endpoint`） | ❌ 无 |
|  |  |

差距等级：大。 这也是"生态三角"（init/lint/agent）当前没有闭环的根因：harness-lint 能发现缺陷，harness-agent 能修复，但没有一层把"发现→诊断→修复"的模式沉淀成新的协议条款。

### 维度 8｜可观测性与度量 — PBH 5 / 基线 55

- 无 trace、无指标、无成本记录、无"门禁通过率/失败原因分布"统计。

- `validate` 的结果是一次性的 stdout，不落盘、不可聚合。

- 对比：OpenAI 接 Chrome DevTools 协议 + LogQL/PromQL；LangChain 用 LangSmith trace 做失败模式分析。

- 最低成本改进：`validate --json` 输出结构化结果 + 落盘 `.harness/trace/validate-<ts>.json`，一行改动就能开启数据飞轮。

### 维度 9｜自身工程质量与分发 — PBH 45 / 基线 85

加分：122 个测试、PyPI Trusted Publishing、`docs/RELEASE.md` 有明确的"绝不改"清单、CHANGELOG 规范、双平台 pre-push。

减分（详见第 5 节硬伤）：CI 只跑 Windows（而 README 自承 Windows 可能没装 make）、无 mypy、模板源码被 ruff 排除（`extend-exclude = ["src/harness_init/templates"]`，意味着发给用户的 Python 骨架从不被 lint）、repo 自身 CI 上传不存在的 `coverage.xml`、项目停滞 2 个月。

### 维度 10｜生态适配与协议标准 — PBH 68 / 基线 70 ✅ 优势项

- 5 个 AI 工具适配（Claude Code / Cursor / OpenCode / Copilot / Trae），且强度分层合理（CLAUDE.md 有数值表 > .cursorrules > opencode.yaml > copilot > trae）。

- PBH-SPEC v2.0 中英双语、独立版本号、`harness_version` 兼容字段 —— 这是全项目最有长期价值的一块资产。

- `validate` / `doctor` 提供了合规性的机器判定入口，方向正确。

- 扣分点：`validate` 覆盖太浅（见下），且 `--ide` 参数无校验（未知值静默生成全部）。

---

## 5. 硬伤清单（P0/P1/P2，可直接开 issue）

### P0 — 正确性缺陷，会导致生成的项目开箱即坏

| # | 问题 |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

### P1 — 一致性/可用性缺陷

|  |  |  |
| --- | --- | --- |
|  |  |  |
| 8 |  | `_ide.py:22` |
|  | `--quick` 漏排 `.trae/`；排除表含死条目 `tests/test_harness.py`（v1.1.0 已删） | `_quick.py:5` |
| 10 | CLI 文档称参数是"项目名称或目标路径"，但 `_validate_project_path` 拒绝任何含分隔符的路径；`harness-init .` 报 "Project name cannot be empty" | `cli.py` / `_utils.py` |
|  |  |  |
|  |  |  |
| 13 | AGENTS.md 章节编号从 §5 跳到 §8（§6/§7 为 SPEC 预留），CLAUDE.md 却引用了 AGENTS.md 中不存在的 "change control matrix" | 模板交叉引用 |

### P2 — 文档漂移与工程债

|  |  |  |
| --- | --- | --- |
| 14 | README 结构图写 `.harness/workspaces/`（实际是 `templates/`）；README 仍写 `make fix`（2.0.4 已改名 `make format`）；`trae-solo-comparison.md` 称 make verify 含 mypy（实际无）；CHANGELOG v1.1.5 声称修复 `skip-existing: true`，但 `publish.yml` 至今保留该配置 | README / docs |
|  | `opencode.yaml` 硬编码 `claude-3-5-sonnet` + 4 个第三方 skills，随模板分发且无版本锁定 | `templates/cli/opencode.yaml` |
|  |  |  |
|  |  |  |

---

## 6. 改进路线图

> 编排原则：先修正确性（P0），再补机械约束层（P1），最后做生态闭环（P2）。前三步都不违反"PBH 三问"——它们全都是"播种"，不是"执行"。

### P0：两周内 — 让生成的项目"开箱即过"（目标：定位内分 41 → 50）

|  |  |  |
| --- | --- | --- |
| 把 IDE 适配文件提到 `templates/common/`，按 `project_type` 渲染 | `templates/` 目录重构 | `harness-init x -t lib --ide=claude` 生成 CLAUDE.md 且 Type 正确 |
|  | `templates/notebook/pyproject.toml` | 4 个模板 × 2 模式全部 `make verify` 通过 |
|  |  |  |
| 修/删 `.pre-commit-config.yaml`（或提供合法版本 + 测试） |  | 解注释后 `pre-commit run --all-files` 通过 |
|  |  |  |
|  |  |  |

### P1：一个月内 — 补上"机械执法层"（目标：定位内分 50 → 65）

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
| `scripts/verify/` 骨架 + `make add-verify` | 引导用户把核心用户路径编码成可执行验证脚本 | Qoder verify skill |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  | 可观测性最小闭环 |

### P2：一个季度 — 从"工具"到"标准 + 生态闭环"（目标：定位内分 65 → 75+）

|  |  |  |
| --- | --- | --- |
| PBH-SPEC v2.1：把上述新能力写进协议 | 新增 §2.4 分层规则、§2.5 预验证接口、§3.x 验证管道四段、§3.x 状态机推进接口 | 协议即护城河 |
|  |  |  |
| 记忆三分 | `.harness/memory/{episodic,procedural,failures}.md`，executor 启动时按相关性注入 | Qoder / Anthropic |
|  | 当某类操作连续 3 次成功且步骤一致，提示用户"是否编译为确定性脚本"，生成 `make add-endpoint` 等 | Qoder 棘轮效应 |
| 多语言/多生态 | 先出 TS/Go 的参考实现 MVP（哪怕只有 AGENTS.md + Makefile 等价物），证明 SPEC 跨语言可复现 | SPEC §5 参考实现 |
| 度量看板 | 发布"PBH 合规性报告"样例：`validate` 通过率、常见失败项 Top5、阶段分布 | 从交付工具到交付洞察 |

---

## 7. 定位与叙事建议

### 7.1 三条值得押注的差异化

1. "阶段感知的 Harness"（Stage-Aware Harness） —— 行业里所有人都在做任务级状态（feature_list.json、progress.md），PBH 的 `init→plan→execute→evaluate→done` 是项目阶段级。只要把它从静态快照变成真状态机，并定义"每个阶段放宽/收紧哪些规则"（execute 抑制风格噪声、evaluate 严格拦截），这就是一条可以写进 SPEC 的原创条款，也是其他工具没有的概念。

2. 协议 + 校验器双资产 —— 单纯写规范没有壁垒（AGENTS.md 已是事实标准），"规范 + `validate` 机器判定 + `doctor` 环境诊断" 才有。建议把 `validate` 的输出做成可对外展示的合规报告（类似 Lighthouse 评分），这会成为最好的传播物料。

3. 三角闭环的数据资产 —— harness-init（播种）→ harness-lint（发现）→ harness-agent（修复）→ 回写规则。三者现在各做各的，一旦用 `.harness/trace/` 串起来，就形成了"越用越准"的飞轮。这正是行业公认的终局——"Harness 就是数据集，你捕获的 trajectory 才是竞争优势，而不再是提示词"（LangChain）。

### 7.2 一个需要警惕的陷阱

`docs/design.md` 的"不越界"原则是对的，但别让它变成不补位的理由。判断标准很简单：

> 如果某件事需要运行时才能做（调度子代理、压缩上下文、路由模型）→ 不做，交给生态。  
>     如果某件事只是把地基种进项目（规则文件、lint 脚本、verify 骨架、trace 目录、权限清单）→ 必须做，这正是"播种器"的本职。

按这条标准，本报告 6.x 里的所有建议都在边界内。

### 7.3 关于"Harness 要可拆卸"

腾讯云 [2648322](https://cloud.tencent.com.cn/developer/article/2648322) 提了一个容易被忽略的坑：Harness 必须可拆卸——模型变强后，今天的控制逻辑明天可能就是负担。对 PBH 的启示是：每一条新加的规则都应该带生效条件与退役条件（例如"当模型 X 在 Y 基准上达到 Z% 时，可移除本条"）。这一点若能写进 PBH-SPEC，同样是行业稀缺的。

---

## 8. 附录：参考资料清单

腾讯云开发者社区

- Agent 系列（三）：Harness Engineering — [https://cloud.tencent.com/developer/article/2647887](https://cloud.tencent.com/developer/article/2647887)

- Agent Harness：2026 年 AI 工程的核心范式 — [https://cloud.tencent.com/developer/article/2698416](https://cloud.tencent.com/developer/article/2698416)

- Harness Engineering：Agent 工程新范式 — [https://developer.cloud.tencent.com/article/2684699](https://developer.cloud.tencent.com/article/2684699)

- Harness Engineering 是什么？AI 编程工程化的三次进化 — [https://cloud.tencent.cn/developer/article/2699549](https://cloud.tencent.cn/developer/article/2699549)

- 别卷模型了！OpenAI 工程师都在偷偷用的 Harness — [https://cloud.tencent.com.cn/developer/article/2648322](https://cloud.tencent.com.cn/developer/article/2648322)

- 宋振华《后端学 agent harness》专栏 — [https://cloud.tencent.cn/developer/column/108078](https://cloud.tencent.cn/developer/column/108078)

阿里云开发者社区

- Qoder 工程实践：Harness Engineering 指南 — [https://developer.aliyun.com/article/1724843](https://developer.aliyun.com/article/1724843)

- 02｜Agent Harness 的核心组成 — [https://developer.aliyun.com/article/1740482](https://developer.aliyun.com/article/1740482)

- 一些 Harness Engineering 的实践 — [https://developer.aliyun.com/article/1718179](https://developer.aliyun.com/article/1718179)

- Harness Engineering 实战：用 AGENTS/ARCHITECTURE — [https://developer.aliyun.com/article/1745097](https://developer.aliyun.com/article/1745097)

- 如何给 Agent 写一份行为规范 — [https://developer.aliyun.com/article/1744762](https://developer.aliyun.com/article/1744762)

字节系（二手，降权）

- DeerFlow 2.0 架构复盘 — [https://juejin.cn/post/7621140573428940851](https://juejin.cn/post/7621140573428940851)

- DeerFlow 2.0 深度拆解 — [https://www.cnblogs.com/itech/p/20206290](https://www.cnblogs.com/itech/p/20206290)

- TRAE 架构解读 — [https://www.51cto.com/aigc/7748.html](https://www.51cto.com/aigc/7748.html)

国外一线（原站沙箱内不可达，经二手精读转述）

- Anthropic《Effective harnesses for long-running agents》— [https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

- OpenAI《Harness engineering: leveraging Codex in an agent-first world》— [https://openai.com/index/harness-engineering/](https://openai.com/index/harness-engineering/)

- Martin Fowler《Harness engineering for coding agent users》— [https://martinfowler.com/articles/harness-engineering.html](https://martinfowler.com/articles/harness-engineering.html)

- LangChain《Improving Deep Agents with harness engineering》— [https://langchain-blog.ghost.io/improving-deep-agents-with-harness-engineering/](https://langchain-blog.ghost.io/improving-deep-agents-with-harness-engineering/)

- LangChain《The Anatomy of an Agent Harness》— [https://langchain.com/blog/the-anatomy-of-an-agent-harness](https://langchain.com/blog/the-anatomy-of-an-agent-harness)

- Stripe《Minions: one-shot, end-to-end coding agents》— [https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)

- 上海 AI Lab《Self-Harness》— [https://arxiv.org/abs/2606.09498](https://arxiv.org/abs/2606.09498)

综合分析

- 万字讲透 Agent Harness 的十二大模块 — [https://zhuanlan.zhihu.com/p/2029220210800883392](https://zhuanlan.zhihu.com/p/2029220210800883392)

被分析项目

- Project-Bootstrap-Harness — [https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness)

- PBH-SPEC v2.0（中） — [https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/blob/master/docs/spec/PBH-SPEC.zh-CN.md](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/blob/master/docs/spec/PBH-SPEC.zh-CN.md)
