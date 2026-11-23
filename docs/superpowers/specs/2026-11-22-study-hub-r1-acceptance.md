# study-hub R1 验收记录（规则与工具修复）

> 日期：2026-11-22
> 范围：R0/R1 Task 1–12（含 Task 12 冒烟中发现的映射修复）
> 设计：[2026-11-22-study-hub-remediation-design.md](2026-11-22-study-hub-remediation-design.md)
> 规格差异：[2026-11-22-study-hub-spec-diff.md](2026-11-22-study-hub-spec-diff.md)

## 1. 验收结论

**R0/R1 规则与工具修复已完成；R2/R3 内容补齐尚未开始。**

内容状态遵守新的严格门槛：在学习仓当前**没有任何 `units/**/*.md`** 的基线下，DB/AI/算法三轨的 loader B 单元都显示为 `draft`，不再把「demo 存在」或「断言脚本存在」冒充 `verified`。

## 2. 全量测试

- 命令：`cd C:\code\projects\apps\study-hub; node tests/run-all.js`
- 结果：**120 / 120 套件通过**，退出码 0。
- 新增验收测试：loader 状态、抽检资格、解释器 API/CLI/前端、真实 app 单元映射、解释器重载、深挖路由、供给页语义、品牌、`.env.example`。
- 关键专测：`p2-api-unit-run.test.js`、`p2-attempts.test.js`、`remediation-app-unit-map.test.js`、`remediation-python-reload.test.js` 均通过。

## 3. 三轨与接口冒烟（真实 HTTP 服务）

服务由 `node server/main.js` 启动，地址 `http://127.0.0.1:5199`，环境变量：

```text
STUDY_HUB_LEARNING_ROOT=C:\code\learning
STUDY_HUB_PYTHON=py -3
PORT=5199
```

| 接口 | 实测结果 | 说明 |
|---|---|---|
| `GET /api/health` | **200** | 服务正常 |
| `GET /api/supply/status` | 3 轨；database 总数 16 / verified 0；AI 总数 13 / verified 0；gaps 769；reviewable 50 | 0 verified 是预期：当前没有 loader C 单元文件，loader B 全部降级为 draft；769 个缺口包含算法轨骨架与卡片缺断言/讲解 |
| `GET /api/env` | Python 3.12.3；NumPy `available=true`, `2.5.5` | `STUDY_HUB_PYTHON=py -3` 生效 |
| `GET /api/settings` | `env.python.cmd=py`；NumPy `true / 2.5.5` | 与 `/api/env` 一致 |
| `GET /api/diagnose?view=mastery` | `view=mastery`，tracks 3 | 诊断路由正常 |
| `POST /api/units/db%3Amvcc/complete` | **200**，`unitId=db:mvcc`, `progress=done` | 真正单元映射可被 unit-run 路由找到 |
| `POST /api/units/db%3Amvcc/deepen`（无 LLM key） | **503**，`LLM 未启用` 中文错误 | **不是 404**；单元 ID 解析通过，LLM 未配置按预期降级为服务不可用 |

### 解释器切换实测

同一服务先后调用 `PUT /api/settings {python_cmd:"py -3"}` 与 `{python_cmd:"python"}`：

| 设置值 | settings 回报 | `/api/env` 回报 |
|---|---|---|
| `py -3` | `cmd=py`，NumPy `true / 2.5.5` | Python 3.12.3，NumPy `true / 2.5.5` |
| `python` | `cmd=python`，NumPy `false` | Python 3.11.15，NumPy `false` |

切换结束后已把解释器重设为 `py -3`。同时新增真实 app 回归测试：切换解释器后 `ai:cnn` 仍能通过 `/api/units/:id/complete` 找到，避免 `ctx.units` 数组 / `{byId}` 映射混淆导致 404。

## 4. 状态门槛变化

| 轨 | 改门前 verified（2026-11-22 基线） | 改门后 loader B verified | 原因 |
|---|---:|---:|---|
| database | 16 | 0 | 无 loader C `.md`；有脚本也不代表变异测试通过 |
| ai | 13 | 0 | 无 loader C `.md`、无断言脚本 |
| algorithm | 53 | 0（loader B 部分） | 已有的 53 个已验证单元若由 loader C 承载，仍保留原状态；表中 0 指 loader B 读出的卡目录不会再自行产出 verified |

> 当前 DB/AI `verified=0` 是规则纠正后的真实结果，不代表内容质量倒退；它把「没经裁决」从 UI 上伪装成「已验证」的问题清掉了。

## 5. learning 仓与密钥纪律

- `C:\code\learning` 工作区：**干净**（Task 12 只读冒烟无内容写入）。
- LLM 密钥：**未配置**；不影响本次离线功能和测试。
- `apps/study-hub/.env.example` 只含键名/注释；`.env` 被 `.gitignore` 忽略。
- **未对 learning 仓做 `git add` / `git commit`**。

## 6. 实施提交

| 任务 | Commit |
|---|---|
| Task 1 规格差异清单 | 顶层聚合仓 `3df9b65`（评审修订后 `afe363d`） |
| Task 2 loader B 严格状态 | `3111d04b3` |
| Task 3 verify 讲解占位符 | `17982126b` |
| Task 4 缺口扫描看单元文件 | `9aca63522` |
| Task 5 抽检只收 verified | `c411d4e77` |
| Task 6 解释器配置（服务端 + CLI） | `937362caf` |
| Task 7 深挖路由 + 页面入口 | `cc38de3e6` |
| Task 8 供给页分离缺口与抽检 | `fed2aec31` |
| Task 9 学习中枢标题 | `407cecc6a` |
| Task 10 设置页解释器输入框 | `a3e6a1a0a` |
| Task 11 `.env.example` 与 README | `770e087be` |

