# 🚀 harness-init

[![PyPI version](https://badge.fury.io/py/harness-init.svg)](https://badge.fury.io/py/harness-init)
[![Python Version](https://img.shields.io/pypi/pyversions/harness-init.svg)](https://pypi.org/project/harness-init/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **为 AI Agent 准备的 Python 项目脚手架。**
> 不是又一个代码生成器，而是一份任何 AI 工具都能读懂的 **"协作合同"**。

---

## 🤔 为什么需要这个工具？

用 Claude Code、Codex、Cursor 写代码时，你是否遇到过这些场景：

- AI 写了代码却不跑测试，小问题滚雪球？
- 新建一个会话后，AI 完全忘记之前的决策，需要你反复"喂"上下文？
- 团队里每个人对 AI 的指挥方式不一样，代码风格混乱？

**问题不在于 AI 不够聪明，而在于我们没给它一个清晰、持久、可验证的"工作环境"。**

`harness-init` 在创建项目的第一秒，就把 **AI 的工作说明书、质量门禁和状态管理系统** 种进项目里。从此，任何进入项目的 AI 工具都知道：该按什么流程干活、如何交接任务、以及怎样才算"做完了"。

---

## ✨ 核心特性

- **🤖 Agent 原生设计**：生成的 `AGENTS.md` 定义了 Planner → Generator → Evaluator 三角色强制工作流，让 AI 学会"分工协作"。
- **✅ 生成即验证**：内置 `make verify` 流水线，强制运行 ruff 代码检查 + pytest 测试，覆盖率门槛 **≥85%**。质量不过关，项目不算生成成功。
- **🛡️ 约束即代码**：自动提供 Git Hooks 脚本和 GitHub Actions CI 配置（可选），让规范成为不可绕过的硬约束。
- **📋 标准化的交接协议**：计划模板、进度状态文件、交接摘要，让 AI 即使在新会话中也能"无缝接棒"。
- **🌍 双语文档**：自动生成中英文 `README.md`，降低国际化团队的协作门槛。
- **🎯 专注 Python，刻意轻量**：不实现复杂的 Agent 运行时，只做最擅长的事——定义一套通用的协作规范。

---

## 📊 效果验证

我们用 Trae Solo Coder 做了一次严格的对照实验，任务是为 CLI 项目添加一个新子命令。

| 指标 | 普通项目 | PBH 项目 |
| :--- | :--- | :--- |
| 人类需要澄清的次数 | 2 次 | **1 次** |
| AI 执行的任务步骤数 | 10 步 | **6 步** |
| 调试修复次数 | 4 次 | **1 次** |
| 是否主动运行质量门禁 | 否 | **是 (`make verify`)** |
| 总耗时 | 15-20 分钟 | **5-8 分钟** |

👉 **[查看完整实验报告 →](docs/experiments/trae-solo-comparison.md)**

---

## 📦 安装

```bash
pip install harness-init
```

需要 Python 3.11 或更高版本。

---

## 🚀 快速开始

### 1. 创建新项目

```bash
harness-init my-awesome-project
```

按提示输入项目描述、作者信息（或使用 `--yes` 跳过）。

### 2. 快速体验模式

如果你只想快速体验核心功能，可以使用 `--quick` 模式：

```bash
harness-init my-project --quick --yes
```

**精简模式包含：**
- 核心项目结构（`src/`、`tests/`）
- `AGENTS.md`（简化版，保留三角色工作流）
- `Makefile`、`pyproject.toml`、`README.md`
- `.harness/` 工作区（计划模板 + 状态追踪）

**精简模式不包含：**
- CI/CD 配置（`.github/workflows/`）
- IDE 适配文件（`CLAUDE.md`、`.cursorrules`）
- 文档体系（`docs/decisions/`、`PROJECT_MAP`）
- Git Hooks（`.pre-commit-config.yaml`）
- Agent 子系统（`harness/`、`agents/`、`tools/`、`utils/`）

适合场景：快速原型验证、5分钟上手体验、个人工具项目。

### 3. 进入项目并安装依赖

```bash
cd my-awesome-project
pip install -e ".[dev]"
```

### 4. 运行验证流水线

```bash
make verify
```

如果一切正常，你会看到 `✔ 验证通过`。

> 💡 使用 `--quick` 模式生成的精简项目结构更简单，详见上方"快速体验模式"。

### 5. 邀请 AI 入场

用 Claude Code、Cursor 或 Codex 打开项目，对 AI 说：

> "请阅读 `AGENTS.md`，以 Planner 角色帮我规划一个功能：添加一个 CLI 命令来显示系统信息。"

AI 会自动读取工作流定义，按 **计划 → 生成 → 评估** 的节奏完成任务。

---

## 📁 生成的项目结构

```
my-awesome-project/
├── .harness/                 # Agent 工作区
│   ├── plans/                # 计划文件存放处
│   ├── state/                # 状态持久化
│   ├── templates/            # 计划模板等
│   ├── logs/                 # 运行日志
│   └── progress.json         # 任务进度追踪
├── configs/                  # 多环境配置
├── docs/                     # 文档（含 context.md 上下文）
├── src/my_awesome_project/   # 主包
│   ├── cli.py                # CLI 入口
│   ├── harness/              # 核心引擎（runner/evaluator/state/workflow）
│   ├── agents/               # Agent 骨架（planner/generator/evaluator）
│   ├── tools/                # 工具函数
│   └── utils/                # 通用辅助
├── tests/                    # 测试套件
├── .gitignore
├── AGENTS.md                 # AI 工作流强制说明书
├── opencode.yaml             # Codex 配置（含自定义命令）
├── Makefile                  # 验证与自动化任务
├── pyproject.toml            # 项目元数据与依赖
├── README.md                 # 中文说明
└── README.en.md              # 英文说明
```

---

## 🛠️ 命令选项

| 选项 | 简写 | 说明 |
| :--- | :--- | :--- |
| `--force` | `-f` | 强制覆盖已存在的目录（旧目录自动备份） |
| `--no-git` | | 跳过 Git 初始化 |
| `--yes` | `-y` | 跳过所有交互提示，使用默认值 |
| `--quick` | `-q` | 生成精简项目（无 CI/文档/钩子/IDE 配置） |
| `--ci <platform>` | | 生成 CI 配置文件（目前支持 `github`） |
| `--version` | `-v` | 显示版本号 |

---

## 🗺️ 路线图

### ✅ 已完成 (v1.0.0)
- [x] 计划模板从 Markdown 迁移到 JSON Schema（Breaking Change）
- [x] 增强 `AGENTS.md`：审批工作流 + 安全规范（≤100 行）
- [x] Git Hook 集成：`.pre-commit-config.yaml` + `scripts/pre-push.sh|ps1`
- [x] GitHub Actions CI 配置：`.github/workflows/ci.yml`
- [x] IDE 适配文件：`CLAUDE.md`、`.cursorrules`
- [x] 项目文档：`docs/PROJECT_MAP.md`、`docs/decisions/ADR_TEMPLATE.md`
- [x] 跨平台 `.sh` 执行权限自动修复

### 📅 计划中
- [ ] 探索多技术栈支持（Node.js / Go）
- [ ] harnessctl CLI 增强

> ⏰ 本项目由个人业余维护，路线图不承诺具体发布时间，按功能优先级和社区反馈动态调整。

---

## 📅 维护节奏

- 🐛 **Bug 修复**：通常在一周内响应。
- ✨ **新功能**：每 **2-4 周** 发布一个小版本，按路线图推进。
- 💬 **Issue 回复**：尽量在 48 小时内回复。

感谢你的耐心和理解！欢迎通过 Issues 和 Discussions 参与讨论。

---

## 🤝 贡献

欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解开发规范和提交流程。

---

## 📄 许可证

MIT License © [renjianguojinqianfan](https://github.com/renjianguojinqianfan)

---

## 🙏 致谢

- [Typer](https://typer.tiangolo.com/) - 优雅的 CLI 框架
- [Ruff](https://docs.astral.sh/ruff/) - 极速 Python Linter
- [Pytest](https://docs.pytest.org/) - 可靠的测试框架
- 灵感来源：Anthropic 的 GAN 式三智能体架构、OpenAI 的"代码仓库作为记录系统"实践、Martin Fowler 的 Harness Engineering 论述。

---

**[English Version](README.en.md)**
