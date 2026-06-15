# Release Checklist (harness-init)

> 配套 `AGENTS.md` §3 step 5 的发版细化清单。
> 本仓库为 **脚手架生成器**，存在双重身份：包版本号 vs 模板内的版本号字符串。读全文再动手。

## 1. SemVer 决策

| 改动类型 | 版本跳变 | 备注 |
|---|---|---|
| 删除/重命名 CLI 命令、改默认行为 | MAJOR | 用户脚本会断 |
| 新增命令、参数、模板类型 | MINOR | 向后兼容 |
| Bug 修复、文档、模板内容微调 | PATCH | **模板改动归 PATCH**（不影响存量项目） |

PyPI 不允许覆盖发布，必须升号；查询：`pip index versions harness-init`。

## 2. 版本号同步矩阵（关键反陷阱）

| 文件 | 改不改 | 说明 |
|---|---|---|
| `pyproject.toml` `[project] version` | ✅ 必改 | PyPI 元数据 |
| `src/harness_init/__init__.py` `__version__` | ✅ 必改 | 运行时读取 |
| `src/harness_init/cli.py` `--version` 输出 | ❌ 不改 | 已经动态读 `__version__`，无硬编码 |
| `src/harness_init/core.py` 含 `__version__ = "0.1.0"` | ⛔ 绝不改 | 注入到生成项目的字符串 |
| `src/harness_init/templates/*/pyproject.toml` `version = "0.1.0"` | ⛔ 绝不改 | 是模板内容，不是本包版本 |
| `docs/spec/PBH-SPEC.md` 协议版本 | ⛔ 不联动 | PBH-SPEC 协议版本与包版本独立演化 |

**精准 grep（排除模板）**：
```powershell
grep "<old-version>" --include="*.py" --include="*.toml" -l | Where-Object { $_ -notmatch "templates" }
```
直接全仓 grep 会大量误报模板里的 `0.1.0`，必须排除 `templates/`。

## 3. CHANGELOG

格式参考 [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)。新增 `## [X.Y.Z] - YYYY-MM-DD`，至少包含 Added / Changed / Fixed / Removed 之一；写**用户能感知**的变化，不是内部 commit log。

## 4. 本地预飞行（任何一项失败 → 不要打 tag）

```powershell
make verify                         # 期望 [OK] verified + coverage >= 85%
python -m build --outdir dist-tmp   # 生成 sdist + wheel
twine check dist-tmp/*              # 期望 PASSED PASSED
Remove-Item dist-tmp -Recurse       # 清理
```

## 5. PR 流程（推荐，非强制）

发版改动建议走 PR 而非直接 push：

```powershell
git checkout -b release/v<X.Y.Z>
# 改版本号 + CHANGELOG
git commit -m "release: v<X.Y.Z>"
git push -u origin release/v<X.Y.Z>
gh pr create --fill
# CI 通过后
gh pr merge --squash --delete-branch
```

## 6. 打 tag 与发布

```powershell
git checkout master
git fetch origin
git pull --ff-only origin master
git tag -a v<X.Y.Z> -m "v<X.Y.Z>"   # annotated，不要 lightweight
git push origin v<X.Y.Z>             # 触发 publish.yml
```

`publish.yml` 已内嵌 `make verify` 门禁（commit `d68d53a`），verify 失败会自动阻止 publish。

## 7. 发布后验证（不能假设成功）

```powershell
gh run list --workflow=publish.yml --limit 1   # 全 3 job 都要 success
curl https://pypi.org/pypi/harness-init/<X.Y.Z>/json  # 期望 200
gh release view v<X.Y.Z>                       # 期望含 .whl + .tar.gz
```

`skip-existing: true` 是双刃剑：版本号没升时会静默跳过、workflow 仍 success。**必须查 publish job 日志看到 `Uploading harness-init-<X.Y.Z>`**。

## 8. 收尾

`git status -sb` 干净 + `git ls-remote --tags origin` 含新 tag + 与 origin 同步。
