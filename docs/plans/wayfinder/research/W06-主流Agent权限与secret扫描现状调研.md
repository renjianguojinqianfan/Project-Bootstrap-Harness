# W06 调研笔记：主流 Agent 权限与 secret 扫描现状调研

- 背景：Wayfinder 地图 #1 票据 #7（W06 安全护栏播种设计）访谈中的质疑——"权限系统和安全扫描大部分
  Agent（opencode、trae、qoder、codex、workbuddy 等）都已自带，这些不应该是 Agent 自己做的事吗？"
  本笔记用一手证据裁决：PBH 播种 `.harness/permissions.md`（项目级风险事实声明）与内置/行业
  secret 扫描防线各自的位置。
- 日期：2026-09-01；方法：一手来源优先（官方文档原文/官方仓库源码），每条论断标注出处；
  查不到的明确写"未查到"，不以推断冒充事实。

## TL;DR 结论

1. **命令权限系统**：七家工具全部有运行时权限机制（弹窗确认 / LLM 分类器审批 / 沙箱），其中
   **四家支持项目内声明式权限文件**——Claude Code `.claude/settings.json`、Qoder
   `<project>/.qoder/settings.json`、Cursor CLI `<project>/.cursor/cli.json`、OpenCode 项目级
   `opencode.json`；Codex 与 Trae 仅用户级配置（`~/.codex/config.toml`、
   `~/.trae-cn/permission/work/global.json`）；WorkBuddy 无文件配置，全在客户端安全中心。
   **格式互不相通，各家只读自己的文件。**
2. **AGENTS.md**：七家全部读取（Claude Code 需 `@AGENTS.md` 导入，其余原生识别），但所有官方文档
   一致强调：**文档/规则只影响模型行为，不构成权限边界**。
3. **项目级风险声明**：**没有任何一家**提供"项目特有危险区/禁区声明"的专门文件槽位；行业公认的
   落点是 AGENTS.md/CLAUDE.md/rules 里的章节——agents.md 标准明确推荐 "Security considerations"
   章节。
4. **secret 扫描**（二轮修订，详见 §5）：原结论"七家均无内置"已修正——Qoder 内置三层代码安全扫描且官方原文明确覆盖"把真实密钥写入配置"；Claude Code 有内置 `/security-review` 命令与官方 security-guidance / Claude Security 插件；Codex 有官方 Codex Security 产品（独立安装）；Cursor Bugbot 的 PR 审查把 security issues 列为检测目标；Trae / OpenCode / WorkBuddy 仍未查到。行业机械防线（detect-secrets / gitleaks / GitHub push protection）独立于此，仍分布在 pre-commit → push → 仓库历史/CI → 平台 partner 吊销。
5. **裁决输入**：4a——播种纯文档是**补空缺不冲突**（无等价机制，且文档不参与任何权限引擎执行，
   不存在被忽略或冲突的路径）；4b（二轮修订）——Agent 内置安全扫描已是头部厂商趋势，但各家官方均自定位"纵深防御的一层、不替代既有机械扫描"，机械门禁仍需作为环境标准播种。

---

## 1. 命令权限系统：逐工具事实

### 1.1 Claude Code（参照）

- **机制形态**：运行时权限规则 + `auto` 模式用 LLM 分类器审批。规则评估顺序 **deny → ask → allow**。
  （来源：https://code.claude.com/docs/en/permissions ，访问 2026-09-01）
- **项目内声明式配置：有**。配置文件层级：`<project>/.claude/settings.json`（项目级，官方明确
  "可检入版本控制与团队共享"）、`<project>/.claude/settings.local.json`（个人、不入版本控制）、
  `~/.claude/settings.json`（用户级）、enterprise managed settings。规则语法如
  `"Bash(npm run *)"` 通配符，分 allow/ask/deny 三类。（同上，逐字核对）
- **AGENTS.md：不原生读取**。memory 文档明确 Claude Code 读 `CLAUDE.md`，不读 AGENTS.md；
  官方建议 `@AGENTS.md` 导入。（来源：https://code.claude.com/docs/en/memory ，访问 2026-09-01）
- **关键引文（执行面与指令层的区分）**：
  > "Permission rules are enforced by Claude Code, not by the model. Instructions in your prompt
  > or CLAUDE.md shape what Claude tries to do, but they don't change what Claude Code allows."

  permissions 文档另建议："Add CLAUDE.md guidance… This shapes what Claude tries but doesn't
  enforce a boundary."——即官方自己把"风险声明文档"定位在行为引导层。