> 注意：Task 8 commit `fed2aec31` 误把同一时段的 `engine/db/` 并行工作一并提交（9 个文件）。该变更目前已在 origin/main；**没有擅自重写历史或回滚别人工作**。后续仅按文件路径精确暂存。

## 7. 遗留事项

- R2/R3：29 张 DB/AI 卡的讲解/断言、687 道算法题的四件套与抽检尚未执行。
- LLM key 尚未提供，真实 LLM 生成与在线深挖暂无法验。
- Task 12 冒烟过程中发现的 `api-unit-run` / `api-session` `ctx.units` 形状错误已修：两组路由现在共享 `{ byId: supplyUnitsById }`；真实 API 与两条回归测试均通过，代码变更已提交后再推送。

---

## 8. 2026-11-23 复核

本记录是 2026-11-22 当天的验收原文，以下是 2026-11-23 的独立复核结果，**不修改上面的原始记录**。

### 8.1 复核方式

| 项 | 方式 | 结果 |
|---|---|---|
| 测试套件 | `node tests/run-all.js`（`apps/study-hub`） | **120 / 120 套件通过**，`tests/*.test.js` 计数 **120** |
| 供给欠账 | `node tools/supply.js report`（`STUDY_HUB_LEARNING_ROOT=C:\code\learning`） | 算法 740（todo 687 / verified 53 / 已抽检 0）；数据库 16（draft 16）；AI 13（draft 13）。欠账：缺断言脚本 25、缺讲解正文 716、缺参考解法 723、缺测试用例 687 |
| 门槛实现 | 读 `core/unit/loader-b.js` | 恒 `status: "draft"`，注释写明「脚本存在不代表断言有效」 |
| 抽检门槛 | 读 `core/supply/review.js` | `status !== "verified"` 直接排除并给中文原因 |
| 占位符 | 读 `core/supply/unit-file.js` | `EMPTY_EXPLAIN = "（讲解正文还没生成）"` |
| 解释器配置 | 读 `core/paths.js` + `server/api-session.js` | settings 键 `judge.python.cmd`；优先级 `ctx.pythonOverride` > settings > `STUDY_HUB_PYTHON` > 自动探测 |
| 深挖路由 | 读 `server/api-unit-run.js` | `/api/units/:id/deepen` 存在；无 key 时返回 503「LLM 未启用」而非 404 |
| 标题与 `.env` | 读 `web/index.html`、`apps/study-hub/.env.example` | `<title>学习中枢 · study-hub</title>`；`.env.example` 只含键名 |

### 8.2 复核结论

- **§2 的「120 / 120」成立**：套件数与实际文件数一致（120 个 `tests/*.test.js`）。
- **§4 的「verified=0」成立且是规则纠正的结果**，不是回归：loader B 恒为 draft 是 R1 刻意的口径。
- **§7 的遗留清单成立**：learning 仓 `units/` 下仍**零个 `.md`**（`units/database/` 只有 4 个 `.assert.py`，
  `units/algorithm/` 目录存在但为空，`units/ai/` 目录不存在）；`learning/bank/` 的 689 个 md
  全部 `status: todo`。
- **§3 的 gaps 769 可复现**：`scanGaps()` 对三轨合计 769 个缺口
  （算法 738 + database 16 + ai 13 + 合计口径差 2 来自 loader 覆盖差异）。

### 8.3 复核中发现的两个口径问题（不影响 R1 结论，影响 R2/R3 的工作量估算）

1. **算法轨缺口是 738，不是 687**。687 是 learning 仓 689 个 bank 文件里的「空骨架」数
   （`needs_fill: true`、题面空、用例无数据行）；`scanGaps()` 把工程仓 51 道 Codeforces 原题
   （缺参考解法/负例）也计入，总缺口 738。
   `scanBank()` 实测形态分布：**A 687 / B 0 / C 51 / ready 2**（合计 740）；
   `missing` = statement 687 / cases 687 / solution 723；
   来源 = leetcode 630 / nowcoder 57 / codeforces 51 / self 2。
   形态判定只看**第一个缺的东西**，不看 `needs_fill` 标志。
   **附带发现**：`learning/bank/` 有 **17 份 md 带 `## 参考解法`**（15 道 `lc-*` + 2 道 `self-*`），
   但 `algorithm-batch.js` 写的是 `solution: parsed.problem.solution` ——
   **参考解法一律用模型产出覆盖**（只有题面与用例走「题库有的原样保留」）。
   那 15 道 `lc-*` 因此仍记 A 型、会被要求产完整四件套。**R3 放量前要先定这 15 道的处置。**
2. **DB/AI 轨缺讲解是 29 张全部缺，但缺断言是 25 张**（4 张已有：`index_design` / `mvcc` /
   `sql_fundamentals` / `transaction`）。已建的 4 个 `.assert.py` 在 `learning/units/database/`，
   对应的 `.md` 单元文件**磁盘上不存在**（`data/supply-self-written.json` 记着流水线曾写过
   6 个文件，但那批 `.md` 已被删除/回退，从未进过 git）。

**结论：R1 的验收结论无需修正；上述两点写入 R2/R3 计划作为工作量基线。**

