---
label: wayfinder:map
status: MIGRATED
created: 2026-09-01
migrated_to: https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/1
---

# MAP：PBH P1 机械执法层实施规划（本地副本）

> ⚠️ **正本已迁移至 GitHub Issues：[#1 MAP: PBH P1 机械执法层实施规划](https://github.com/renjianguojinqianfan/Project-Bootstrap-Harness/issues/1)**（票据 #2–#9 为其子 issue）。本文件仅作历史快照，一切操作以 GitHub 为准。
>
> 以下为迁移前的本地 markdown tracker 约定（已废弃）：

> 本仓库未配置 issue tracker（GitHub MCP 不可达），采用本地 markdown tracker 约定：
> - 票据 = `docs/plans/wayfinder/tickets/W##-*.md`，front-matter 含 `type` / `status` / `blocked_by` / `assignee`
> - 前沿（frontier）= `status: open` 且 `blocked_by` 全为 closed 且 `assignee` 为空的票据
> - 认领 = 在 front-matter 填入 `assignee`；解决 = 在票据末尾追加 `## Resolution`，置 `status: closed`，并回写本文件的 Decisions-so-far

## Destination

产出一份**决策完备的 P1 实施 spec**（机械执法层 + 可观测性最小闭环），保存到 `docs/plans/`，可直接交给 `/implement` 或 `/to-tickets` 执行。地图完成标准：spec 中不再有"待定"的设计取舍。

## Notes

- 领域：harness-init（协议播种器）的 P1 阶段改进。输入材料：根目录《PBH-harness-engineering-对标报告》、`docs/plans/2026-09-01-harness-engineering-research.md`（一手调研）、`docs/spec/PBH-SPEC.zh-CN.md`、`docs/design.md`
- **硬边界（PBH 三问）**：只播种不执行——种规则/脚本/目录骨架进生成项目，绝不引入 Agent 运行时逻辑
- **可拆卸原则**：spec 中每条新规则必须带生效条件与退役条件（一手调研证实这是行业共识）
- **P0 正确性缺陷修复是既定前提**（对标报告第 5 节），不进本地图，但终点 spec 须将其列为第 0 阶段
- 每个会话开工前先读本文件与 `2026-09-01-harness-engineering-research.md`

## Decisions so far

<!-- 已解决票据的索引，一行一条：标题 + 一句话结论 + 链接 -->

（地图刚建立，尚无已解决票据。以下决策在画图前的访谈中确定，不属于票据结论：）

- 地图范围 = 仅 P1（机械约束层 + 可观测性最小闭环）；P2 全部进雾区
- 分层依赖规则形态 = 声明式配置（`.harness/layers.yaml` + 说明 + 校验占位），执行工具待调研
- 状态机推进 = 播种契约 + 脚本（progress.json 推进契约 + `harness stage` 脚本 + git 检查点钩子），推进由用户的 Agent 运行时执行
- 可观测性 = 对齐 OpenTelemetry（格式需先调研）
- 安全护栏播种 = 纳入（`.harness/permissions.md` + secret 扫描钩子）
- 目录命名 = 保持 `.harness`（调研证实 `.agent/` 无任何工具自动读取）
- Tracker = 本地 markdown（GitHub MCP fetch failed，恢复后可迁移）

## Not yet specified

<!-- 雾区：方向已知但问题尚不锐化，等前沿推进后毕业为票据 -->

- **SPEC v2.1 协议条款**：P1 新能力（分层声明、预验证接口、状态机推进接口、trace 格式）写入协议的措辞与版本策略——需 P1 设计全部落定后才锐化
- **生态闭环接口**：`.harness/trace/` 格式定案后，为 `harness-lint` / `harness-agent` 预留的数据接口长什么样
- **记忆三分目录**（`.harness/memory/{episodic,procedural,failures}.md`）：报告 P2 项，与 trace 格式强耦合，等 W02 结论
- **合规性报告输出**（类 Lighthouse 评分）：依赖 `validate --json` schema（W05）定案
- **lint 报错注入修复指令**：候选并入 W07（verify 骨架）或 W03（分层校验），待两者设计时自然浮现归属

## Out of scope

- **PBH 播种 Agent Skills**：访谈中用户明确否决——技能内容是用户自己的经验沉淀，不是协议地基；且报告 P2-15 已证明"随模板分发技能"是反模式（`opencode.yaml` 硬编码第三方 skills 被列为硬伤）。若未来重议，须重画终点
