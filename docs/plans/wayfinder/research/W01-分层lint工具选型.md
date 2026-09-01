# W01 调研：分层依赖 lint 执行工具选型

- 票据：`tickets/W01-分层lint工具选型调研.md`
- 日期：2026-09-01
- 方法：逐候选查官方文档 / PyPI 元数据 / 仓库源码树，每条论断标注一手来源。

## 问题

PBH 播种 `.harness/layers.yaml`（声明层与依赖方向），需要一个**执行器**来校验该声明。
核心约束（来自票据）：声明式驱动（不绑定工具自有配置格式）、纯静态、安装成本低、
报错可附加自定义修复提示（"正向 prompt 注入"）、可拆卸、兼容 ruff / `make verify`。

## 结论（先行）

**推荐：grimp + 约 50 行胶水脚本 `scripts/lint_deps.py`**，读取 `.harness/layers.yaml`，
调用 grimp 的一等 API `graph.find_illegal_dependencies_for_layers()` 执行，
报错文案由胶水层完全自控（可注入"违反规则 + 原因 + Fix:"三段式）。
import-linter 作为备选（想要成熟 CLI / pre-commit 生态、不想维护胶水时）。
ruff 与 deptry 均不能表达分层约束，不参与选型。

---

## 候选逐个调研

### 1. import-linter（seddonym/import-linter，最新 2.14，2026-08-28 发布）

| 事实 | 来源 |
| --- | --- |
| 定位"Lint your Python architecture"，契约类型含 `layers`（分层架构专用）、`forbidden`、`independence`、`acyclic_siblings`、`protected`，且支持自定义契约 | 官方文档首页：https://import-linter.readthedocs.io/en/latest/ |
| `layers` 契约语义与本项目一致：高层可依赖低层反之不行，**含间接链**（low 不能经由中间模块间接 import high）；支持 `containers`、可选层 `(medium)`、`exhaustive`、同层兄弟模块（`\|` 独立 / `:` 非独立） | layers 契约文档：https://import-linter.readthedocs.io/en/latest/contract%5Ftypes/layers/ |
| 配置文件固定为三选一：`setup.cfg` / `.importlinter`（INI）/ `pyproject.toml`（TOML），无 YAML 输入 | configure 文档：https://import-linter.readthedocs.io/en/latest/get%5Fstarted/configure/ |
| CLI `lint-imports --config <path>` 可指定任意路径配置——意味着可"YAML → 生成临时配置 → 调 CLI"间接驱动，但需维护二次翻译层 | run 文档：https://import-linter.readthedocs.io/en/latest/get%5Fstarted/run/ |
| 前置条件：`root_package` **must be importable**（通常需已安装或在当前目录）——不是完全脱离环境 | 同上（configure 文档 `root_package` 条目） |
| 纯静态：官方文档明确外部包"are *not* statically analyzed"，反证根包是静态分析；底层图由 grimp 构建（见 §2） | configure 文档 `include_external_packages` 条目 |
| 依赖：`click>=6`、`grimp>=3.14`、`rich>=14.2.0`、`typing-extensions`，要求 Python>=3.10 | PyPI JSON：https://pypi.org/pypi/import-linter/json |
| 报错输出为工具自有格式，**无自定义报错文案注入口**（文档中无此选项） | run / contract_types 文档通读无此项 |
| 支持 pre-commit 集成（`language: system`）与缓存（`.import_linter_cache`） | run 文档 |

**判定**：语义覆盖最成熟，但①配置格式绑定（需从 layers.yaml 翻译）；②报错文案不可注入修复提示；
③拆卸后残留 `[tool.importlinter]` 段或 `.importlinter` 文件。三点均违反票据核心约束。

### 2. grimp（python-grimp/grimp，最新 3.16，2026-08-28）

| 事实 | 来源 |
| --- | --- |
| 定位：构建"一个或多个 Python 包内部 import 的可查询图"，纯库形态，无 CLI | README：https://grimp.readthedocs.io/en/latest/readme.html |
| **一等分层 API**：`graph.find_illegal_dependencies_for_layers(layers, containers)`，返回违规的 `PackageDependency`（含 importer/imported 与 import 链 `Route`）；支持同层兄弟 `grimp.Layer(..., independent=False)`、`closed=True` 闭合层 | usage 文档"Higher level analysis"：https://grimp.readthedocs.io/en/latest/usage.html |
| 可拿到违规 import 的**行号与行内容**（`get_import_details` 返回 `line_number`/`line_contents`）——自写报错定位所需信息齐备 | 同上（direct imports 节） |
| 静态性：包定位靠 importlib（`adaptors/modulefinder.py`），import 提取由源码级解析完成——仓库含 `rust/src/import_parsing.rs`、`import_scanning.rs`（Rust 源码扫描层）；测试资产含 `syntaxerrorpackage`（带语法错误的包也能被处理，证明不执行代码） | 仓库文件树：https://api.github.com/repos/python-grimp/grimp/git/trees/main?recursive=1 |
| 前置条件：被分析的包需可被发现（README quick start 要求 `pip install somepackage`）——与 import-linter 同一约束（import-linter 内部就是调它） | README quick start |
| 模块表达式支持 `*` / `**` 通配（`mypackage.**`） | usage 文档"Module expressions" |
| 内建缓存（`.grimp_cache`，可 `cache_dir=None` 关闭） | usage 文档 `cache_dir` 参数 |
| grimp 仓库自身用 `.importlinter` 文件 dogfood 自己的分层约束（旁证该组合是作者本人认可的生产用法） | 仓库文件树（含 `.importlinter`） |