### 1.2 OpenCode

- **机制形态**：运行时权限规则（默认多数工具 `ask`）；`--auto` 自动模式**仍执行显式 deny**。
  （来源：https://opencode.ai/docs/permissions/ ，访问 2026-09-01）
- **项目内声明式配置：有**。项目根 `opencode.json`（可提交 Git）的 `permission` 字段，三态
  `allow/ask/deny` + 对象语法，**last matching rule wins**：
  ```json
  { "permission": { "*": "ask", "bash": { "*": "ask", "git *": "allow", "rm *": "deny" } } }
  ```
  默认 `.env` 读取为 deny。（同上，逐字核对）
- **AGENTS.md：原生读取**。rules 文档：AGENTS.md 是规则文件（项目级/全局级），兼容 CLAUDE.md
  作为回退，`instructions` 字段可追加任意 md。（来源：https://opencode.ai/docs/rules/ ，
  访问 2026-09-01）

### 1.3 Codex CLI（OpenAI）

- **访问受限说明**：官方网页文档已迁移至 developers.openai.com，该站对当前网络返回 403
  （WebFetch 与浏览器均被拒）；官方仓库内 `docs/` 于 2026-05-03 提交 67849d950d
  （"Remove local docs and specs (#20896)"）移除。**以下以官方仓库 main 分支源码取证。**
- **机制形态**：审批策略 + 沙箱模式。`codex-rs/core/config.schema.json` 定义：
  - `approval_policy`：`AskForApproval` 枚举（on-request / granular / never / untrusted 语义）
  - `sandbox_mode`：`"read-only" | "workspace-write" | "danger-full-access"`
  （来源：https://raw.githubusercontent.com/openai/codex/main/codex-rs/core/config.schema.json ，
  访问 2026-09-01，逐字核对）
- **项目内声明式配置：未查到**。配置位于用户级 `~/.codex/config.toml`；schema 中无项目内
  permissions 文件槽位。
- **AGENTS.md：原生读取，且是一等公民**。schema 中 `project_doc_fallback_filenames` 描述为
  "Ordered list of fallback filenames to look for when AGENTS.md is missing"，
  `project_doc_max_bytes` 默认 32768——证明 Codex 以 AGENTS.md 为项目指令文档主入口。

### 1.4 Qoder

- **机制形态**：运行时权限规则 + `autoMode`（LLM 分类器审批）。规则语法与 Claude Code 同构
  （如 `Bash(npm run test:*)`）。IDE 端：内置风险类别 + 用户黑名单命中即弹确认；Experts 模式
  在沙箱（Seatbelt/bubblewrap/自研引擎）内自动执行，`~/.ssh` 对沙箱不可见。
  （来源：https://docs.qoder.com/zh/cli/permissions 与
  https://docs.qoder.com/zh/user-guide/quest/terminal-and-sandbox ，访问 2026-09-01）
- **项目内声明式配置：有**。8 层配置来源中明确包含 `<project>/.qoder/settings.json`
  （项目级、官方定位"团队共享"）与 `.qoder/settings.local.json`（个人）。
- **AGENTS.md：读取，但官方明确不构成授权**。关键引文：
  > 用户级 "AGENTS.md 同样注入分类器上下文……其内容用于说明意图，不构成授权"。

  且 `autoMode` **只读用户全局设置、"工作区下的文件一律忽略"**（官方说明是为了防提示注入）。
- **结论**：Qoder 把"文档影响审批器上下文"与"工作区文件不参与授权"都写进了官方文档。

### 1.5 Cursor（参照）

- **机制形态**：Agent 终端命令默认需用户批准；Run Modes 官方自称 "best-effort guardrails rather
  than a hard security boundary"。（来源：https://cursor.com/docs/agent/security ，访问 2026-09-01）
- **项目内声明式配置：有（CLI）**。`<project>/.cursor/cli.json`（项目级）或
  `~/.cursor/cli-config.json`（全局），token 语法 `Shell(git)` / `Read(.env*)` /
  `Write(**/*.key)` / `WebFetch(domain)` / `Mcp(server:tool)`，**deny 优先**。
  （来源：https://cursor.com/docs/cli/reference/permissions ，访问 2026-09-01）
- **AGENTS.md：原生读取**。rules 文档：`.cursor/rules/*.mdc` 项目规则 + 根/子目录 AGENTS.md。
  关键引文：
  > "Some teams use enforced rules as part of internal compliance workflows. While this is
  > supported, AI guidance should not be your only security control."
  （来源：https://cursor.com/docs/context/rules ，访问 2026-09-01）

