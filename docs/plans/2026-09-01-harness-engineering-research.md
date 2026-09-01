# Harness Engineering 一手资料调研与后续应对思路

> 调研日期：2026-09-01
> 调研对象：`Agent = Model + Harness` 范式下的一手来源，以及仓库根目录《PBH-harness-engineering-对标报告》的论断核实
> 产出位置：`docs/plans/2026-09-01-harness-engineering-research.md`（本文档）

---

## 1. 调研背景与方法

### 1.1 背景

本仓库（harness-init）是一个"协议播种器"：为 Python 项目脚手架注入 `AGENTS.md`、`make verify` 质量门禁等，遵循 `docs/spec/PBH-SPEC.md`，且明确不做 Agent 运行时（见 `docs/design.md` §2）。仓库根目录的《PBH-harness-engineering-对标报告》给出 PBH 加权分 33/100（行业基线 76）、定位内 41/100 的结论，但其大量表格单元格为空，且附录自承国外一线来源"原站沙箱内不可达，经二手精读转述"。

本调研的任务：逐个抓取 9 个指定一手来源的原文，补一手证据、核实报告中的关键数字、校正失真论断，并整理可落地的后续思路。

### 1.2 方法与可达性声明

- **直接抓取成功（一手原文）**：Martin Fowler、Anthropic、LangChain 两篇、Stripe。
- **经官方/可信镜像获取全文**：阿里云 Qoder 文章（原站 JS 渲染，经 53AI 全文转载镜像获取，与 GitCode/知乎/AI 星球多个镜像交叉一致）。
- **原文不可达，经多源交叉转述**：OpenAI 原文（403 拒绝，经 AIGC Camp 精读笔记 + Fowler 原文转引 + 多个中文精读交叉）；上海 AI Lab Self-Harness（arXiv 网络不可达，经论文团队官方投稿转载"量子位"全文 + 知乎逐表精读交叉）。
- **页面无法获取内容**：腾讯云《Agent 系列（三）》（多次抓取返回空内容，页面为 JS 渲染），相关论断仅沿用对标报告的转述并降级标注。

凡未直接读到原文的数字，均在正文与第 3 节核实表中显式标注证据等级。

---

## 2. 一手来源逐篇摘要

### 2.1 Martin Fowler / Birgitta Böckeler《Harness engineering for coding agent users》（2026-04-02，Thoughtworks）

来源：<https://martinfowler.com/articles/harness-engineering.html>（直接抓取，全文）

核心论断与原文关键句：

1. **范式定义（有界化）**："'Harness' 已成为指代 AI agent 中除模型本身以外一切的简写——Agent = Model + Harness。"作者将其收窄到"编码代理使用者"的有界上下文，区分三层同心圆：模型（核心）→ 代理构建者的内置 harness → **用户自建的外层 harness**（PBH 所处的正是这一层）。
2. **双目标**："一个构建良好的外层 harness 服务于两个目标：提高代理第一次就做对的概率，并提供一个在问题到达人眼之前自我纠正尽可能多问题的反馈回路。"
3. **分类学（Guides × Sensors × 两种执行方式）**：
   - Guides（前馈控制）：在代理行动前引导；Sensors（反馈控制）：在行动后观察并帮助自我纠正。
   - Computational（确定性、快、可靠）与 Inferential（语义分析、LLM 评审，慢且非确定）。
   - **与 PBH 最相关的一句**："当传感器产生为 LLM 消费而优化的信号时尤其强大，例如**包含自我纠正指令的自定义 linter 消息——一种正向的 prompt 注入**。"这为"lint 报错注入修复指令"提供了直接的一手依据。
   - 表格中明确举例：结构性测试（如 ArchUnit 检查模块边界）作为前馈/反馈的 computational 控制；AGENTS.md、Skills 作为 inferential 前馈。
4. **Steering loop（人的角色）**："每当某个问题多次发生，就应改进前馈与反馈控制，使该问题未来更不容易发生。"且"可以用 AI 来改进 harness：代理可以帮忙写结构性测试、从观察到的模式生成规则草案、脚手架化自定义 linter"。
5. **Keep quality left**：按成本/速度/关键性把检查分布到生命周期——快而廉价的在提交前跑（lint、快测试），昂贵的放到集成后管道（变异测试、深度评审）。
6. **三类调节对象**：Maintainability harness（最易，现有工具充足）/ Architecture fitness harness（fitness functions）/ **Behaviour harness（房间里的象）**："这给了 AI 生成的测试太多信任，目前还不够好"——即端到端功能验证是行业公认的未解难题，PBH 的"验证闭环太窄"短板正是全行业的痛点。
7. **Harnessability 与 Harness templates**："不是每个代码库都同样适合被 harness 化"；"大多数企业有几种覆盖 80% 需求的服务拓扑……这些可能演化为未来的 **harness 模板**：一捆把编码代理拴在某拓扑的结构、约定与技术栈上的 guides 与 sensors。团队可能部分基于已有哪些 harness 来挑选技术栈。"——**这是"播种器"赛道最有力的一手背书**：PBH 做的事正是 harness template 的雏形。
8. **对 OpenAI 的原文转引**（可作二手中的一手）："一个 OpenAI 团队记录了他们的 harness 样子：由自定义 linters 和结构性测试强制实施的分层架构，以及周期性'垃圾回收'——扫描漂移并让代理建议修复。他们的结论：'我们最难的挑战现在集中在设计环境、反馈回路与控制系统上。'"
9. **janitor army**："Thoughtworks 团队用 computational 与 inferential 传感器混合应对架构漂移，例如用'清洁工军团'提升代码质量。"

### 2.2 OpenAI《Harness engineering: leveraging Codex in an agent-first world》（2026-02-11，作者 Ryan Lopopolo）

来源：<https://openai.com/index/harness-engineering/>（**原文 403 不可达**，以下经 AIGC Camp 精读笔记 + Fowler 原文转引 + 腾讯云/头条多个精读交叉验证）

核心论断：

