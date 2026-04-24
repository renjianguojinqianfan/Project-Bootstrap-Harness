# Project-Bootstrap-Harness (PBH)

> 一个为 AI 辅助编程设计的**项目协议模板**。
>
> 我们不教 AI 怎么思考，我们为它提供最佳的执行环境。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/pypi-harness--init-green.svg)](https://pypi.org/project/harness-init/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 为什么需要这个？

用 Claude Code、Cursor 或 OpenCode 写代码时，你大概率遇到过这些摩擦：

- **每次新会话都要重新交代规则**："记得跑测试"、"别改无关文件"、"先写计划再编码"
- **AI 写了代码却不验证**：小错误滚雪球，最后人类来兜底
- **切换 AI 工具时上下文断裂**：Claude Code 理解的规则，Cursor 不知道

**问题不在于 AI 不够聪明，而在于项目本身缺少一份"默认协作协议"。**

PBH 在 `harness-init my-project` 的瞬间，把协议、质量门禁和状态记录种进项目。从此，任何打开这个项目的 AI 工具都能在 30 秒内知道：这里怎么跑测试、质量底线在哪里、当前项目处于什么阶段。

---

## 它是什么（以及不是什么）

### ✅ PBH 是

- **一份通用协作协议**：`AGENTS.md` 作为所有 AI 工具的共同入口，定义致命规则、工作准则和项目结构
- **一套质量门禁基础设施**：`make verify` 开箱即用，lint + 测试 + 覆盖率一气呵成
- **一个可观测的 Agent 行为基准**：同一份 `AGENTS.md`，你可以观察不同 AI 工具的遵循程度和表现差异
- **一个 Spec Coding 容器**：提供 `tasks/` 目录供你拆解任务，内容完全由你掌控

### ❌ PBH 不是

- **不是 Agent 框架**：不定义 AI 角色，不实现多智能体调度
- **不是代码生成器**：不根据自然语言描述生成业务代码
- **不是 Spec Coding 流程工具**：不生成 PRD、SPEC、constraints.md，只提供存放它们的目录

---

## 快速开始

```bash
pip install harness-init

# 完整模式
harness-init my-awesome-project

# 快速模式（最小可用，5 分钟上手）
harness-init my-project --quick --yes
```

进入项目并验证：

```bash
cd my-awesome-project
pip install -e ".[dev]"
make verify        # 应输出 ✅ 验证通过
```

### 💡 如果 make 命令不可用

Windows 用户可能未安装 make。若提示 'make' 不是内部或外部命令，你可以：

**安装 make：**

- Windows：安装 [GnuWin32 Make](https://gnuwin32.sourceforge.net/packages/make.htm) 或运行 `winget install GnuWin32.Make`
- macOS：`xcode-select --install`
- Linux：`sudo apt install make` 或等价命令

**或直接运行等价命令：**

```bash
# 代码风格检查
ruff check src/ tests/

# 运行测试 + 覆盖率
pytest tests/ -v --cov=src --cov-fail-under=85
```

邀请 AI 入场：

> "请阅读 AGENTS.md，了解这个项目的规则，然后帮我开始工作。"

---

## 生成的项目结构

```text
my-awesome-project/
├── .harness/
│   ├── progress.json         # 项目阶段状态（AI 新会话的第一站）
│   └── workspaces/           # 多智能体工作区隔离（预留）
├── docs/
│   ├── context.md            # 深层上下文（架构、约定、任务）
│   └── decisions/            # 架构决策记录（ADR）
├── src/my_awesome_project/
│   └── cli.py                # CLI 入口（可按需替换）
├── tests/                    # 测试套件（镜像 src/ 结构）
├── tasks/                    # 任务拆解（Spec Coding 容器）
├── AGENTS.md                 # AI 协作协议（所有工具的共同入口）
├── Makefile                  # verify / test / lint / fix
├── pyproject.toml            # 依赖 + 工具配置
└── README.md
```

---

## AGENTS.md：所有 AI 工具的共同入口

PBH 生成的核心文件是 `AGENTS.md`，它采用"机场导航"式结构，让 AI 在 30 秒内理解项目：

- **快速上手**：第一步做什么、怎么跑验证
- **多智能体声明**：支持多 AI 并行工作，建议使用独立 git worktree
- **工作准则**：柔性引导——修改前先说明计划、聚焦原子任务、完成后验证
- **致命规则**：不可违反的质量底线
- **安全指南**：禁止硬编码密钥、命令审查等
- **文件映射**：一目了然的目标速查

PBH 不定义 AI 角色，不强制特定工作流。它提供的是一个所有 AI 工具都能理解的通用协议。

---

## 两种模式对比

| 特性 | 完整模式 | 快速模式 (--quick) |
|------|----------|-------------------|
| AGENTS.md | 完整版（≤80 行） | 精简版（≤50 行） |
| CI/CD | ✅ GitHub Actions | ❌ |
| 文档体系 | ✅ context.md / ADR | ❌ |
| 依赖 | typer + pytest + ruff 等 | 仅 typer |

两种模式都包含：`AGENTS.md`、`Makefile`（verify/test/lint）、`tests/` 目录、`tasks/` 目录、`progress.json`。

---

## 适用场景

**适合：**

- 个人开发者使用多种 AI 工具，需要统一的项目级协作规则
- 小团队希望统一 AI 协作标准
- 需要可验证、可交接的 AI 辅助开发流程
- 想观察和比较不同 AI 工具在同一项目中的表现

**不适合：**

- 需要多智能体自主调度系统 → 使用专门的 Agent 框架
- 需要确定性自动化的无人值守流水线 → PBH 不锁死 Agent 行为
- 非 Python 项目 → 当前模板仅支持 Python 3.11+

---

## 路线图

- **v1.1.0**：砍掉越界功能，重写 AGENTS.md 为"机场导航"式，确立清晰边界
- **v1.5.0**：支持 `--ide` 参数（按需生成 IDE 适配文件）、`--template` 参数（lib/web/notebook 等多项目类型）
- **v2.0.0**：多智能体原生支持、生态接口、正式宣告通用协议定位

本项目由个人业余维护，路线图按优先级动态调整。

---

## 致谢

- [Typer](https://typer.tiangolo.com/) — 优雅的 CLI 框架
- [Ruff](https://docs.astral.sh/ruff/) — 极速 Python Linter
- [Pytest](https://docs.pytest.org/) — 可靠的测试框架

灵感来源：Anthropic 的 Agentic Workflow 与 Context Engineering 实践、OpenAI 的 Harness Engineering 理念

## License

MIT © renjianguojinqianfan