### 1.6 Trae

- **机制形态**：三预设——手动审批 / 自动审批（LLM Guardian）/ 完全访问；高风险命令（如
  `rm -rf`）拦截弹窗；命令白名单在客户端"对话流"设置；沙箱（macOS sandbox-exec）
  白名单在客户端设置。（来源：https://docs.trae.cn/work_permission-and-approval 与
  /work_sandbox ，浏览器渲染抓取，访问 2026-09-01）
- **项目内声明式配置：未查到**。自定义权限配置位于用户级
  `~/.trae-cn/permission/work/global.json`（customProfiles：shellSandbox / approval.reviewer /
  sceneRules / commandRules / mcpRules + filesystem + network allow/deny），非项目内文件。
- **AGENTS.md：读取，但需开关**。规则页：`.trae/rules/*.md`（frontmatter：alwaysApply /
  description / globs / paths / scene:git_message）；AGENTS.md 需在设置中心开启
  "将 AGENTS.md 包含在上下文中"开关；兼容 CLAUDE.md。
  （来源：https://docs.trae.cn/ide_rules ，访问 2026-09-01）

### 1.7 WorkBuddy

- **机制形态**：两种模式——默认权限 / 完全访问（Full Access），任务输入框下拉切换；默认权限下
  写敏感路径、删除、执行脚本命令、网络访问会停下确认；沙箱约束 + 删除保护（回收站）+ 自动备份。
  （来源：
  https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes ，
  访问 2026-09-01）
- **安全中心三类名单**（腾讯云官方账号文章，2026-08-03）：文件"强制审批黑名单"（可加
  `.ssh`/`.env` 目录）、命令"询问名单"（可加 `git push`、`npm publish`）、网络"拒绝域名"
  ——**全部客户端侧配置，未查到任何项目内文件读取机制**。
- **AGENTS.md：未查到**官方文档记载（官方文档站无相关页面）。

### 1.8 归纳事实表

| 工具 | 运行时机制 | 项目内声明式权限文件 | AGENTS.md |
| --- | --- | --- | --- |
| Claude Code | 规则 + auto 模式分类器；deny→ask→allow | **有**：`.claude/settings.json` | 需 `@AGENTS.md` 导入（原生读 CLAUDE.md） |
| OpenCode | 规则；`--auto` 仍执行 deny | **有**：项目根 `opencode.json` | 原生（兼容 CLAUDE.md） |
| Codex CLI | approval_policy + sandbox_mode | **未查到**（仅用户级 `~/.codex/config.toml`） | 原生，一等公民（有字节上限与回退文件名） |
| Qoder | 规则 + autoMode 分类器；IDE 沙箱 | **有**：`.qoder/settings.json` | 原生，但"不构成授权"；autoMode 忽略工作区文件 |
| Cursor | 终端命令默认批准；CLI 权限规则 | **有**（CLI）：`.cursor/cli.json` | 原生（根+子目录） |
| Trae | 手动/自动审批（LLM Guardian）/完全访问 | **未查到**（仅用户级 `~/.trae-cn/permission/work/global.json`） | 需设置开关 |
| WorkBuddy | 默认权限/完全访问 + 沙箱 + 客户端三类名单 | **未查到**（全客户端侧） | 未查到 |

**共性**：四家有项目内权限文件，但格式互不相通、各自只认自己的文件；无一家的权限文件能覆盖
其他家。所有官方文档一致区分"执行面"（权限引擎/沙箱强制）与"指令面"（文档/规则软约束）。

## 2. "项目级风险声明"的既有落点

- **没有一家工具提供"项目特有危险区/禁区声明"的专门文件槽位**。逐家核对（§1）：四家的项目内
  文件都是**可执行的权限规则**（allow/deny 命令列表），不是自然语言风险事实声明；Codex/Trae/
  WorkBuddy 连项目内文件都不读。
- **行业公认落点是 AGENTS.md/rules 里的章节**。agents.md 标准站（Linux Foundation Agentic AI
  Foundation 治理，GitHub 60k+ 仓库采用）的推荐章节列表明确包含：
  > "Security considerations — security gotchas… anything you'd tell a new teammate belongs here."
  （来源：https://agents.md ，访问 2026-09-01）