1. **实验设定**：团队约束自己不手写产品代码，5 个月从空仓库构建并发布一个内部产品，约 100 万行代码（应用逻辑、测试、CI、文档、可观测性、内部工具）100% 由 Codex 生成，合并约 1500 个 PR（多源一致转述）。
2. **人的角色转变**："工程师从直接写代码转向设计环境、表达意图、构建反馈循环"（AIGC Camp 精读）。Fowler 原文转引的 OpenAI 原话："Our most difficult challenges now center on designing environments, feedback loops, and control systems."
3. **AGENTS.md 是地图不是百科**（多源一致转述的原话）："Instead of treating AGENTS.md as the encyclopedia, we treat it as the table of contents."——约 100 行的入口文件只做导航，深层内容（架构、规格、计划、质量标准、安全）放 `docs/`，仓库内版本化文档是 System of Record。
4. **机械约束**：分层架构由自定义 linters 与结构性测试强制；周期性 "garbage collection"（doc-gardening/janitor 式代理扫描漂移并提出修复）——此两点经 Fowler 原文转引，可信度较高。
5. **可靠性依赖**："可靠输出依赖 repo 结构、测试、文档、CI、任务描述和错误反馈；代码生成比例越大，越需要更强的验证和回滚机制"（AIGC Camp 精读）。

> ⚠️ 注意：报告中"32 KiB 上限"并非出自此文，而是 Codex 产品配置 `projectdocmaxbytes` 默认值 32768 字节（见 3.1 校正）。

### 2.3 Anthropic《Effective harnesses for long-running agents》（Justin Young）

来源：<https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>（直接抓取，全文）

核心论断与原文关键句：

1. **问题定义**："长程代理的核心挑战是它们必须以离散会话工作，每个新会话开始时对之前发生的一切没有记忆。"类比：轮班工程师交接，每班新工程师没有前一班的记忆。
2. **两件套方案**：
   - **Initializer agent**（仅第一个会话）："使用专门提示要求模型搭建初始环境：一个 `init.sh` 脚本、一个记录各代理做了什么的 `claude-progress.txt` 文件、以及展示新增文件的初始 git commit。"
   - **Coding agent**（后续每个会话）："被要求取得增量进展，然后留下结构化更新。"脚注明确：两者只是初始提示不同的同一代理。
3. **Feature list（JSON 而非 Markdown）**："这些特性最初全部标记为 'failing'……我们提示编码代理只能通过修改 `passes` 字段来编辑这个文件，并使用强硬措辞如 **'删除或修改测试是不可接受的，因为这可能导致功能缺失或带 bug'**……经实验后我们确定使用 JSON，因为模型相对 Markdown 文件更不容易不当地修改或覆盖 JSON 文件。"（claude.ai 克隆案例中超过 200 个特性条目。）
4. **增量进展 + 环境清洁**："每次只做一个特性……我们发现引出这种行为最好的方式是要求模型用描述性 commit message 提交进展并在 progress 文件中写总结。这让模型可以用 git 回滚坏的代码改动、恢复代码库的工作状态。"
5. **端到端验证**："Claude 倾向于在没有适当测试的情况下把特性标记为完成……一旦明确提示使用浏览器自动化工具并像人类用户一样做所有测试，Claude 在端到端验证特性上大多做得很好。"（Puppeteer MCP。）
6. **会话开场固定步骤**：原文只列举了 **3 步**（`pwd` → 读 git log 与 progress 文件 → 读 feature list 选最高优先级未完成特性），另建议先跑 `init.sh` 启动开发服务器并做基础端到端测试。（对标报告称"每轮开工 7 步固定动作"与原文不符，见 3.1。）
7. **失败模式表**：过早宣布项目完成 / 留下带 bug 环境 / 过早标记特性完成 / 浪费时间搞清楚如何运行应用——各自对应 initializer 与 coding agent 的行为设计。

### 2.4 LangChain《Improving Deep Agents with harness engineering》（2026-02）

来源：<https://langchain-blog.ghost.io/improving-deep-agents-with-harness-engineering/>（直接抓取，全文）

核心论断与原文关键句：

1. **头条结果（原文）**："我们用简单配方把 deepagents-cli 在 Terminal Bench 2.0 上迭代提升了 13.7 分，从 52.8 到 66.5。我们只调了 harness，模型固定为 gpt-5.2-codex。""我们的编码代理在 Terminal Bench 2.0 上从 Top 30 进了 Top 5。"
2. **三个旋钮**：刻意压缩优化空间，只动 System Prompt、Tools、Middleware（"我们对包裹模型调用与工具调用的钩子的称呼"）。
3. **Trace Analyzer Skill**："我们想让 trace 分析可重复，所以做成了 Agent Skill：从 LangSmith 拉实验 traces → 派生并行错误分析代理 → 主代理综合发现与建议……这类似针对前轮错误的 boosting。"
4. **Build & Self-Verify**："最常见的失败模式是代理写了方案、重读自己的代码、确认看起来没问题、然后停止。"解法：四步法（Planning & Discovery → Build → Verify → Fix）+ **PreCompletionChecklistMiddleware**："一个在代理退出前拦截它、提醒它对 Task spec 跑一遍验证的中间件……类似 Ralph Wiggum Loop，用钩子强制代理在退出时继续执行，我们用于验证。"
5. **环境上下文注入**：LocalContextMiddleware 启动时映射目录结构、探测工具链；时间预算警告（"代理在时间估计上出了名地差"）。"代理对环境、约束与评估标准知道得越多，就越能自主地自我指导工作。"
6. **LoopDetectionMiddleware（软熔断）**："通过工具调用钩子跟踪每文件编辑计数，对同一文件 N 次编辑后注入'考虑换一种方法'的上下文。"并明确其临时性："**这些护栏会随着模型改进而大概率不再必要**，但今天有帮助。"（"可拆卸"原则的一手依据。）
7. **Reasoning sandwich**：xhigh-high-xhigh 基线；全程 xhigh 反而因超时只得 53.9%（high 为 63.6%）。
8. **模型适配**："为任务调适 harness……Claude Opus 4.6 在早期 harness 版本下得 59.6%，有竞争力但差于 Codex，因为我们没对 Claude 跑同样的改进循环。"

### 2.5 LangChain《The Anatomy of an Agent Harness》（Vivek Trivedy，2026-03-10）

来源：<https://langchain.com/blog/the-anatomy-of-an-agent-harness>（直接抓取，全文）

核心论断与原文关键句：

