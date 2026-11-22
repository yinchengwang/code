# study-hub 规格差异清单（R0 交付物）

> 日期：2026-11-22
> 用途：本轮补齐工程的验收依据。每一条都核实到**真实文件:行号**。
> 设计：[2026-11-22-study-hub-remediation-design.md](2026-11-22-study-hub-remediation-design.md)

---

## 0. 规格来源

| 规格文件 | 路径 | 内容版本 | 角色 |
|---|---|---|---|
| 原整体设计 | `docs/superpowers/specs/2026-11-12-study-hub-design.md` | 2026-11-12 | 蓝图（本轮以它为背景） |
| 接口契约 | `docs/superpowers/plans/2026-11-12-study-hub-接口契约.md` | 2026-11-21 | **最新事实来源**，冲突时以它为准 |
| 补齐设计 | `docs/superpowers/specs/2026-11-22-study-hub-remediation-design.md` | 2026-11-22 | 本轮范围与门禁 |

**判定词**（只用这五个）：已实现 · 部分实现 · 未实现 · 与现规格冲突 · 明确排除
**处置词**（只用这两个）：本轮实现 · 登记不实现（必须写理由）
**`—`** = 不需处置（仅用于判定为「已实现」或「明确排除」的行）。

---

## 1. 状态门槛与供给语义

| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-01 | 卡缺断言脚本时的 `status` | 补齐设计 §3.2 | `core/unit/loader-b.js:123` `status: hasDemo ? "verified" : "draft"` | 与现规格冲突 | 本轮实现 | `tests/remediation-loader-status.test.js` |
| D-02 | 脚本存在但未经 `verify` 裁决时的 `status` | 补齐设计 §3.2 变更二 | 同上 `core/unit/loader-b.js:123` | 与现规格冲突 | 本轮实现 | 同上（第二条用例） |
| D-03 | `verify` 新建单元文件时的讲解内容 | 补齐设计 §4.4 | `core/supply/verify.js:179-215`，`renderUnitFile(fields, { explain: String(unit.statement \|\| "") })`（第 210–213 行） | 与现规格冲突 | 本轮实现 | `remediation-loader-status.test.js` 第四条用例 |
| D-04 | 缺口扫描认不认「占位符讲解」 | 补齐设计 §4.4 | `core/supply/plan.js:86`，只看 `unit.statement` 空/占位 | 部分实现 | 本轮实现 | 同文件第五、六条用例 |
| D-05 | 抽检对象的资格 | 补齐设计 §6.2 | `core/supply/review.js:61-64`，只判 `reviewed !== true`，不看 `status` | 与现规格冲突 | 本轮实现 | `tests/remediation-review.test.js` |
| D-06 | 抽检打回**不暂停整轨** | 补齐设计 §3.4 | 打回只写 `status: rejected`（`core/supply/review.js:109`），不中断 | 已实现 | — | 人工抽检时观察 |
| D-06b | 抽检打回后**该层样本扩大**（默认 2 倍，最少 +5） | 补齐设计 §3.4 | `core/supply/review.js:74` `sample` 只看 `opts.sample`，无分层/扩容逻辑；全仓 `扩大\|扩容\|expandSample` **0 处** | 未实现 | 本轮实现（属 R2/R3 计划 Task 14 / Task 22） | `remediation-review.test.js` 分层用例 |
| D-07 | 算法轨分层抽样 | 补齐设计 §3.4 | `core/supply/review.js:57-75` 只有「按状态排序取前 N」；`core/supply/algorithm-cli.js:30` `COMMANDS` 无 `review` | 未实现 | 本轮实现（属 R2/R3 计划 Task 14） | `remediation-review.test.js` 分层用例 |

---

## 2. 判题环境

| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-08 | 判题解释器可从 Web 配置 | 补齐设计 §5 | `server/api-session.js:756` 起的 `PUT /api/settings` 校验段（822–829 行）**不含** `python_cmd`；键常量在 `:35` `KEY_PYTHON = "judge.python.cmd"` | 未实现 | 本轮实现 | `tests/remediation-settings-python.test.js` |
| D-09 | 环境探测随解释器变化重算 | 补齐设计 §5 | `server/api-session.js:142-150` `createEnvProbe` 缓存 `cached` 后永不失效 | 与现规格冲突 | 本轮实现 | 同上（切换解释器用例） |
| D-10 | `GET /api/settings` 的 env 段带上解释器与 numpy 版本 | R1 计划 Task 6 Step 5 | `server/api-session.js:131-134` `probeEnv` 只回 `{ok, detail}`，无 `version` / `cmd`。（注：`/api/env` **本来就回** version，见 `server/api-unit-run.js:299-304`——缺口只在 settings 的 env 段） | 部分实现 | 本轮实现 | 同上 |
| D-11 | 单元索引随解释器重扫 | R1 计划 Task 6 Step 7 | `server/app.js:351-352` 启动时 `loadUnits(unitOpts)` + `refreshUnitIndex` 一次；全仓 `reloadUnits` **0 处** | 部分实现 | 本轮实现 | `PUT /api/settings` 后 `/api/supply/status` 的 numpy 结论翻转 |
| D-12 | 设置页可改解释器 | 补齐设计 §5 | `web/pages/settings.js:123-135` `envRows` 只有 Python / NumPy 两行只读状态 | 未实现 | 本轮实现 | `remediation-settings-python.test.js` 前端用例 |
| D-13 | 解释器优先级一致（**服务端**三处） | 补齐设计 §5 | `server/api-session.js:369-377`、`server/api-unit-run.js:85-92`、`server/app.js:349` 三处都已是 `ctx注入 > settings > envPython` | 已实现 | — | 代码对读 |
| D-13b | 解释器优先级一致（**离线 CLI**） | 补齐设计 §5（`全部读同一配置` 含 `supply verify`） | `tools/supply.js:373-378` 的 `loadUnits({...})` **不传 `pythonOverride`**；`:588-594` 的 `verifyBatch({...})` **也不传**（`core/supply/verify.js:295` 支持该参数）；`tools/supply.js` 全文 `resolvePythonOverride` / `STUDY_HUB_PYTHON` **0 处** | 未实现 | 本轮实现 | 设 `STUDY_HUB_PYTHON=py -3` 后 CLI 的 numpy 结论翻转 |
| D-14 | 缺 numpy 时明确降级不崩 | 补齐设计 §3.3 | `core/unit/loader-b.js:98-104` 写 warning；`core/supply/verify.js:302-314` 判 `skipped`；`judge/runner.js:309-311` 判「环境缺失」 | 已实现 | — | 已有测试覆盖 |
| D-14b | 提供 `.env.example`（键名 + 注释，无真实值），README 指向它 | 补齐设计 §7.1 | `apps/study-hub/.env.example` **不存在**（`Test-Path` = False）；`README.md` 有「## 环境变量」小节但未指向模板 | 未实现 | 本轮实现 | R1 Task 11 |

---

## 3. Web / API

| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-15 | 深挖概念在线场景 | 原设计 §7.1 场景 5 | 服务层有 `core/llm/service.js:555` `async function deepen`；**`server/` 下 0 处路由**；`web/` 无入口 | 部分实现 | 本轮实现 | `tests/remediation-deepen.test.js` |
| D-16 | 供给页缺口与抽检分离 | 补齐设计 §6.2 | `web/pages/supply.js:146-147` 缺口项挂着「通过 / 打回」按钮 | 与现规格冲突 | 本轮实现 | `tests/remediation-supply-web.test.js` |
| D-17 | 供给接口给出待抽检列表 | 补齐设计 §6.2 | `server/api-supply.js:48-52` 只回 `{tracks, gaps, warnings}`，无 `reviewable` | 未实现 | 本轮实现 | 同上 |
| D-18 | 应用标题与页头 | 补齐设计 §6.2 | `web/index.html:6` `<title>算法能力计划</title>`；`:12` 页头同样 | 与现规格冲突 | 本轮实现 | `tests/remediation-brand.test.js` |
| D-19 | 会话首页「上次还有 N 个没做完」 | 原设计 §8.2 | `server/api-session.js:484` `notice: left > 0 ? "上次还有 " + left + " 个没做完" : ""` | 已实现 | — | R1 Task 12 冒烟 |
| D-20 | 诊断页三视图 | 原设计 §8.2 | `server/api-diagnose.js:290` 一条路由，`?view=mastery\|radar\|heatmap`（文件头注释 6–8 行）；`web/diagnose.js` 页内标签切换 | 已实现 | — | R1 Task 12 冒烟 |
| D-21 | 单元库按轨浏览与搜索 | 原设计 §8.1 | `server/api-units.js:78` `GET /api/units`（支持 track/q）；`web/pages/library.js:301` | 已实现 | — | 冒烟 |
| D-22 | hash 路由 `#/unit/:id` | 契约 §9.2 | `web/app.js:121` `parseHash`、`:159` `applyHash`；`tests/p2-hash-route.test.js` | 已实现 | — | 已有测试 |
| D-23 | `GET /api/next` 废弃标记 | 契约 §13 | `server/api.js:122-124` `deprecated: true` + 中文提示 | 已实现 | — | 冒烟时看响应字段 |
| D-24 | LLM 工作台独立页面 | 原设计 §8.1 | `web/llm.js:724-729` 自挂载到 `#view` 顶部（`insertBefore`），**不是** `pages` 注册 | 与现规格冲突 | **登记不实现** | — |