- Claude Code 官方同样建议在 CLAUDE.md 里写行为引导（§1.1 引文），并明确其不是边界。
- **结论**：项目级风险事实声明目前是"公认该写、但没有标准文件"的状态——写在 AGENTS.md 的
  Security considerations 章节里是事实惯例。

## 3. secret 扫描：Agent 内置情况与行业防线

### 3.1 七家 Agent 是否内置（二轮修订）

> **[二轮修订，2026-09-01]** 一轮结论"七家官方文档均无内置密钥扫描记载"已修正：Qoder 官方文档
> 明确记载内置三层代码安全扫描（L1 静态检查 / L2 语义 / L3 数据流）且覆盖 secret 检测；
> Claude Code / Codex / Cursor 亦有官方安全扫描产品或插件（形态各异，多数需安装）；
> Trae / OpenCode / WorkBuddy 维持"未查到"。逐家证据与来源见新增 §5。
> 一轮原文（保留备查）：逐家核对官方文档（§1 各来源），均未记载内置密钥扫描（提交前或执行时检测硬编码 secret）；"未查到"不等于不存在未公开功能。

修订后的事实表：

| 工具 | 内置安全扫描（官方文档层） | 专门的 secret 检测记载 |
| --- | --- | --- |
| Qoder | **有**，内置三层（L1 每次写入后自动 / L2 任务收尾 / L3 推送前） | **明确**：L1 原文"把真实密钥写入配置……L1 是常开的底线"，L2 原文"悄悄写进配置的 API Key" |
| Claude Code | **有**，内置 `/security-review` 命令 + 官方 security-guidance / Claude Security 插件 + Code Review（PR）+ 托管产品 | 部分：security-guidance 自定义模式的官方示例即 secret 前缀（`sk_live_`、`AKIA`） |
| Codex（OpenAI） | **有**，官方 Codex Security（独立 CLI/SDK + Codex 插件，需安装登录） | 未查到专门记载（主打漏洞扫描/验证/补丁） |
| Cursor | 部分：Bugbot 云端 PR 审查，官方表述检测 "bugs, security issues, and code quality problems" | 未查到专门记载 |
| Trae | **未查到**（"智能体审查"为通用代码审查，无 secret 专项） | 未查到 |
| OpenCode | **未查到**（官方文档站无安全扫描相关页面） | 未查到 |
| WorkBuddy | **未查到**（仅"Skill 安装前安全扫描"，扫的是第三方 Skill 而非用户代码） | 未查到 |

### 3.2 行业防线分层（各自定位）

| 防线 | 定位环节 | 一手来源原文 |
| --- | --- | --- |
| detect-secrets（Yelp） | **pre-commit**，防新 secret 入库 | 官方三目标："preventing new secrets entering the codebase / detecting known secrets that bypassed the pre-commit hook / a checklist to roll out"；baseline 机制（来源：README https://github.com/Yelp/detect-secrets ，访问 2026-09-01） |
| gitleaks | git 仓库/文件/stdin 全量与增量扫描，官方提供 **gitleaks-action**（CI） | "detecting secrets like passwords, API keys, and tokens in git repos, files, and…stdin"；README 宣布 feature complete、转向 Betterleaks（来源：https://github.com/gitleaks/gitleaks ，访问 2026-09-01） |
| GitHub push protection | **push 时**阻断 | "secret scanning blocks contributors from pushing secrets to a repository and generates an alert whenever a contributor bypasses the block"（来源：https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/enable-push-protection ，访问 2026-09-01） |
| GitHub secret scanning | **仓库历史/全分支**持续扫描 + partner 集成自动吊销 + validity checks | "Secret scanning scans your entire Git history on all branches…hardcoded credentials"；公共仓库免费（来源：https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning ，访问 2026-09-01） |

**关键特征**：四道防线全部是**确定性机械检查**（正则/规则匹配 + 平台校验），不依赖模型判断，
且分布在 Agent 触及不到的环节（commit hook、push 通道、平台侧历史扫描）。

## 4. 裁决输入

### 4a. 播种 `.harness/permissions.md` 是补空缺还是重复/冲突？

**事实层面：补空缺，且无冲突路径。**

1. **无等价机制**：没有任何一家提供"项目级风险事实声明"的专门落点（§2）。四家的项目内权限
   文件是机器规则（命令 allow/deny），语义与自然语言风险事实声明不同层。
2. **不会被"忽略"到有害、也不会"冲突"**：纯文档不参与任何权限引擎执行——各家的权限文件
   格式互不相通且只认自己的路径，`.harness/permissions.md` 不会撞上任何家的解析器。它的作用
   路径只有一条：被 Agent 作为上下文读到（如 AGENTS.md 里引用它）。
