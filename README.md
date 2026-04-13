# harness-init

快速初始化符合 Harness Engineering 规范的 Python CLI 项目。

## 安装

```bash
git clone https://github.com/renjianguojinqianfan/Harness-Engineering.git
cd Harness-Engineering
pip install -e ".[dev]"
```

## 使用

```bash
harness-init my-project
```

执行后会在当前目录创建 `my-project/`，包含：
- 完整的 Python 包结构（`src/my_project/`）
- 初始 CLI 代码和单元测试（`pytest` + `typer`）
- `pyproject.toml`、`Makefile`、`.gitignore`、`AGENTS.md`
- 自动初始化的 Git 仓库和初始提交

进入生成的项目即可运行验证：

```bash
cd my-project
pip install -e ".[dev]"
make verify
```

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

- `src/harness_init/cli.py` — CLI 入口
- `src/harness_init/core.py` — 项目生成逻辑
- `src/harness_init/templates/` — 目标项目的模板文件
