# harness-init

[![PyPI version](https://badge.fury.io/py/harness-init.svg)](https://badge.fury.io/py/harness-init)
[![Python Version](https://img.shields.io/pypi/pyversions/harness-init.svg)](https://pypi.org/project/harness-init/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

一个 CLI 工具，用于快速初始化符合 **Harness Engineering** 规范的完整 Python 项目。生成的项目不是空壳，而是包含可运行的 Harness 核心引擎、Agent 骨架、测试套件和验证流水线，**生成后即可 `make verify` 通过**。

## 核心特性

- **一键生成完整项目**：包结构、CLI、测试、Harness 运行时、Git 初始化，全部自动完成
- **生成即验证**：每个生成的项目都内置 `make verify`（ruff + pytest，覆盖率 ≥ 85%）
- **对 Agent 友好**：生成的项目自带 `AGENTS.md`、`docs/context.md`、`opencode.yaml`，外部智能体（如 OpenCode）可以直接理解项目结构和工作流
- **安全健壮**：项目名校验、路径遍历防护、Git 失败自动回滚、State 原子写入
- **双语文档**：生成的项目包含中英文 README，便于国际化协作
- **模块化设计**：生成的 `harness` 核心引擎包含 `runner`、`evaluator`、`state`、`workflow` 等组件，开箱即用

## 安装

```bash
pip install harness-init
```

或者从源码安装：

```bash
git clone https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness.git
cd Project-Bootstrap-Harness
pip install -e ".[dev]"
```

## 快速开始

```bash
# 创建新项目
harness-init my-project

# 进入并验证
cd my-project
pip install -e ".[dev]"
make verify
```

执行后会在当前目录创建 `my-project/`，包含：

- 完整的 Python 包结构（`src/my_project/`）
- Harness 核心引擎：`runner.py`（任务执行）、`evaluator.py`（结果评估）、`state.py`（状态持久化）、`workflow.py`（工作流定义）
- Agent stubs：`planner.py`、`generator.py`、`evaluator.py`
- 运行时目录：`.harness/plans/`、`.harness/eval_feedback/`、`.harness/state/`、`.harness/progress.json`
- 多命令 CLI：`run`、`evaluate`、`status`
- `configs/`（dev/test/prod）、`docs/context.md`、`docs/decisions/`、`AGENTS.md`、`opencode.yaml`
- `pyproject.toml`、`Makefile`、`.gitignore`、`README.md`、`README.en.md`
- 自动初始化的 Git 仓库和初始提交

## 生成的项目结构

```
my-project/
├── .harness/                 # Harness 运行时目录
│   ├── plans/                # 执行计划
│   ├── eval_feedback/        # 评估反馈
│   ├── state/                # 状态持久化
│   ├── templates/            # 模板文件
│   ├── logs/                 # 运行日志
│   └── progress.json         # 任务进度
├── configs/                  # 多环境配置 (dev/test/prod)
├── docs/                     # 文档
│   ├── context.md            # Agent 上下文
│   └── decisions/            # 架构决策记录
├── src/my_project/           # 主包
│   ├── __init__.py
│   ├── cli.py                # CLI 入口
│   ├── harness/              # 核心引擎
│   │   ├── runner.py
│   │   ├── evaluator.py
│   │   ├── state.py
│   │   └── workflow.py
│   ├── agents/               # Agent 骨架
│   │   ├── planner.py
│   │   ├── generator.py
│   │   └── evaluator.py
│   ├── tools/                # 工具函数
│   └── utils/                # 通用辅助
├── tests/                    # 测试
├── .gitignore
├── AGENTS.md                 # Agent 操作指南
├── opencode.yaml             # 工作流配置
├── Makefile
├── pyproject.toml
├── README.md                 # 中文说明
└── README.en.md              # 英文说明
```

## CLI 选项

```bash
harness-init [OPTIONS] PROJECT_NAME
```

| 选项 | 简写 | 说明 |
|------|------|------|
| `--force` | `-f` | 强制覆盖已存在的目录（旧目录自动备份） |
| `--no-git` | | 跳过 Git 初始化 |
| `--yes` | `-y` | 跳过所有交互提示，使用默认值 |
| `--version` | `-v` | 显示版本号 |

### 项目名规则

为了生成合法的 Python 包，项目名必须：
- 以字母或下划线开头
- 只包含字母、数字、连字符（`-`）和下划线（`_`）
- 不能为空，不能包含空格、路径分隔符或 `..`

**合法示例**：`my-project`、`my_project`、`harness_v2`  
**非法示例**：`123project`（数字开头）、`my project`（含空格）、`foo/../bar`（路径遍历）

## 开发命令（针对 harness-init 本身）

| 命令 | 说明 |
|------|------|
| `make verify` | 运行 ruff + pytest（覆盖率 ≥ 85%） |
| `make test` | 运行 pytest |
| `make lint` | 运行 ruff |
| `make install` | `pip install -e .` |

## 为什么生成的项目对 Agent 友好

生成的项目专为外部智能体设计：

- **`AGENTS.md`**：快速地图，agent 第一眼就能理解项目角色、工作流和关键约束
- **`docs/context.md`**：深层上下文，包含架构细节、命名规范、常见任务示例
- **`opencode.yaml`**：显式声明七阶段工作流配置
- **`make verify`**：统一验证入口，agent 修改后立即获得质量反馈
- **`.harness/` 运行时目录**：plan、eval_feedback、state 分离，支持多轮对话断点续传

## 架构

- `src/harness_init/cli.py` — CLI 入口（参数解析）
- `src/harness_init/core.py` — 项目生成核心逻辑（校验、复制、渲染、Git 初始化、回滚）
- `src/harness_init/_utils.py` — 名称验证、模板渲染等辅助函数
- `src/harness_init/_git.py` — Git 初始化与回滚辅助函数
- `src/harness_init/templates/` — 目标项目的模板文件

## 许可证

MIT License

---

[English Version](README.en.md)
