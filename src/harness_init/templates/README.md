# {project_name}

{project_description}

## 特性

- 完整的 Python 项目结构，生成后即可开发
- 内置 `make verify` 流水线（lint + 测试，覆盖率 ≥ 85%）
- 对 Agent 友好：附带 `AGENTS.md`、`docs/context.md` 和 `opencode.yaml`
- 支持外部 Agent（如 OpenCode）以 Planner / Generator / Evaluator 模式协作

## 快速开始

```bash
pip install -e ".[dev]"
make verify
```

## 安装

```bash
# 从源码安装
pip install -e ".[dev]"
```

## CLI 使用

安装后，使用 `{project_name}` 命令行工具：

```bash
# 运行执行计划
{project_name} run [plan_path]

# 评估结果
{project_name} evaluate [result_path]

# 查看项目状态
{project_name} status
```

## 开发命令

| 命令 | 说明 |
|------|------|
| `make verify` | 运行 lint + 测试，覆盖率必须 ≥ 85% |
| `make test` | 运行 pytest |
| `make lint` | 运行 ruff 检查 |
| `make install` | 以可编辑模式安装当前包 |

## 目录结构

```
{project_name}/
├── src/{package_name}/          # 主代码
│   ├── cli.py                   # CLI 入口
│   └── ...
├── tests/                       # 测试（结构与 src/ 对应）
├── .harness/                    # 运行时产物
│   ├── plans/                   # JSON 执行计划
│   ├── eval_feedback/           # 评估反馈
│   └── progress.json            # 会话状态唯一真相源
├── configs/                     # 配置文件
├── docs/
│   ├── context.md               # 架构与约定详情
│   └── decisions/               # 架构决策记录（ADR）
├── AGENTS.md                    # Agent 快速参考
├── opencode.yaml                # Agent 工作流配置
├── Makefile
├── pyproject.toml
└── README.en.md                 # English README
```

## 架构说明

本项目遵循分层设计：

- **CLI 层** (`cli.py`)：解析参数，委托给核心逻辑
- **核心层** (`src/{package_name}/`)：业务实现
- **测试层** (`tests/`)：单元测试与集成测试

详细架构约定和常见任务，请参考 `docs/context.md`。

## 许可证

MIT