3. **与官方立场一致**：Claude Code、Qoder、Cursor 的官方文档都明确"文档/规则只塑造行为、
   不构成权限边界"（§1.1/§1.4/§1.5 引文）——播种它时必须如实标注这一性质（行为引导，非强制
   边界），否则反而违背各家官方表述。
4. **真正的空缺**是"让风险声明更难被忽略 + 跨工具一致"：各家只读自己的规则文件，一份放在
   固定路径、被 AGENTS.md 引用的风险声明是跨工具的公共信息源——这正是 PBH"协议播种器"
   （让协议更难被忽略）的落点。

### 4b. secret 扫描是"Agent 已覆盖"还是独立机械门禁？（二轮修订）

**事实层面：Agent 内置安全扫描已成头部厂商趋势，但机械门禁仍独立、不可替代。**

1. **内置扫描已是趋势**（逐家证据见 §5）：Qoder 内置三层（明确覆盖 secret，L1 免费）、
   Claude Code 内置命令 + 官方插件族、Codex Security 官方产品、Cursor Bugbot PR 审查——
   时间集中在 2025-10 至 2026-07。Trae / OpenCode / WorkBuddy 仍未查到。
2. **但没有任何一家官方声称可替代机械防线**，均自定位"纵深防御的一层"：
   - Claude Code 官方 defense-in-depth 表格把 CI 层保留为 "Your existing static analysis and
     dependency scanners"，并明言 "The plugin doesn't replace your existing source-code
     security tools"；security-guidance 另声明 "None of the layers block writes or commits"。
   - Qoder L1 是模式匹配、L2/L3 是模型驱动并按 Credits 计费——属概率性、非全时门禁。
3. 行业防线（§3.2）定位不变：pre-commit 钩子、push 通道、平台历史扫描是**与行为主体无关的确定性检查**，即使 Agent 完全遵守纪律也照样执行；gitleaks 宣布自身 "feature complete" 亦说明机械扫描工具仍独立演化。
4. 对 PBH 的含义（维持并补强原结论）：secret 防线仍该播种为**环境标准**（.pre-commit-config.yaml 里的 detect-secrets/gitleaks 条目、或 Makefile 检查目标）。Agent 内置扫描是"更早发现、概率性、厂商割裂"的一层，与跨工具环境标准互补而非替代——且 PBH 无法假设用户恰好使用带内置扫描的厂商。

## 5. 补充调研：内置安全扫描复核（2026-09-01 二轮）

- 背景：新事实——Qoder 官方文档明确记载内置三层代码安全扫描且覆盖 secret 检测，一轮 §3.1 结论需修正。
- 方法：与一轮相同（一手来源优先，标注 URL 与访问日期；查不到写"未查到"）。本轮全部来源访问日期：2026-09-01。

### 5.1 Qoder：内置三层代码安全扫描（触发本轮修订的新事实）

- **机制形态**：三层渐进式扫描 + `/security-scan` 斜杠命令 + 整仓全量扫描（单次上限 1 万行）。
  （来源：https://docs.qoder.cn/ide/security ，访问 2026-09-01，逐字核对）
  | 层级 | 强度 | 触发时机 |
  | --- | --- | --- |
  | L1 静态检查 | 高危模式匹配 | 会话中每次代码写入后自动执行，无需确认 |
  | L2 轻量扫描 | 语义理解，仅看增量 | 推荐任务收尾时（会话流推荐卡片或 `/security-scan`） |
  | L3 深度扫描 | 跨文件数据流分析 | 推荐提交/推送前；识别到推送意图时弹卡确认；Quest 提交菜单有"扫描并推送"入口 |
- **secret 检测：官方原文明确覆盖**。关键引文：
  > L1："模型可能悄悄用上 eval()、把真实密钥写入配置——L1 是常开的底线，用来避免这些'一眼可疑'的写法真正落到文件里。"
  > L2 适用场景："刚拼好的 SQL 字符串、刚传给 shell 的请求参数、悄悄写进配置的 API Key。"
- **收费**：L1 免费；L2 约 5 Credits/500 行，L3 约 20 Credits/500 行，Credits 耗尽后扫描被阻塞。（同上）
- **定性**：七家中唯一"内置、默认、明确覆盖 secret"的形态；但 L1 是模式匹配、L2/L3 是模型驱动且计费，属概率性防线而非机械门禁。