1. **定义（原文）**："Agent = Model + Harness. 如果你不是模型，你就是 harness。""harness 是不属于模型本身的每一段代码、配置与执行逻辑"：System Prompts；Tools/Skills/MCPs 及其描述；捆绑基础设施（文件系统、沙箱、浏览器）；编排逻辑（子代理生成、交接、模型路由）；**确定性执行的 Hooks/Middleware（compaction、continuation、lint 检查）**。
2. **文件系统是最基础的 harness 原语**："代理获得工作区……工作可增量卸载而不是全塞进上下文……文件系统是天然的协作面。**Git 为文件系统加上版本化，让代理能跟踪工作、回滚错误、分支实验。**"
3. **沙箱与安全**："harness 可以允许列表化命令并强制网络隔离。"
4. **记忆**："harness 支持像 AGENTS.md 这样的记忆文件标准，在代理启动时注入上下文……这是一种持续学习形式。"
5. **对抗 Context Rot**：compaction（上下文近满时摘要卸载）、工具输出卸载（保留头尾、全文落盘）、Skills 渐进式披露。"今天的 harness 很大程度上是良好 context engineering 的投递机制。"
6. **Ralph Loop**："一个通过钩子拦截模型退出尝试、在干净上下文窗口中重新注入原始提示、强制代理对着完成目标继续工作的 harness 模式。"
7. **Harness 与模型共同进化**："有用的原语被发现、加入 harness、然后在训练下一代模型时使用……但你这任务最好的 harness 不一定是模型后训练所用的那个……**Opus 4.6 在 Claude Code 中的得分远低于在其他 harness 中的得分。**"
8. **未来方向**："分析自己的 traces 以识别并修复 harness 级失败模式的代理"；"harness 会越来越不重要吗？不——配置良好的环境、正确的工具、持久状态与验证回路让任何模型更高效，无论其基础智能。"

### 2.6 Stripe《Minions: Stripe's one-shot, end-to-end coding agents》（Alistair Gray，2026-02-09）

来源：<https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents>（直接抓取，全文）

核心论断与原文关键句：

1. **规模**："每周超过一千个在 Stripe 合并的 pull request 完全由 minion 产出……它们被人类评审，但不含人类写的代码。"典型流程：Slack 消息发起 → 无人值守 → 通过 CI 的 PR。
2. **为何自建**："在 Stripe 这种规模、复杂度与成熟度的代码库上迭代本质上更难……minion 与人类工程师使用同一套开发者工具：**如果它对人类好，它对 LLM 也好。**"
3. **devbox 预热隔离**："Minion 运行始于一个隔离的开发者环境——'devbox'……devbox 被预热，10 秒内即可启动，预载 Stripe 代码与服务。它们与生产资源和互联网隔离……这也给了并行能力，**而不用像 git worktrees 那样——在 Stripe 的规模下无法扩展。**"
4. **确定性代码穿插代理循环**："我们以有主见的方式定制了编排流程，把代理循环与确定性代码——git 操作、lint、测试等——交织，使 minion 运行混合了代理的创造力与**它们永远会完成 Stripe 必需步骤（如 linters）的保证**。"
5. **条件化规则**："对 Stripe 来说拥有许多无条件规则是不现实的，所以几乎所有代理规则都基于子目录有条件地应用。"（规则文件与 Cursor/Claude Code 共用。）
6. **左移反馈**："第一道防线是一个自动化本地可执行体，用启发式选择并在每次 git push 时自动运行选定的 lint。**这花不到 5 秒。**""任何会在 CI 失败的 lint 步骤最好在 IDE 或 git push 时就强制，并立刻呈现给工程师。"
7. **CI 断路器（原文）**："我们最多只有两轮 CI……'通常一轮、最多两轮——且只在本地修完一切能修的之后'取得了好的平衡。"（300 万+ 测试池中选择性运行；失败测试若有 autofix 自动应用，否则退回 minion 修复。）
8. **上下文预水合**："我们在 minion 运行开始前确定性地对看似相关的链接运行相关 MCP 工具，以更好地水合上下文。"（中心化 MCP 服务器 Toolshed，400+ 工具，可配置但精选的子集。）

### 2.7 上海 AI Lab《Self-Harness》（arXiv 2606.09498，2026-06）

来源：<https://arxiv.org/abs/2606.09498>（**网络不可达**，以下经论文团队官方投稿"量子位"全文转载（新浪/搜狐/网易多平台一致）+ 知乎逐表精读交叉验证）

核心论断：

1. **范式定位**：Human Harness Engineering（人工修订）→ Meta-Harness（更强外部代理指导较弱代理）→ **Self-Harness（代理改进其自身的运行 harness）**，消除对外部指导的依赖。
2. **机制（核心闭环）**：固定模型在现有 harness 下执行 → 基于自身执行证据（traces）提出**有界的**（bounded）harness 修改 → 回归测试门控（held-in 提升且 held-out 不降才可晋升）→ 合并或回滚。"每次改动都经回归测试门控，可记录、可复现、可回退。"（量子位转载）
3. **实验设置**：minimal 起始 harness + 三个模型家族（MiniMax M2.5、Qwen3.5-35B-A3B、GLM-5）在 Terminal-Bench-2.0 上。
4. **数字**（知乎精读逐表转述）：
   - held-in pass rate：M2.5 43.0%→50.0%；Qwen3.5 15.1%→36.0%；GLM-5 47.7%→57.0%。
   - held-out pass rate：M2.5 40.5%→61.9%；Qwen3.5 23.8%→38.1%；GLM-5 42.9%→57.1%。
   - 官方头条口径（量子位）："Qwen3.5-35B-A3B 总提升 104%，MiniMax M2.5 提升 28%，GLM-5 提升 24%。"（头条口径与分切片口径的换算关系无法在原文不可达下核对，见 3.1。）
5. **模型特异性**：同一框架在三个模型上挖出三种完全不同的弱点（M2.5 无限探索超时；Qwen 工具报错后反复重试同一操作；GLM 长时间下载耗尽 token 预算）——"对一个模型有效的 harness 对另一个未必最优"，**harness 设计本质上是模型相关的**。
6. **编辑不止于 prompt**：可引入更宽的结构机制（如 subagent 分解、middleware 创建）。
7. **自我批判**：论文自认改进是有界的、接受编辑可能仍反映 benchmark 特定失效模式；知乎精读指出其缺配对 bootstrap 置信区间与多次重跑方差。