**判定**：这是"执行器"本身（import-linter 的 layers 契约正是构建在它之上，二者语义一致），
以 Python API 形态存在，**从 layers.yaml 驱动只需 ~50 行胶水**，报错格式完全自控。
代价：胶水脚本需自行维护（但逻辑极薄：读 YAML → build_graph → check → print）。

### 3. deptry（fpgmaas/deptry）

| 事实 | 来源 |
| --- | --- |
| 职责：比对"代码中 import 的模块"与"项目声明的依赖（pyproject/requirements）"，检出 DEP001 缺失 / DEP002 冗余 / DEP003 传递 / DEP004 dev 误分类等 | 官方 README：https://github.com/fpgmaas/deptry |
| 它查的是**第三方依赖声明卫生**，不涉及项目内模块间的 import 关系，无任何"层/模块边界"概念 | 同上（全文无此概念） |

**判定**：❌ 不适用。与分层校验是正交问题（可作为未来独立票据的候选，如"依赖卫生检查"）。

### 4. ruff（TID251 banned-api 等）

| 事实 | 来源 |
| --- | --- |
| `banned-api`（TID251，源自 flake8-tidy-imports）：全局禁用某些模块/成员的 import，`"<target>".msg` 可附自定义消息，报错形如 `` `pkg.a.fa` is banned: DO NOT USE `` | 规则文档：https://docs.astral.sh/ruff/rules/banned-api/ ；实际输出见 issue 16692：https://github.com/astral-sh/ruff/issues/16692 |
| 禁用的对象是**全局的**——无法表达"模块 A 禁止 import 模块 B，但模块 C 允许"这种**上下文相关**约束；"per-file banned-api"支持目前只是未实现的 feature request | issue 7974（请求方明确说"如果支持按模块设置规则就能替代我的 pylint 插件"）：https://github.com/astral-sh/ruff/issues/7974 |
| ruff 官方也无意把依赖卫生类检查纳入（deptry/pip-check-reqs 的移植请求停留在 issue） | issue 10015：https://github.com/astral-sh/ruff/issues/10015 |
| ruff 不支持自定义规则（无插件机制，写新规则需改 Rust 源码并自行编译） | 社区实践仅能通过源码修改：CSDN 案例（二手，仅作旁证） |

**判定**：❌ 不能表达分层约束（分层是"谁 import 谁"的有向上下文关系，banned-api 是全局黑名单）。
但可作为**补充**：把个别绝对禁用的模块（如禁止业务层直接 import `os.system` 类）写进
模板已有的 `[tool.ruff.lint]` 时，`banned-api` 的 `msg` 字段可携带教学性文案。

### 5. 自写 ~50 行 AST 静态扫描脚本

| 事实 | 来源 |
| --- | --- |
| 技术可行性：`ast.parse` + 遍历 `ast.Import`/`ast.ImportFrom` 提取 import 是标准做法，纯静态、零依赖 | Python 官方 ast 文档：https://docs.python.org/3/library/ast.html |
| 行业先例①：OpenAI Codex 团队的 harness 用"自定义 linters 和结构性测试强制实施的分层架构"（经 Fowler 原文转引） | 本仓库《2026-09-01 harness 工程调研》§2.1 §8 / §2.2 §4 |
| 行业先例②：Microsoft TaskWeaver 官方文档明确"对生成代码做静态分析，解析成 AST 后检查是否只 import 了允许的模块" | 官方文档：https://microsoft.github.io/TaskWeaver/docs/advanced/code_verification/ |
| 行业先例③：Java 生态的 ArchUnit `layeredArchitecture()` 是同语义在 JVM 的标准解，证明"声明分层 + 机械校验"是成熟范式 | Fowler 博客（本仓库调研 §2.1 §3 转引）；ArchUnit 官方：https://www.archunit.org/ |
| **关键语义差距**：朴素 AST 扫描只能看**直接** import；而 import-linter 官方文档强调分层违规包括**间接链**（low 经由未列入的 utils 间接 import high 也算违规）。自写脚本要覆盖间接链就必须建全图并做可达性分析——这正是 grimp 解决的问题 | layers 契约文档（"This includes indirect imports…"） |

**判定**：直接 import 检查可行且有充分行业先例，但要覆盖间接链、相对导入解析、容器/通配等语义，
自写脚本会迅速膨胀成"重造 grimp"。因此最优解不是二选一，而是**自写薄胶水 + grimp 引擎**。

---

## 对比表