### 5.2 Codex（OpenAI）：官方 Codex Security 产品（独立安装，非运行时默认）

- **一手来源（官方仓库）**：openai/codex-security——"Codex Security CLI and TypeScript SDK for
  finding, validating, and fixing security vulnerabilities"；`npm install @openai/codex-security` →
  `codex-security login` → `codex-security scan`；CI 用 `OPENAI_API_KEY`；支持 SARIF/CSV/JSON 导出、
  `--fail-on-severity`、Docker 批量扫描、第三方推理供应商（Bedrock/OpenRouter/Fireworks）。
  （来源：https://github.com/openai/codex-security ，访问 2026-09-01，逐字核对）
- **时间线**（多家报道互证；官方公告页 openai.com 对当前网络返回 403，官方文档站
  learn.chatgpt.com/docs/security 超时无法访问，均已标注）：2025-10 Aardvark（GPT-5 驱动的
  agentic security researcher，小范围内测）→ 2026-03-06 更名 Codex Security，并入 Codex 网页版
  研究预览（ChatGPT Pro/Business/Enterprise/Edu）→ 2026-06-22 起 Codex App/CLI 内可调用 →
  2026-07-28/29 CLI 与 SDK 开源（Apache-2.0）。
- **secret 检测：未查到专门记载**。官方仓库 README 与可达文档均以漏洞扫描/验证/补丁为主线，
  无专门"硬编码 secret 检测"条目。
- **定性**：有官方安全扫描能力，但**不是 Codex CLI/IDE 运行时的默认内置**，需单独安装登录；
  云端研究预览限 ChatGPT Pro/Business/Enterprise/Edu，本地 CLI/SDK 为有限 beta。

### 5.3 WorkBuddy：未查到（仅 Skill 供应链扫描）

- **官方文档站逐页核查**：workbuddy.cn/docs 全部 81 个文档页（浏览器渲染抓取）无任何"用户代码安全扫描/密钥检测"功能页。
  （来源：https://www.workbuddy.cn/docs/workbuddy ，访问 2026-09-01）
- **仅有的两处"扫描"记载，对象都是第三方 Skill 而非用户代码**：
  1. Changelog 4.7.5（2026-03-30）："安装 Skill 前自动进行安全扫描，检测潜在的恶意脚本和风险行为，保障你的数据安全。"
     （来源：https://www.workbuddy.cn/docs/workbuddy/Changelog ，访问 2026-09-01）
  2. Skill Scanner 技能（SkillHub）：安装第三方 Skill 前审查"可疑依赖、硬编码配置和潜在风险"。
     （来源：.../WorkBuddy-Zero-Cost-Skill-Top-10/Skill-Scanner ，访问 2026-09-01）
- 安全中心（审计日志、沙箱、黑白名单、目录写保护、自动备份）均为运行时防护，非代码扫描。
- **相关但独立的事实**：腾讯云 2026-06-05 发布企业级代码安全产品 CodeBuddy Security，为独立产品而非 WorkBuddy 内置功能；同场宣布 WorkBuddy 默认开启的安全防护为"身份校验、输入检测、运行时沙箱、工具调用拦截、输出审核、传输加密"（无代码 secret 扫描表述）。
- **结论：未查到内置代码安全扫描/密钥检测。**

### 5.4 Trae：未查到（维持一轮结论）

- **站点地图全量核查**：docs.trae.cn sitemap 255 页（浏览器渲染抓取），无安全扫描/密钥检测专页；
  候选页面逐一核对：
  - 「智能体审查」（ide_agent-powered-code-review）：AI 识别代码潜在问题 + 变更总结，支持未提交变更/单次提交/分支间差异，可提交后自动触发——**通用代码审查，无 secret 检测专项记载**。
  - 「自动运行 & 安全性」（ide_auto-run-and-security）：仅讲自动运行 MCP/命令的沙箱外风险。
  - 企业版「安全、合规与治理」：数据"用后即抛"、RBAC、审计日志——数据治理向。
  （来源：https://docs.trae.cn/ide_agent-powered-code-review 、/ide_auto-run-and-security 、
  /enterprise_security-compliance-and-governance ，浏览器渲染抓取，访问 2026-09-01）
- **结论：未查到内置安全扫描/密钥检测。**（网络上的"Trae 内置密钥扫描"说法均出自第三方软文/教程，非官方文档记载，不采信。）

### 5.5 复核：Claude Code（一轮遗漏，本轮最大修正）

