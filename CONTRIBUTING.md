# 贡献指南（CONTRIBUTING.md）

欢迎贡献。请先阅读本项目的 [AGENTS.md](AGENTS.md) 了解协作规则。

## 快速开始

本项目由 PBH 自身初始化，因此在开始贡献之前，请先确认你已理解本项目的 AGENTS.md。

```bash
make verify    # 确保环境就绪
pytest tests/  # 确保现有测试通过
```
## 贡献流程
Fork 本仓库，创建功能分支

修改代码前，先在 tasks/ 下声明任务计划

遵循 AGENTS.md 中的行为准则：先说明计划，再执行

确保 make verify 通过（lint + test + coverage ≥ 85%）

提交 PR，PR 描述中引用 AGENTS.md 相关条款（若有）

## 什么类型的贡献受欢迎
新增 --ide 适配（新的 AI 工具引导文件）

新增 --template 骨架（新的项目类型）

模板中的占位符遗漏修复

文档中的事实性错误修正

Harness-Lint 新规则提案（需附带"这是 AI 的什么缺陷"的解释）

## 什么类型的贡献暂不接受
向 PBH 核心添加 Agent 运行时逻辑

向模板中添加特定 Agent 的角色定义

机器可读规则文件的定义（如 rules.yaml）

任何让 PBH 从"播种"走向"执行"的改动

（详见 DESIGN.md 了解这些边界背后的设计决策）

## 行为准则
本项目由 AGENTS.md 定义协作规则。参与贡献即意味着你同意在协作中遵守这套规则。

如果你发现 AGENTS.md 本身有改进空间，欢迎提出 PR——这正是 PBH 生态"归因锚定"理念的实践。