### 2.8 阿里云《Qoder 工程实践：Harness Engineering 指南》（2026-04-03）

来源：<https://developer.aliyun.com/article/1724843>（原站 JS 渲染，经 53AI 全文镜像抓取，并与知乎专栏、GitCode、AI 星球三个镜像交叉一致）

核心论断与原文关键句：

1. **核心思路**："与其教 Agent 怎么做，不如让它自己验证做得对不对。靠代码、linter、测试来保证正确性，而不是靠 LLM 的'直觉'。……就像 CI/CD 对人类开发者的作用——自动拦截问题。只不过这次拦截的时机更早，不是合并前，而是**写代码前**。"
2. **仓库是 Agent 的操作系统**：仓库是唯一事实来源；"AGENTS.md 应该是地图，不是手册——控制在 ~100 行，只做索引和指路，详细内容放在 `docs/` 目录里按需加载。……当一切都重要时，什么都不重要。"
3. **层级编号**："把自然依赖方向编码为层级编号——Layer 0 是类型定义……规则就一条：高层可以 import 低层，反过来不行。在这个边界之内怎么实现，随便。中心化约束，本地自治。"
4. **预验证（原文数字）**："当一个层级违反在 50 行代码写完后才被 linter 抓到，修复代价很大——撤销改动、重新设计，**差不多要消耗 10 次 tool call。而如果在写代码前先问一句'这样做合法吗'，两次交互就够了**……**层级违反是 Agent 翻车的头号原因。**"（触发条件：在新位置创建文件、添加跨包 import。）
5. **lint 报错质量**："一条 `Forbidden import in core/types/user.go` 看完不知道怎么办；但如果改成 '…Layer 0 packages must have NO internal dependencies. Fix: Move config-dependent logic to a higher layer…'——什么规则违反了、为什么是问题、怎么修，全在里面。**一条好的报错本身就是一次教学。**"
6. **四段验证管道**："build → lint-arch → test → verify……verify 步骤是项目级别的端到端功能验证——不是'函数返回值对不对'，而是'用户执行这个操作，最终结果对不对'。"项目缺端到端能力时，引导创建 **verify skill**：识别核心用户路径（如"创建用户→登录→查看资料"），编码成可执行验证脚本骨架放 `scripts/verify/`。
7. **修复循环熔断**："如果同一个错误转了 3 圈还没过，就别让 Agent 继续挣扎了，停下来交给人。"
8. **协调者/执行者分离**："中等复杂度以上的任务，**协调者绝不写代码**……如果你发现协调者正在用 Edit 或 Write 工具修改源代码，立刻停下来，启动子代理。没有例外。"结构性变更在 Git Worktree 隔离执行。
9. **检查点**："每完成一个阶段、跑过验证就存档，**包括已有的架构决策**……没有它，新 Agent 可能走一条完全不同的路。"
10. **自我进化闭环**："每次验证失败都被结构化地保存到 `harness/trace/failures/`。Critic 脚本定期分析这些记录，找出模式和根因……然后 Refiner 根据建议去更新 Harness……整个循环：Agent 执行 → 验证抓到问题 → Critic 分析模式 → Refiner 更新规则 → 下一个 Agent 受益。"
11. **记忆三分**："情景记忆记录具体事件和教训……程序记忆记录成功的操作步骤……失败记忆专门供 Critic 分析用。每次任务开始时，executor 会查询相关记忆。"
12. **轨迹编译与棘轮**："当同一类任务被成功执行了三次以上，而且步骤高度一致……这个模式就可以被'编译'成一个确定性脚本，像 `make add-endpoint NAME=foo`……每个被编译的成功模式都变成了永久基础设施……**竞争优势不再是 Prompt，而是 Trajectory。**"
13. **审计口径**：creator 首次运行按文档覆盖率、lint 规则覆盖率等维度打 0-100 分（0-20 裸奔 / 21-70 有基础有缺口 / 71+ 健康）。目录布局：`docs/`（ARCHITECTURE/DEVELOPMENT/PRODUCT_SENSE/design-docs/exec-plans）+ `scripts/`（lint-deps/lint-quality/verify/validate.py）+ `harness/`（tasks/trace/memory）。

### 2.9 腾讯云《Agent 系列（三）：Harness Engineering》（2647887）

来源：<https://cloud.tencent.com/developer/article/2647887>（**多次抓取返回空内容**，页面为 JS 渲染，未能获取正文）

处理：本调研未能获得该文一手内容，相关论断（如"线束工程"译名、三代演进表述、"Harness 必须可拆卸"等）仅存在于对标报告的转述中，**不作为本调研的证据基础**。其中"可拆卸"论点获得了独立的一手旁证（见 4.3）。

### 2.10 补充：2026 年进展扫描（WebSearch）

- **Terminal-Bench 2.1 已发布**（Stanford + Laude Institute，基于 Z.ai 的 2.0 Verified 优化）；榜首已达 ~88%（GPT-5.6 Sol 88.8），2.0 榜首约 82.7%（GPT-5.5）。来源：datalearner.com 基准页。
- **第三方 harness 本身成为刷榜变量**：ForgeCode 作为第三方 harness 占据 Terminal-Bench 2.0 前 6 名中的 3 席（靠跨模型路由）；同一模型不同 harness 差距显著——Opus 4.5 配 Terminus 2 为 57.8%，配 Claude Code 为 52.1%。来源：uncoveralpha.com、toutiao 精读。
- **Harness 平台化/开源化**：OpenAI 于 2026-08-19 发布《Codex as a platform》，将 Codex Harness 作为开放能力（codex exec / SDK / App Server 三条集成路径）；DeepSeek Harness 同期开源（Cordis 内核）。
- **可拆卸性的一手旁证**：Boris Cherny（Claude Code 创造者）："Prompt、Skill、Tools、Harness 甚至 Eval 都是会折旧的资产，建议大约每六个月清空自己的 CLAUDE.md、skills 和 hooks，重新观察新模型到底还需要什么"（《We Cut 80% of Claude Code's Prompt》访谈，2026-08 转述）；LangChain 原文亦称护栏"会随着模型改进而大概率不再必要"（2.4 §6）。
- **Context Engineering 与 Harness 的关系**："Context Engineering 管信息层（该让模型看到什么），Harness Engineering 管结构层（模型在几十轮里怎么持续把事做对）"；"Context Engineering 和 SDD 是 Harness Engineering 的两个核心组成部分"（InfoQ，2026-06）。
- **AGENTS.md 演进**：已是跨工具事实标准（agents.md，支持子目录嵌套）；对 2500+ 仓库的调研显示超过约 150 行收益递减、推理成本上升 20-23%（atlan 综述）；最佳实践是"迭代长出来而非一次规划"（Matt Nigh）。