- **官方文档索引**（来源：https://code.claude.com/docs/llms.txt ，访问 2026-09-01）设有专门的 "Code review & CI/CD" 章节，一轮调研遗漏。
- **四层官方安全扫描体系**：
  1. **`/security-review` 内置命令**：对当前分支做一次性安全检查（内置，无需安装）。
  2. **security-guidance 插件**（官方插件市场 `claude-plugins-official`，所有套餐可用）：三层检查——
     每次文件编辑后的确定性模式匹配（无模型调用、免费）+ 每轮结束后的后台模型 diff 审查 +
     每次 `git commit`/`git push` 的 agentic 深度审查。关键事实：
     - **secret 检测有官方落点**：项目内 `.claude/security-patterns.yaml` 可加自定义模式，官方示例即 `substrings: ["sk_live_", "AKIA"]`（硬编码 API key 前缀）。
     - **非阻断**："None of the layers block writes or commits."；官方定位 "one layer of defense in depth, not a complete security solution"。
     - 可通过 `.claude/settings.json` 的 `enabledPlugins` 检入仓库全团队开启，或企业 managed settings 统一分发。
     （来源：https://code.claude.com/docs/en/security-guidance ，访问 2026-09-01，逐字核对）
  3. **Claude Security 插件**：多 Agent 深度扫描（架构映射→威胁建模→漏洞捕猎→独立 verifier 复核），输出 SARIF 2.1.0/CWE 分类报告与补丁（补丁永不自动应用）；另有 Enterprise 托管版产品。
     （来源：https://code.claude.com/docs/en/claude-security ，访问 2026-09-01）
  4. **Code Review**：PR 时多 Agent 审查，"catch logic errors, security vulnerabilities, and regressions"（Team/Enterprise 套餐）。
- **官方立场引文（裁决关键）**：
  > "The plugin doesn't replace your existing source-code security tools."；defense-in-depth 表的
  > CI 层写的是 "Your existing static analysis and dependency scanners — language-specific rules,
  > supply-chain checks, and policy enforcement the plugin does not attempt"。

### 5.6 复核：Cursor / OpenCode

- **Cursor：Bugbot 是官方文档层的安全审查能力（一轮遗漏）**。官方表述：
  > "Bugbot reviews pull requests and identifies bugs, security issues, and code quality problems."

  形态：云端、对 PR diff 运行（每次 PR 更新自动或 `cursor review` 手动），集成 GitHub/Bitbucket/Azure DevOps，可作 CI check、按审查计费。**非 IDE 运行时扫描，亦无 secret 检测专项记载**。
  （来源：https://cursor.com/docs/bugbot ，访问 2026-09-01，逐字核对）
  另：Agent Security 页复核维持一轮事实（权限护栏向，"best-effort guardrails rather than a hard security boundary"，无 secret 扫描记载）。
- **OpenCode：未查到**。官方站点 sitemap 无任何 security/scan/vulnerability 相关文档页（维持一轮结论）。
  （来源：https://opencode.ai/sitemap.xml ，访问 2026-09-01）

### 5.7 行业事实归纳（基于修正后全景）

修正后的全景表：

| 厂商 | 内置安全扫描 | 形态 | secret 覆盖 | 收费 |
| --- | --- | --- | --- | --- |
| Qoder | 有 | 内置三层，默认集成 | 明确 | L1 免费，L2/L3 耗 Credits |
| Claude Code | 有 | 内置命令 + 官方插件 + PR 审查 + 托管产品 | 部分（官方扩展示例） | security-guidance 全套餐；Code Review/托管版 Team+ |
| Codex | 有（官方产品） | 独立 CLI/SDK + 插件，需安装 | 未查到专门记载 | 研究预览/有限 beta |
| Cursor | 部分 | Bugbot 云端 PR 审查 | 未查到专门记载 | 按审查计费 |
| Trae / OpenCode / WorkBuddy | 未查到 | —（WorkBuddy 仅 Skill 安装扫描） | 未查到 | — |