| 维度 | import-linter | grimp + 胶水 | deptry | ruff TID251 | 纯自写 AST |
| --- | --- | --- | --- | --- | --- |
| 能否表达分层（含间接链） | ✅ 原生 | ✅ 原生 API | ❌ 职责不同 | ❌ 仅全局黑名单 | ⚠️ 仅直接 import |
| 声明式驱动（layers.yaml 直驱） | ⚠️ 需翻译成其 INI/TOML | ✅ YAML→API 直接映射 | ❌ | ❌ | ✅ |
| 纯静态（不执行代码） | ✅ | ✅（源码级解析） | ✅ | ✅ | ✅ |
| 安装成本 | 中（grimp+click+rich） | 低（仅 grimp；import-linter 反正也依赖它） | 低但无用 | 零（模板已有） | 零 |
| 报错可注入自定义修复提示 | ❌ 输出格式固定 | ✅ 胶水层完全自控 | — | ⚠️ 仅 `msg` 字段 | ✅ |
| 可拆卸性（移除无残留） | ⚠️ 残留 `[tool.importlinter]`/`.importlinter` | ✅ 删脚本+YAML+一个 dev 依赖即净 | — | — | ✅ |
| 与 make verify 兼容 | ✅（CLI 退出码） | ✅（脚本退出码） | — | ✅ | ✅ |
| 维护负担 | 零（成熟工具） | ~50 行薄胶水 | — | 零 | 随需求膨胀 |
| 前置约束 | 包需可 import | 包需可发现（同等） | — | 无 | 无 |

## 推荐选型与理由

**首选：grimp + `scripts/lint_deps.py` 胶水脚本。**

1. **声明式直驱**：grimp 的 `find_illegal_dependencies_for_layers(layers, containers)` 参数
   与 layers.yaml 字段一一对应，无需二次配置翻译（import-linter 必须生成中间配置）。
2. **报错教学化**：胶水层拿到 `PackageDependency` + 行号行内容后，可按项目规范输出
   "违反了什么规则 + 为什么是问题 + Fix: …"三段式——这是票据明确的硬需求，
   也是 harness 调研中"正向 prompt 注入"机制的落点（本仓库调研 §机制#4、#2）。
3. **语义完备**：间接链、容器、同层独立性、可选层等语义由 grimp 承担，
   自写扫描只覆盖直接 import，语义差距见 §5。
4. **可拆卸**：产物只有 `scripts/lint_deps.py`、`.harness/layers.yaml`、
   dev 依赖 `grimp` 三者，全部删除即回到无约束状态，零残留。
5. **安装成本最低档**：import-linter 本身就依赖 `grimp>=3.14`（PyPI 元数据），
   直接用 grimp 反而少装 click/rich。
6. **行业先例背书**：OpenAI 自写分层 linter（经 Fowler 转引）、TaskWeaver AST 白名单、
   ArchUnit 分层架构，均证明"声明 + 轻量执行器"是标准做法；grimp 仓库自身也用
   import-linter 强制自身分层，说明该生态是作者维护的活跃项目。

**备选**：若未来希望零维护脚本、接受固定报错格式与配置文件翻译层，可切换到
import-linter（`lint-imports --config`），layers.yaml 的字段设计已与之兼容（见下）。

**注意事项**：grimp/import-linter 均要求被分析包可被定位（模板项目为 src 布局，
`make verify` 的 build 段需先 `pip install -e .`，或在脚本内把 `src/` 加入
`sys.path` 后按目录名定位根包）。

## `.harness/layers.yaml` 字段建议

字段设计同时适配首选（grimp API）与备选（import-linter layers 契约），字段命名
尽量向两者靠拢以降低切换成本：

```yaml
# .harness/layers.yaml —— 分层架构声明（唯一事实来源）
version: 1

# 被分析的根包（可多个）。对应 grimp.build_graph(*names) /
# import-linter 的 root_packages。
root_packages:
  - mypackage

options:
  # TYPE_CHECKING 守卫内的 import 不计入图（两侧工具都支持）
  exclude_type_checking_imports: true
  include_external_packages: false

contracts:
  - name: main-layers            # 报错时引用的契约名
    # 层容器（相对层名时必填）；对应 containers 参数
    containers: [mypackage]
    # 层序：从高到低。高层可 import 低层，反之违规（含间接链）
    layers:
      - cli                      # 单层
      - services
      - repositories
      - { siblings: [adapters_x, adapters_y], independent: true }  # 同层兄弟
    # 可选：声明式豁免（逃生舱，需写明理由）
    ignore:
      - from: mypackage.legacy.shim
        to: mypackage.cli
        reason: "迁移期豁免，2026-12 前移除"
```

映射关系：
- `layers`（高→低序列）→ grimp `layers` 元组 / import-linter `layers` 列表
- `containers` → 两者同名参数
- `siblings.independent` → grimp `set` 或 `grimp.Layer(..., independent=False)` / import-linter `|` 与 `:` 分隔符
- `ignore` → grimp 侧在胶水层过滤，import-linter 侧映射为 `ignore_imports`

## 后续票据衔接

- W03（分层声明协议设计）可直接采用上文 YAML schema 作为草案。
- W05/W07（validate / 预验证脚本）可复用 `lint_deps.py` 的图查询能力
  （如 `verify_action.py --action "import A from B"` 直接调 `chain_exists`）。