---

## 3. 数字核实表

| # | 对标报告中的论断 | 核实结果 | 一手证据 | 证据等级 |
| --- | --- | --- | --- | --- |
| 1 | LangChain Terminal-Bench 2.0 得分 52.8%→66.5%（+13.7pp），不换模型（gpt-5.2-codex），排名 30 名开外→前 5 | ✅ **属实** | LangChain 博客原文（2.4 §1）逐字吻合 | 一手原文 |
| 2 | Self-Harness：Qwen3.5-35B-A3B +104%、MiniMax M2.5 +28%、GLM-5 +24% | ⚠️ **方向属实，口径存疑** | 论文团队官方投稿转载（量子位）一致使用该三数为"总提升"；知乎精读给出的分切片数字（held-in/held-out，见 2.7 §4）与头条口径的换算关系无法核对（arXiv 不可达） | 官方转载 + 交叉精读（原文不可达） |
| 3 | Boris Cherny"验证质量提升 2–3 倍" | ✅ **属实**（原话为最终结果质量 2-3x） | "give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality of the final result"（2026-01 工作流分享，多个独立来源一致） | 多源一致的公开发言转述 |
| 4 | OpenAI AGENTS.md ~100 行 | ✅ **属实** | "Instead of treating AGENTS.md as the encyclopedia, we treat it as the table of contents"（多源一致）；Qoder 原文同口径"~100 行，只做索引" | 二手交叉（原文 403） |
| 5 | OpenAI "Codex 上限 32 KiB" | ⚠️ **事实存在但归因不准** | 32 KiB 是 Codex 配置项 `projectdocmaxbytes` 的默认值（32768 字节，超出静默丢弃），属产品文档而非 harness 文章论断；且官方建议的应对是裁剪分层而非调大上限 | 产品文档（非目标文章） |
| 6 | "事后 10 次 tool call vs 事前 2 次交互" | ✅ **属实** | Qoder 原文逐字吻合："差不多要消耗 10 次 tool call。而如果在写代码前先问一句……两次交互就够了"（2.8 §4） | 一手镜像全文 |
| 7 | "层级违反是 Agent 翻车的头号原因" | ✅ **属实** | Qoder 原文逐字吻合（2.8 §4） | 一手镜像全文 |
| 8 | Anthropic "每轮开工 7 步固定动作" | ❌ **与原文不符** | 原文只列 3 步 + 启动开发服务器跑基础测试（2.3 §6），"7 步"无出处 | 一手原文 |
| 9 | Anthropic ">200 项 feature list、JSON 而非 Markdown" | ✅ **属实** | 原文："over 200 features"；"we landed on using JSON"（2.3 §3） | 一手原文 |
| 10 | "PreCompletionChecklist，最多强制验证 3 次" | ⚠️ **前半属实，后半无出处** | 中间件存在且机制描述吻合（2.4 §4），但"最多 3 次"未见于原文 | 一手原文（部分） |
| 11 | "CI 2 轮硬熔断"（Stripe） | ✅ **属实** | 原文："often one, at most two, CI runs"（2.6 §7） | 一手原文 |
| 12 | "本地门禁 <5 秒"（Stripe） | ✅ **属实** | 原文："This takes less than five seconds"（2.6 §6） | 一手原文 |
| 13 | OpenAI "接 Chrome DevTools 协议 + LogQL/PromQL"；LangChain "LangSmith trace 做失败模式分析" | ⚠️ 前者**无法核实**（原文不可达）；后者✅属实 | LangSmith traces 分析见 2.4 §3 | 混合 |
| 14 | 腾讯云"三代演进：Prompt→Context→Harness" | ✅ 有多个独立来源支撑 | 2.10 补充扫描 | 多源一致 |
| 15 | 阿里云审计口径"0-20 裸奔 / 21-70 有基础有缺口 / 71+ 健康" | ✅ **属实** | Qoder 原文逐字吻合（2.8 §13） | 一手镜像全文 |

---

## 4. 对标报告校正

### 4.1 明确与一手原文不符的论断

1. **Anthropic "每轮开工 7 步固定动作"（§2.2 矩阵）**：原文只给出 3 步定位流程（pwd / 读 git log+progress / 读 feature list 选特性）外加"先跑 init.sh 起服务并做基础端到端测试"。应改写为"固定的会话开场协议（定位→读状态→选特性→先测后写）"。
2. **"OpenAI：Codex 上限 32 KiB"作为 harness 文章条款（§2.3 checklist 第 1 条）**：该数字出自 Codex 产品配置（`projectdocmaxbytes` 默认 32768），不是《Harness engineering》文章的论断。文章真正的条款是"~100 行地图式 AGENTS.md + docs/ 承载深层内容"。报告把两者并列为同一出处，属归因失真。
3. **"PreCompletionChecklist，最多强制验证 3 次"（§2.3 第 8 条）**：原文只有"退出前拦截并提醒对 Task spec 跑验证"，"最多 3 次"无任何出处，疑似与 Stripe"最多两轮 CI"或 Qoder"3 圈熔断"混淆。
4. **Self-Harness 数字表述**："只改 Harness：Qwen3.5 +104%、M2.5 +28%、GLM-5 +24%"是论文团队的头条"总提升"口径；知乎精读显示 held-in 上 Qwen 实际为 15.1%→36.0%（相对 +138%）、held-out 为 23.8%→38.1%（+60.1%）。报告直接引用头条数不算错，但**不应表述为"同等口径的可比提升"**，对外材料建议附口径说明。

### 4.2 二手转述但经核实成立（可放心引用）的论断