**两个事实性结论**：
1. **"把安全扫描内置进运行时"是已成趋势，而非个别现象**：四家头部厂商（Qoder/Anthropic/OpenAI/Cursor）在 2025-10 至 2026-07 集中推出官方安全扫描能力，但形态分三档——默认内置（仅 Qoder）、官方插件/命令需安装（Claude Code、Codex）、云端 PR 审查（Cursor）；Trae/OpenCode/WorkBuddy 尚无官方记载。没有任何一家的内置扫描以 secret 检测为主打（仅 Qoder 明确覆盖）。
2. **行业机械防线未被认为可被替代，仍独立存在**：所有带内置扫描的厂商均官方自定位"纵深防御的一层"——Claude Code 明言插件不替代既有扫描器、CI 层保留给"你既有的静态分析与依赖扫描器"，且其各层均不阻断写入/提交；Qoder 的扫描为概率性且计费。detect-secrets / gitleaks / GitHub push protection 等确定性机械门禁的生态位（确定性、免费/低成本、与行为主体无关、跨工具）未被任何官方文档声称取代。
- **对 PBH 播种设计的含义**：内置扫描是"更早发现"的概率层，环境标准（pre-commit/CI 机械扫描）是"绝不漏放"的门禁层——两者互补，PBH 播种 `.pre-commit-config.yaml` 机械扫描条目与 AGENTS.md 安全章节的路径不变；另可新增一个可选增强项：对带内置扫描的厂商（Qoder `/security-scan`、Claude Code security-guidance 插件）在文档中声明其存在与开关位置。
- **本轮局限**：openai.com 官方公告页 403、learn.chatgpt.com 官方文档站超时，Codex 时间线部分依赖多家互证的二手报道（已标注）；developers.openai.com 仍 403（同一轮）。

## 6. 来源清单

一手来源（均为 2026-09-01 访问）：

- Claude Code：https://code.claude.com/docs/en/permissions 、https://code.claude.com/docs/en/memory
- OpenCode：https://opencode.ai/docs/permissions/ 、https://opencode.ai/docs/rules/
- Codex CLI：https://raw.githubusercontent.com/openai/codex/main/codex-rs/core/config.schema.json
  （官方仓库 main 分支；网页文档 developers.openai.com 返回 403，无法访问，已标注）；
  文档迁移提交 67849d950d 经 api.github.com commits API 定位
- Qoder：https://docs.qoder.com/zh/cli/permissions 、
  https://docs.qoder.com/zh/user-guide/quest/terminal-and-sandbox
- Cursor：https://cursor.com/docs/context/rules 、https://cursor.com/docs/agent/security 、
  https://cursor.com/docs/cli/reference/permissions
- Trae：https://docs.trae.cn/ide_rules 、https://docs.trae.cn/work_permission-and-approval 、
  https://docs.trae.cn/work_sandbox （JS 渲染站点，经浏览器渲染抓取）
- WorkBuddy：
  https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes ；
  腾讯云官方账号文章（安全中心三类名单，2026-08-03 发布）
- AGENTS.md 标准：https://agents.md
- Secret 扫描：https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning 、
  https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/enable-push-protection 、
  https://github.com/gitleaks/gitleaks 、https://github.com/Yelp/detect-secrets

二轮新增一手来源（均为 2026-09-01 访问）：

- Qoder：https://docs.qoder.cn/ide/security （内置三层扫描 + secret 检测原文 + Credits 计费）
- Codex Security：https://github.com/openai/codex-security （官方仓库 README）；
  openai.com/index/codex-security-now-in-research-preview 返回 403、learn.chatgpt.com/docs/security 超时，无法直接核对，已标注；时间线由多家互证报道支撑（unite.ai、腾讯新闻、品玩等，2026-03 至 2026-08）
- Claude Code：https://code.claude.com/docs/llms.txt 、
  https://code.claude.com/docs/en/security-guidance 、
  https://code.claude.com/docs/en/claude-security
- Cursor：https://cursor.com/docs/bugbot
- Trae：https://docs.trae.cn/ide_agent-powered-code-review 、
  https://docs.trae.cn/ide_auto-run-and-security 、
  https://docs.trae.cn/enterprise_security-compliance-and-governance 、
  https://docs.trae.cn/sitemap.xml （255 页全量核查；JS 渲染站点，经浏览器渲染抓取）
- WorkBuddy：https://www.workbuddy.cn/docs/workbuddy/Changelog 、
  https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/WorkBuddy-Zero-Cost-Skill-Top-10/Skill-Scanner 、
  https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes （81 页全量核查）；
  CodeBuddy Security 发布：腾讯云 2026-06-05 大会报道（网易号转载，独立产品非 WorkBuddy 内置）
- OpenCode：https://opencode.ai/sitemap.xml （无安全扫描相关页面）

仓库内部上下文：`docs/plans/wayfinder/research/` 既有笔记（W01/W02/W05）、
`docs/design.md`（PBH 三问）。