> **D-24 为何登记不实现**：契约 §9.1 第 1560 行原文写明
> 「`llm: { ... }  // P6 不在本轮，沿用 web/llm.js 自挂载」，
> 且 `web/index.html` 的脚本清单里 `llm.js` 在 `app.js` 之后、页面脚本之前加载（注释说明「自挂载，不改 app.js」）。
> 改成独立页面要动 `app.js` 的 `TABS`、`pages` 注册表、`index.html` 三处，
> 收益只是「多一个导航标签」，而现方案在每个页面顶部都能用。**P6 明确不在本轮范围。**

---

## 4. 明确排除项

| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-25 | `scaffold/db` 的 51 个 C 内核目录 | 原设计 §2.3 | `C:\code\learning\scaffold\db\` 实测 **51 个目录** | 明确排除 | 登记不实现（理由见下） | — |
| D-26 | 自动安装 NumPy 或 Python 依赖 | 补齐设计 §1.3 | `apps/study-hub` 全仓无 `pip install` / `ensurepip` / `apt-get`（实测 **0 处**） | 明确排除 | 登记不实现（理由见下） | — |
| D-29 | `learning/notes/` 重复目录与空文件清理 | 原设计 §12 | `notes/DB/`、`notes/vectordb/vectordb.md`、`interview/database/SQL.md` 实测 **0 字节** | 明确排除 | 登记不实现（理由见下） | — |

**D-25 理由**：原设计 §2.3 原文「列为本轮之后的扩展，不纳入 P0–P5」；
其断言脚本要 C 编写、变异手法与 Python 卡不同，是独立的一摊工作量。

**D-26 理由**：改机器状态风险高（网络、权限、多解释器冲突）；
本机 `py -3` 已带 numpy 2.5.5，靠配置收敛即可（D-08/D-12 就是配这个的入口）。

**D-29 理由**：原设计 §12 原文「本轮不清理，但供给流水线遇到这些会标"问题条目"」。

---

## 5. 约束守住项

| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-27 | 零 npm 依赖 / 无前端框架 / 零构建 | 原设计 §1.7 | `package.json:10` `"dependencies": {}` | 已实现 | — | 代码对读 |
| D-28 | 零第三方图表库 | 原设计 §1.7 | `web/charts.js:14`「手绘 SVG 的纯函数层」 | 已实现 | — | 代码对读 |

---

## 6. 统计

| 判定 | 条数 | 条目 |
|---|---|---|
| 与现规格冲突 | 7 | D-01, D-02, D-03, D-05, D-09, D-16, D-18 |
| 未实现 | 7 | D-06b, D-07, D-08, D-12, D-13b, D-14b, D-17 |
| 部分实现 | 4 | D-04, D-10, D-11, D-15 |
| 已实现 | 9 | D-06, D-13, D-19, D-20, D-21, D-22, D-23, D-27, D-28 |
| 明确排除 | 3 | D-25, D-26, D-29 |
| 登记不实现（冲突项） | 1 | D-24 |

合计 **31 条**。

**要改的：18 条**
- R1 阶段 16 条：D-01～D-05、D-06b、D-08～D-12、D-13b、D-14b、D-15～D-18
- R2/R3 阶段 2 条：D-06b（扩容部分）、D-07

**登记不实现：4 条**（D-24、D-25、D-26、D-29）
**确认不需改动：9 条**（D-06、D-13、D-19～D-23、D-27、D-28）

---

## 7. 与两份实施计划的对应

| 计划任务 | 覆盖的差异项 |
|---|---|
| R1 Task 2（loader B 门槛） | D-01, D-02 |
| R1 Task 3（verify 讲解占位符） | D-03 |
| R1 Task 4（缺口扫描） | D-04 |
| R1 Task 5（抽检资格） | D-05 |
| R1 Task 6（解释器服务端） | D-08, D-09, D-10, D-11, **D-13b** |
| R1 Task 7（深挖接线） | D-15 |
| R1 Task 8（供给页语义） | D-16, D-17 |
| R1 Task 9（标题品牌） | D-18 |
| R1 Task 10（设置页解释器） | D-12 |
| R1 Task 11（`.env.example`） | **D-14b** |
| R1 Task 12（验收） | D-19～D-23 的冒烟确认 |
| R2/R3 Task 14（分层抽样） | D-07, D-06b（分层 + 扩容） |
| R2/R3 Task 22（算法分层抽检） | D-06b（扩容的实测确认） |

**⚠️ 对计划的修订要求**（本清单发现的、计划里还没写进去的）：
1. **R1 Task 6 的 Files 要加 `tools/supply.js`** —— D-13b 只能在 CLI 里修，
   而现在 Task 6 的 Files 只列了 `server/api-session.js` 与 `server/app.js`（计划第 749–751 行）。
2. **R1 Task 5 的抽检规则要注意 D-06b** —— Task 5 只改「谁有资格被抽检」，
   扩容逻辑落在 R2/R3 Task 14；两处不要重复实现同一件事。

没有遗漏的规格、也没有超出范围多做。