- OpenAI 实验规模（3 名工程师、5 个月、~100 万行、~1500 PR、100% 生成）——多源一致。
- OpenAI 分层架构 lint + 垃圾回收——经 Fowler 原文转引（一手转一手）。
- Stripe devbox 预热/隔离、"worktree 在 Stripe 规模不可行"、选择性测试 + autofix——一手原文确认，报告"子代理隔离：worktree（小团队）/ 预热 devbox（大规模）"的概括方向正确。
- Qoder 全部机制（层级编号、预验证、四段管道、协调者/执行者、记忆三分、Critic→Refiner、轨迹编译）——一手镜像全文确认。

### 4.3 报告的判断性结论，经一手证据后需要加强的

1. **"播种器"定位的行业合法性比报告说的更强**：Fowler 原文明确预言 "harness templates"（2.1 §7），PBH 正是该概念的实现雏形；报告可以更大胆地把这个一手出处写进叙事。
2. **"可拆卸"有一手依据，不必只靠腾讯云转述**：LangChain 原文（护栏随模型改进而失效）+ Boris Cherny（harness 是会折旧的资产、每 6 个月清空重来）+ Anthropic feature list 的"强措辞但可演化"，三重一手旁证。
3. **"端到端功能验证（behaviour harness）"是全行业未解之谜**（Fowler 原话"还不够好"）：报告的"验证闭环太窄"批评成立，但应同时指出：PBH 若只做播种，其合理目标是**种下 verify 的骨架与接口**（Qoder verify skill 模式），而非承诺解决 behaviour harness 本身。

---

## 5. 行业机制清单（含"播种范畴"判定）

判定标准（沿用 `docs/design.md` "PBH 三问"）：**播种** = 把文件/脚本/目录结构/协议条款种进生成项目，无需 Agent 运行时；**运行时** = 需要调度、拦截、压缩上下文等执行期能力。

| # | 机制 | 一手出处 | 实现要点 | 播种？ |
| --- | --- | --- | --- | --- |
| 1 | 地图式 AGENTS.md（~100 行入口 + docs/ 深层） | OpenAI（2.2）、Qoder（2.8 §2） | 入口只做导航与命令索引；深层知识放 `docs/` 按需加载；定期裁剪（>150 行收益递减） | ✅ 播种 |
| 2 | 分层依赖 lint（Layer 0-4，高层可 import 低层反之不行） | Qoder（2.8 §3）、Fowler（ArchUnit 例，2.1 §3）、OpenAI（经 Fowler 转引） | 扫描 import 语句；层级映射表版本化入仓；规则覆盖全部包 | ✅ 播种（脚本 + 映射表） |
| 3 | 预验证脚本（写代码前问"这样做合法吗"） | Qoder（2.8 §4） | `verify_action.py --action "create file X / import A from B"`，输出 VALID/INVALID + 修复建议 | ✅ 播种（脚本本身）；"执行时调用"靠 AGENTS.md 引导 |
| 4 | lint 报错注入修复指令（"正向 prompt 注入"） | Fowler（2.1 §3）、Qoder（2.8 §5） | 报错格式：违反了什么规则 + 为什么是问题 + 怎么修（Fix: …） | ✅ 播种（lint 脚本的报错文案模板） |
| 5 | 四段验证管道（build → lint-arch → test → verify） | Qoder（2.8 §6） | `make verify` 扩展为四段语义；顺序不可乱（编译不过不往下走） | ✅ 播种（Makefile 条款 + SPEC） |
| 6 | verify skill / 端到端验证骨架（核心用户路径编码成脚本） | Qoder（2.8 §6）、Anthropic（像真实用户一样测试，2.3 §5） | `scripts/verify/` 骨架 + 断言占位；引导用户把"创建用户→登录→查看资料"类路径写成可执行脚本 | ✅ 播种（骨架 + 引导文档） |
| 7 | 预完成拦截（退出前强制对照 spec 验证） | LangChain（2.4 §4）、Boris Cherny（2-3x） | 中间件钩子在代理退出前提醒验证 | ❌ 运行时；但可播种"完成前自检清单"条款进 AGENTS.md/CLAUDE.md 作为 inferential 等价物 |
| 8 | 循环检测软熔断（同文件 N 次编辑后提示换思路） | LangChain（2.4 §6） | 工具调用钩子跟踪每文件编辑计数 | ❌ 运行时；可拆卸性示范（模型变强即退役） |
| 9 | CI 硬断路器（最多两轮；本地先修完再上 CI） | Stripe（2.6 §7） | CI 策略文档 + autofix 优先 | ✅ 播种（策略写进 AGENTS.md §5 Critical Rules + CI 工作流注释） |
| 10 | 左移反馈（<5 秒本地门禁；push 前跑相关 lint） | Stripe（2.6 §6）、Fowler keep-quality-left（2.1 §5） | pre-push 钩子按启发式选 lint；`make verify` 快路径 | ✅ 播种（pre-push 脚本，仓库已有雏形） |
| 11 | 修复循环熔断（同一错误 3 圈未过即停手交人） | Qoder（2.8 §7）、PBH AGENTS.md 已有（"Max 2 auto-fix attempts"） | 熔断阈值写进协议条款 | ✅ 播种（条款）；执行靠代理自觉/运行时 |
| 12 | 会话开场协议（定位→读状态→选任务→先测后写） | Anthropic（2.3 §6）、Qoder executor 工作流 | AGENTS.md §3 Session Protocol（PBH 已有雏形）+ 生成项目的对应章节 | ✅ 播种（条款模板） |
| 13 | 增量进展 + 描述性 commit + progress 文件（可回滚恢复） | Anthropic（2.3 §4） | progress 文件 + "每步提交、坏改动可 git revert" 条款 | ✅ 播种（`.harness/progress.json` 已有，补行为条款） |
| 14 | 结构化任务清单（JSON 而非 Markdown、passes 字段、禁删禁改测试） | Anthropic（2.3 §3） | `feature_list.json` 骨架 + "不得删除或修改测试"强措辞 | ✅ 播种（文件骨架 + 条款） |
| 15 | 检查点（每阶段验证后存档，携带架构决策） | Qoder（2.8 §9） | 检查点文件格式（含已做架构决策）放 `.harness/`；推进动作留给编排器 | ✅ 播种（目录 + 格式）；自动推进 ❌ 运行时 |
| 16 | 协调者/执行者分离、结构性变更 worktree 隔离 | Qoder（2.8 §8）、LangChain（subagent）、Stripe（devbox 为大规模替代） | 协作模式条款 + worktree 操作指引脚本化 | ✅ 播种（条款 + 脚本）；调度 ❌ 运行时 |
| 17 | 记忆三分（情景/程序/失败） | Qoder（2.8 §11）、LangChain（AGENTS.md 记忆标准，2.5 §4） | `.harness/memory/{episodic,procedural,failures}.md` + 读写约定条款 | ✅ 播种（目录 + 格式 + 条款）；按相关性注入 ❌ 运行时 |
| 18 | trace 落盘（验证失败结构化存储） | Qoder（2.8 §10）、LangChain（LangSmith traces） | `.harness/trace/failures/` + `validate --json` 落盘 | ✅ 播种（目录 + 工具输出改造） |
| 19 | Critic → Refiner 自我进化回路 | Qoder（2.8 §10）、Self-Harness（2.7 §2）、LangChain（trace 分析 skill） | Critic 分析失败模式 → 提出规则修改 → 门控验证 → 更新 | ❌ 运行时/生态工具（harness-lint/agent 的职责）；可播种的是 **接口与目录约定** |
| 20 | 轨迹编译为确定性脚本（`make add-endpoint`，棘轮效应） | Qoder（2.8 §12） | 重复模式识别是运行时；但"编译产物"是 Makefile 目标 | ✅ 播种（Makefile 目标模式库）；识别 ❌ 运行时 |
| 21 | 权限/命令分级清单 | LangChain 沙箱 allow-list（2.5 §3） | `harness/permissions.md`：白/黑名单 + 需人工确认清单 | ✅ 播种 |
| 22 | 可拆卸规则（每条规则带生效/退役条件） | LangChain（2.4 §6）、Boris Cherny（2.10 补充） | 规则元数据：来源、生效条件、退役条件、上次复核日期；半年复核节奏 | ✅ 播种（条款格式，可写进 SPEC） |
| 23 | 文档垃圾回收（doc-gardening / janitor army） | OpenAI（经 Fowler 转引）、Fowler（2.1 §9） | 定期偏差扫描清单 + 清理任务模板 | ✅ 播种（清单模板 + tasks/ 惯例） |
| 24 | 环境上下文注入（启动时探测目录/工具链） | LangChain（2.4 §5） | LocalContextMiddleware 类 | ❌ 运行时；但可播种 `docs/DEVELOPMENT.md`（命令/工具链清单）降低其需求 |
| 25 | 上下文预算声明 | Qoder（2.8 §2）、atlan 调研（>150 行收益递减） | AGENTS.md ≤100 行硬约束（PBH 已有 ≤80）+ 推广为"每次注入预算" | ✅ 播种（条款） |

