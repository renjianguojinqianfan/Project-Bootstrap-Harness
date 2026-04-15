# harness-init

快速初始化符合 Harness Engineering 规范的**完整 Harness Engineering 项目**。生成后即可 `cd` 进入并运行 `make verify`。

## 安装

```bash
git clone https://github.com/renjianguojinqianfan/Harness-Engineering.git
cd Harness-Engineering
pip install -e ".[dev]"
```

## 使用

### 基础用法

```bash
harness-init my-project
```

执行后会在当前目录创建 `my-project/`，包含：
- 完整的 Python 包结构（`src/my_project/`）
- Harness 核心引擎（`runner.py`、`evaluator.py`、`state.py`、`workflow.py`）
- 智能体 stubs（`planner.py`、`generator.py`、`evaluator.py`）
- 运行时目录（`.harness/plans/`、`.harness/eval_feedback/`、`.harness/state/`、`.harness/logs/`）
- 多命令 CLI（`run`、`evaluate`、`status`）
- `configs/`（dev/test/prod）、`docs/context.md`、`AGENTS.md`
- `pyproject.toml`、`Makefile`、`.gitignore`、`opencode.yaml`
- 自动初始化的 Git 仓库和初始提交

进入生成的项目即可运行验证：

```bash
cd my-project
pip install -e ".[dev]"
make verify
```

### CLI 选项

```bash
# 查看版本
harness-init --version

# 强制覆盖已存在目录（旧目录会被备份为 my-project.bak-YYYYMMDDhhmmss）
harness-init my-project --force

# 跳过 Git 初始化
harness-init my-project --no-git
```

### 项目名规则

为了生成合法的 Python 包，项目名必须：
- 以字母或下划线开头
- 只包含字母、数字、连字符（`-`）和下划线（`_`）
- 不能为空，不能包含空格、路径分隔符或 `..`

**合法示例**：`my-project`、`my_project`、`harness_v2`

**非法示例**：`123project`（数字开头）、`my project`（含空格）、`foo/../bar`（路径遍历）

## 开发命令

| 命令 | 说明 |
|------|------|
| `make verify` | 运行 ruff + pytest（覆盖率 ≥ 85%） |
| `make test` | 运行 pytest |
| `make lint` | 运行 ruff |
| `make install` | `pip install -e ".[dev]"` |

## 要求

- Python 3.11+
- Git

## 架构

- `src/harness_init/cli.py` — CLI 入口（参数解析）
- `src/harness_init/core.py` — 项目生成核心逻辑（校验、复制、渲染、Git 初始化、回滚）
- `src/harness_init/templates/` — 目标项目的模板文件

## 最近修复的重点

- **安全**：项目名校验、路径遍历防护、shell 注入防护
- **健壮**：模板渲染支持二进制文件、Git 失败自动回滚（Windows 兼容）
- **CLI**：新增 `--version`、`--force`、`--no-git`
- **生成项目**：Runner 真正执行命令（优先 `exec`，失败 fallback 到 `shell`）、StateManager 原子写入
