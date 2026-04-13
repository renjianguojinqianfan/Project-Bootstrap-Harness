# AGENTS.md - harness-init

## 项目目标
构建 `harness-init` CLI 工具，用于快速初始化符合 Harness Engineering 规范的**完整可运行 Python CLI 项目**（非空壳，生成后即可 `make verify` 通过）。

## 技术栈
- Python 3.11+
- CLI 框架：`typer`
- 测试：`pytest` + `pytest-cov`（覆盖率 ≥ 85%）
- 代码检查：`ruff`

## 常用命令
| 命令 | 说明 |
|------|------|
| `make verify` | 运行 lint + test（项目验收标准） |
| `make test` | 运行 pytest，要求覆盖率 ≥ 85% |
| `make lint` | ruff 检查 `src/` |
| `make install` | `pip install -e .` |

## 目录结构约定
```
src/harness_init/
├── cli.py          # CLI 入口
├── core.py         # 核心逻辑
└── templates/      # 项目模板资源（生成目标项目的文件模板）
tests/              # 单元测试，与 src 结构对应
```

## 架构铁律
1. `cli.py` 只负责参数解析和调用 `core.py`
2. `core.py` 处理所有文件生成和 Git 初始化逻辑
3. `templates/` 存放目标项目的模板文件（AGENTS.md、Makefile、.gitignore 等）
4. 所有核心逻辑必须有单元测试
5. 每个函数 ≤ 30 行，每个文件 ≤ 200 行

## 开发流程
- 使用 **Sisyphus** 主编排任务
- 每完成一个子任务，必须运行 `make verify` 验证
- 测试覆盖率不达标时禁止提交

## 关键实现细节
- 生成的项目 CLI 使用 `typer.run(hello)` 单命令模式，避免 `typer.Typer()` 在单命令时被压平的问题
- `core.py` 使用 `textwrap.dedent` 管理多行模板字符串，避免 E501 超长行
- `_init_git()` 会自动配置本地 `user.name` 和 `user.email`，不依赖全局 Git 配置
- 模板目录 `src/harness_init/templates/` 已被根 `pyproject.toml` 的 ruff 配置排除

## 环境要求
- 首次开发前必须执行：`pip install -e .`（或 `make install`）
- 系统中必须安装 `git`，`core.py` 会调用 `git init` 和 `git commit`
- Windows 下若缺少 `make`，可通过 `winget install --id GnuWin32.Make` 安装
- Windows 下 `make` 不可用时，可运行等价命令：
  - `ruff check src/`
  - `pytest tests/ -v --cov=src --cov-fail-under=85`

## 远程仓库
- GitHub: https://github.com/renjianguojinqianfan/Harness-Engineering