小结：**25 条机制中约 19 条的全部或部分落在播种范畴**，其中 #2/#3/#4/#5/#6（机械约束 + 验证扩展）与 #17/#18（记忆与 trace 目录）是当前 PBH 完全缺失、且与运行时无关的纯播种项——这印证了对标报告"最大短板是确定性机械约束"的判断，且证明这些短板可在不违背"PBH 三问"的前提下修复。

---

## 6. 后续应对思路路线图

边界提醒（来自 `docs/design.md`）：PBH 只做播种不做运行时；凡需要调度/拦截/压缩上下文的，种"接口与目录约定"即可，执行留给生态工具。所有新规则按机制 #22 附生效/退役条件。

### 6.1 近期（约 2 周）：修正确性缺陷 + 对齐已核实的一手事实

| # | 动作 | 一手依据 |
| --- | --- | --- |
| N1 | 落实对标报告 P0 清单（IDE 适配文件按 `project_type` 渲染、4 模板 × 2 模式全部 `make verify` 通过、修/删 `.pre-commit-config.yaml` 等）——开箱即坏的项目无法承载任何新机制 | 报告 §5；Fowler "harnessability：greenfield 应把可 harness 性从第一天烤进去"（2.1 §8） |
| N2 | 校正对外材料中的失真数字：Anthropic "7 步"→"3 步定位协议"；"32KiB"归因改为 Codex 配置；Self-Harness 数字补口径说明 | 本文 §4.1 |
| N3 | `validate --json` + 落盘 `.harness/trace/validate-<ts>.json`（在 `validators/_base.py` 的 `ValidationResult` 之上加序列化，改动极小） | Qoder（2.8 §10 trace 落盘）、LangChain（"Traces 是反馈信号"，2.4 实践要点 3） |
| N4 | AGENTS.md 模板条款补"完成前自检"：声明完成前必须对照任务规格重跑 `make verify` 并逐条核对（inferential 版的 #7） | LangChain PreCompletionChecklist（2.4 §4）、Boris 2-3x（#3） |
| N5 | AGENTS.md/CLAUDE.md 补"同错误 2-3 次未修复即停手上报"熔断条款（现 `AGENTS.md` 已有 "auto-fix ≤2"，扩展到生成项目模板） | Qoder（2.8 §7）、Stripe "最多两轮"（2.6 §7） |

### 6.2 中期（约 1 个月）：补机械约束层（对标报告最大短板，全部在播种范畴内）

| # | 动作 | 一手依据 |
| --- | --- | --- |
| M1 | 播种分层依赖 lint：`scripts/lint_deps.py`（扫描 import，层级映射表放 `docs/ARCHITECTURE.md` 或 `.harness/layers.json`），并接入 `make verify` | Qoder（2.8 §3）、Fowler ArchUnit 例（2.1 §3）、OpenAI 分层强制（经 Fowler 转引） |
| M2 | lint 报错文案模板化："违反规则 + 原因 + Fix: …" 三段式（把"正向 prompt 注入"写进模板） | Fowler（2.1 §3）、Qoder（2.8 §5 "一条好的报错本身就是一次教学"） |
| M3 | 播种预验证脚本：`scripts/verify_action.py`（create file / import 两类动作的合法性查询），在生成项目 AGENTS.md 写入触发条件（新位置建文件、跨包 import 前必跑） | Qoder（2.8 §4，"10 次 vs 2 次"、"层级违反是翻车头号原因"） |
| M4 | `make verify` 语义升级为四段（build → lint → test → verify），PBH-SPEC §2.2 增补"第四段可选但应预留" | Qoder（2.8 §6） |
| M5 | 播种 `scripts/verify/` 骨架 + `make add-verify`：引导用户把核心用户路径编码为可执行验证脚本 | Qoder verify skill（2.8 §6）、Anthropic 端到端验证（2.3 §5） |
| M6 | 播种 `.harness/{tasks,trace,memory}` 三目录 + 记忆三分文件格式（`memory/{episodic,procedural,failures}.md`）与读写约定条款 | Qoder（2.8 §10/§11）、LangChain 记忆文件标准（2.5 §4） |
| M7 | 播种 `harness/permissions.md`（命令白/黑/需确认清单）+ secret 扫描钩子 | LangChain 沙箱 allow-list（2.5 §3）；报告维度 6 |

### 6.3 远期（约 1 个季度）：协议升级与生态闭环接口

| # | 动作 | 一手依据 |
| --- | --- | --- |
| L1 | PBH-SPEC v2.1：新增分层规则条款、预验证接口、四段验证管道、检查点格式、记忆/trace 目录约定、**规则可拆卸元数据条款**（来源/生效条件/退役条件/复核日期） | 本文机制 #2/#3/#5/#15/#22；"可拆卸"三重一手旁证（4.3） |
| L2 | 阶段状态机接线（只播种、不执行）：`progress.json` 增加"推进前置条件"字段（如 plan→execute 需 `make verify` 通过 + 计划文件存在），由生态工具（harness-lint）执行推进判定；检查点格式携带架构决策 | Qoder 检查点（2.8 §9）、Anthropic 增量+回滚（2.3 §4）；注意：自动推进属运行时，PBH 只定义接口 |
| L3 | 定义"轨迹编译"产物的标准形态：`make add-endpoint NAME=foo` 式 Makefile 目标模式库，作为模板的一部分播种（识别环节留给运行时/人） | Qoder 棘轮（2.8 §12） |
| L4 | 文档垃圾回收条款：`tasks/` 下定期偏差扫描清单模板（doc-gardening 惯例） | OpenAI garbage collection（经 Fowler 转引）、Fowler janitor army（2.1 §9） |
| L5 | "Harness 模板"叙事升级：引用 Fowler harness templates 一手出处重新定位 PBH（"团队会基于已有 harness 选技术栈"），并把 `validate` 合规报告做成可对外展示的评分（对标 Qoder 0-100 审计口径） | Fowler（2.1 §7）、Qoder（2.8 §13） |
| L6 | 为多模型适配预留空间：AGENTS.md 条款避免绑定单一模型的提示习惯（不同模型需不同 harness 调适），IDE 适配层保持现有的强度分层 | LangChain（2.4 §8、2.5 §7 "Opus 4.6 在不同 harness 下得分差异巨大"）、Self-Harness 模型特异性（2.7 §5） |

### 6.4 明确不做的事（边界自检）

以下属于运行时职责，PBH 只种接口不实现：子代理调度与模型路由（#16 执行侧）、退出拦截中间件（#7 执行侧）、上下文压缩（#24）、Critic→Refiner 自动分析（#19 执行侧）。这与 `docs/design.md` §3.3 "一旦定义 rules.yaml 之类，PBH 就从环境播种者变成行为控制者"的判断一致——上述建议全部是**文件、脚本、目录与条款**，不是行为控制。

---

## 7. 参考资料

### 一手来源（本次调研）

1. Martin Fowler / Birgitta Böckeler《Harness engineering for coding agent users》（2026-04-02，全文直接抓取）— <https://martinfowler.com/articles/harness-engineering.html>
2. OpenAI《Harness engineering: leveraging Codex in an agent-first world》（2026-02-11，原文 403，经镜像与转引）— <https://openai.com/index/harness-engineering/>
3. Anthropic《Effective harnesses for long-running agents》（全文直接抓取）— <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
4. LangChain《Improving Deep Agents with harness engineering》（全文直接抓取）— <https://langchain-blog.ghost.io/improving-deep-agents-with-harness-engineering/>
5. LangChain《The Anatomy of an Agent Harness》（2026-03-10，全文直接抓取）— <https://langchain.com/blog/the-anatomy-of-an-agent-harness>
6. Stripe《Minions: Stripe's one-shot, end-to-end coding agents》（2026-02-09，全文直接抓取）— <https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents>
7. 上海 AI Lab《Self-Harness》（arXiv 2606.09498，原文网络不可达；经量子位官方投稿转载与知乎精读交叉）— <https://arxiv.org/abs/2606.09498>
8. 阿里云《Qoder 工程实践：Harness Engineering 指南》（2026-04-03，经 53AI 全文镜像，三镜像交叉）— <https://developer.aliyun.com/article/1724843>
9. 腾讯云《Agent 系列（三）：Harness Engineering》（页面不可抓取，未获得正文）— <https://cloud.tencent.com/developer/article/2647887>

### 佐证与补充来源

- Boris Cherny 工作流分享（2026-01）及其多源转述（paddo.dev、53ai、shellypalmer 等）— 验证 2-3x 论断
- 量子位/新浪/搜狐/网易对 Self-Harness 的官方投稿转载（2026-07-19）
- 知乎专栏 Self-Harness 逐表精读 — <https://zhuanlan.zhihu.com/p/2050864423942862617/>
- Terminal-Bench 2.0/2.1 榜单 — <https://www.datalearner.com/benchmarks/terminalbench-2>
- Codex Harness 开源（2026-08-19《Codex as a platform》）相关报道（CSDN/搜狐）
- Boris Cherny《We Cut 80% of Claude Code's Prompt》访谈转述（2026-08，AGIHunt/观猹）
- Context Engineering / SDD / Harness 关系 — <https://xie.infoq.cn/article/b9a230ed66abdf9ddffe6be78>
- AGENTS.md 长度研究综述 — <https://atlan.com/know/how-to-write-agents-md/>
- OpenAI harness 文章中文精读 — <https://aigccamp.com/industry/openai/harness-engineering>
- ForgeCode/harness 刷榜分析 — <https://www.uncoveralpha.com/p/the-harness-the-moat-for-ai-model>

### 仓库内文件

- 对标报告：`PBH-harness-engineering-对标报告.md`
- 协议：`docs/spec/PBH-SPEC.zh-CN.md`
- 设计哲学与边界：`docs/design.md`
- 本仓库操作手册：`AGENTS.md`
- 实现：`src/harness_init/core.py`、`src/harness_init/validators/make_verify.py` 等
