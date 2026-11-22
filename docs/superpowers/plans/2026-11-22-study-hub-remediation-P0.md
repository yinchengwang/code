# study-hub 补齐与收尾 — R0/R1 实施计划（规则与工具修复）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 study-hub 的「内容状态门槛」「供给/抽检语义」「判题解释器配置」三处规则修对，
并产出规格差异清单，让后续内容补齐（R2/R3）建立在可信的判定口径上。

**Architecture:** 纯函数层（`core/`）改判定口径 → 服务层（`server/`）改接口与配置 → 前端（`web/`）改呈现。
每一层都有独立测试文件兜底；本计划**不依赖任何 LLM 密钥**，全部离线可验。

**Tech Stack:** Node ≥ 24（内置 `node:sqlite` / `node:test`）、零 npm 依赖、零构建、原生 JS 前端。

## Global Constraints

- 仓库根目录：`C:\code\projects`（工程仓，git 远端 `origin` = `github.com/yinchengwang/projects`）
- 应用目录：`C:\code\projects\apps\study-hub`；学习仓：`C:\code\learning`（独立 git 仓）
- 设计文档：`C:\code\docs\superpowers\specs\2026-11-22-study-hub-remediation-design.md`
- **零 npm 依赖、零构建**：只用 Node 内置模块与原生浏览器 JS
- **零第三方图表库**：`web/charts.js` 手绘 SVG 纯函数层沿用
- **单一暗色主题**：不动 `web/style.css` 的 `:root` 变量集
- **注释与 commit message 用中文**（`projects/CLAUDE.md` 铁律）
- **绝不自动 `git add` / `git commit`** learning 仓的内容产物；工程仓代码按任务要求提交并推送
- **LLM 密钥只从环境变量 / `.env` 读**，不进代码、不进 settings 表、不进 git
- 判题解释器优先级：`ctx 注入` > `settings.judge.python.cmd` > `STUDY_HUB_PYTHON` > 自动探测
- 测试入口：`node tests/run-all.js`（在 `apps/study-hub` 下运行）
- 本计划的每个任务结束时 `node tests/run-all.js` 必须全绿

---

## 文件结构（本次会改动的文件）

| 文件 | 职责 | 动作 |
|---|---|---|
| `core/unit/loader-b.js` | 卡目录 → Unit；决定卡的 `status` | 改：`verified` 只由 loader C 承载 |
| `core/supply/verify.js` | 执行器反向校验 + 变异测试 | 改：建单元文件时讲解写占位符 |
| `core/supply/plan.js` | 缺口扫描 | 改：缺口判定纳入「无 loader C 文件」 |
| `core/supply/review.js` | 抽检写回 | 改：只允许抽检已达标单元 |
| `core/supply/unit-file.js` | 单元文件读写 | 改：导出 `EMPTY_EXPLAIN` 常量 |
| `server/api-session.js` | 会话 + 设置接口 | 改：`PUT /api/settings` 收解释器；环境探测不缓存 |
| `server/api-supply.js` | 供给接口 | 改：状态响应带「待抽检」列表 |
| `server/api-unit-run.js` | 判题 / 完成 / 问 LLM / 环境自检 | 改：新增 `deepen` 路由 |
| `web/pages/settings.js` | 设置页 | 改：解释器输入框 |
| `web/pages/supply.js` | 供给页 | 改：缺口只读、抽检独立 |
| `web/pages/unit.js` | 单元学习页 | 改：深挖入口 |
| `web/index.html` | 应用外壳 | 改：标题与品牌文案 |
| `tests/unit-loader-b.test.js` | loader B 单测 | 改：按新口径重写 |
| `tests/p2-loader-b.test.js` | 真实 learning 仓验收 | 改：按新口径重写 |
| `tests/remediation-loader-status.test.js` | **新建**：状态门槛闸门 | 新建 |
| `tests/remediation-review.test.js` | **新建**：抽检语义闸门 | 新建 |
| `tests/remediation-settings-python.test.js` | **新建**：解释器配置闸门 | 新建 |
| `tests/remediation-deepen.test.js` | **新建**：深挖路由闸门 | 新建 |
| `tests/remediation-supply-web.test.js` | **新建**：供给页语义闸门 | 新建 |

---

### Task 1: 规格差异清单（R0 交付物）

**Files:**
- Create: `C:\code\docs\superpowers\specs\2026-11-22-study-hub-spec-diff.md`

**Interfaces:**
- Consumes: 设计文档 `2026-11-22-study-hub-remediation-design.md`；契约 `2026-11-12-study-hub-接口契约.md`
- Produces: 一份差异清单文档，后续任务的验收以它为准

- [ ] **Step 1: 盘点三份规格的来源**

逐项列出并写进清单表格的规格来源：

```markdown
| 规格文件 | 路径 | 最后修改 | 角色 |
|---|---|---|---|
| 原整体设计 | `docs/superpowers/specs/2026-11-12-study-hub-design.md` | 2026-11-12 | 蓝图（本轮以它为背景） |
| 接口契约 | `docs/superpowers/plans/2026-11-12-study-hub-接口契约.md` | 2026-11-21 | **最新事实来源**，冲突时以它为准 |
| 补齐设计 | `docs/superpowers/specs/2026-11-22-study-hub-remediation-design.md` | 2026-11-22 | 本轮范围与门禁 |
```

- [ ] **Step 2: 逐条比对并填判定列**

清单**每一行**都要有这六列，不许留空：

```markdown
| # | 条目 | 规格出处 | 当前实现（文件:行） | 判定 | 处置 | 验收方式 |
|---|---|---|---|---|---|---|
| D-01 | 卡缺断言脚本时的 status | 补齐设计 §3.2 | `core/unit/loader-b.js:123` | 与现规格冲突 | 本轮实现 | Task 2 测试 |
| D-02 | 判题解释器可配置 | 补齐设计 §5 | `server/api-session.js:786`（白名单缺该键） | 未实现 | 本轮实现 | Task 6 测试 |
| D-03 | 深挖概念在线场景 | 原设计 §7.1 场景 5 | `core/llm/service.js:555`（有实现）、`server/`（无路由） | 部分实现 | 本轮实现 | Task 7 测试 |
| D-04 | 供给页缺口与抽检分离 | 补齐设计 §6.2 | `web/pages/supply.js:146` | 未实现 | 本轮实现 | Task 8 测试 |
| D-05 | 应用标题 | 补齐设计 §6.2 | `web/index.html:6` | 未实现 | 本轮实现 | Task 9 测试 |
| D-06 | 单元索引重建时机 | 契约 §3.4 | `server/app.js:352`（启动时一次） | 部分实现 | 本轮实现 | Task 6 |
| D-07 | LLM 工作台独立页面 | 原设计 §8.1 | `web/llm.js`（自挂载，非 pages 注册） | 与现规格冲突 | 登记不实现（契约 §9.1 明确沿用自挂载） | — |
| D-08 | `scaffold/db` 的 51 个 C 目录 | 原设计 §2.3 | `learning/scaffold/db/` | 明确排除 | 登记不实现 | — |
```

判定词只用五个：**已实现 / 部分实现 / 未实现 / 与现规格冲突 / 明确排除**。
处置词只用两个：**本轮实现 / 登记不实现**（登记不实现必须写理由）。

- [ ] **Step 3: 核对清单条目数与真实缺口一致**

Run:

```powershell
cd C:\code\projects\apps\study-hub
Select-String -Path core\unit\loader-b.js -Pattern 'status: hasDemo' | ForEach-Object { "$($_.LineNumber)" }
Select-String -Path server\api-session.js -Pattern 'KEY_PYTHON' | ForEach-Object { "$($_.LineNumber)" }
```

Expected: 分别打出 loader-b 的 status 行号与 api-session 的 `KEY_PYTHON` 行号——用于填清单的「当前实现」列。
清单里每一条的「当前实现」列必须能对应到真实行号。

- [ ] **Step 4: 提交清单**

```bash
cd C:\code
git add docs/superpowers/specs/2026-11-22-study-hub-spec-diff.md
git commit -m "docs(spec): 新增 study-hub 规格差异清单"
git push origin main
```

---

### Task 2: 收紧卡的 `verified` 门槛（loader B）

**Files:**
- Modify: `projects/apps/study-hub/core/unit/loader-b.js:82-129`
- Modify: `projects/apps/study-hub/tests/unit-loader-b.test.js:94-107`
- Modify: `projects/apps/study-hub/tests/p2-loader-b.test.js:152`
- Test: `projects/apps/study-hub/tests/remediation-loader-status.test.js`（新建）

**Interfaces:**
- Consumes: `parseCardDirectory(dirAbs, opts)`，`opts.unitsDir` 为 `learning/units` 绝对路径
- Produces: `parseCardDirectory` 的 `unit.status` 只可能是 `"draft"`（卡从未 verified）；
  `verified` 由 loader C 的单元文件承载

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-loader-status.test.js`：

```js
"use strict"
/**
 * remediation-loader-status.test.js —— 状态门槛闸门
 *
 * 补齐设计 §3.2：verified 只能由 loader C（verify 写回的单元文件）承载。
 * loader B 单独加载一张卡时，最多给 draft——不管断言脚本在不在。
 * 理由：脚本存在 ≠ 校验通过。mvcc / index_design 的脚本存在但变异测试判 rejected，
 * 若「脚本存在即 verified」，这两张会被绕过裁决放回学习队列。
 */

const test = require("node:test")
const assert = require("node:assert/strict")
const fs = require("node:fs")
const path = require("node:path")

const loaderB = require("../core/unit/loader-b.js")
const { tmpDir } = require("./helpers/tmp.js")

/** 造一张卡目录；unitsDir 下可放断言脚本。 */
function makeCard(stem, opts) {
  const options = opts || {}
  const root = path.join(tmpDir("study-hub-status-"), stem)
  const dir = path.join(root, "card")
  fs.mkdirSync(dir, { recursive: true })
  fs.writeFileSync(path.join(dir, "README.md"), "# " + stem + "\n\n正文\n", "utf8")
  fs.writeFileSync(path.join(dir, "main.py"), "print('hi')\n", "utf8")
  const unitsDir = path.join(root, "units", "database")
  fs.mkdirSync(unitsDir, { recursive: true })
  if (options.withScript) {
    fs.writeFileSync(path.join(unitsDir, stem + ".assert.py"), "print('ok')\n", "utf8")
  }
  return { dir: dir, unitsDir: path.join(root, "units") }
}

test("断言脚本不存在 → draft（不是 verified）", function () {
  const card = makeCard("mvcc")
  const res = loaderB.parseCardDirectory(card.dir, { track: "database", unitsDir: card.unitsDir })
  assert.ok(res.unit)
  assert.equal(res.unit.status, "draft")
})

test("断言脚本存在但没有 loader C 单元文件 → 仍是 draft", function () {
  const card = makeCard("mvcc", { withScript: true })
  const res = loaderB.parseCardDirectory(card.dir, { track: "database", unitsDir: card.unitsDir })
  assert.ok(res.unit)
  assert.equal(res.unit.status, "draft", "脚本存在不等于校验通过，不能给 verified")
})

test("status 仍然只能是四档里的合法值", function () {
  const card = makeCard("mvcc", { withScript: true })
  const res = loaderB.parseCardDirectory(card.dir, { track: "database", unitsDir: card.unitsDir })
  assert.ok(["todo", "draft", "verified", "rejected"].indexOf(res.unit.status) !== -1)
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
```

Expected: FAIL —— 「断言脚本不存在 → draft」实际拿到 `verified`（`actual: 'verified' / expected: 'draft'`）。

- [ ] **Step 3: 改 loader B**

`core/unit/loader-b.js`，把 `status: hasDemo ? "verified" : "draft"` 改成：

```js
    // status 由「能不能学」决定，不由「内容是不是教材」决定。
    // verified 只能由 loader C 的单元文件承载（那是 verify 真跑过执行器与变异测试的裁决）。
    // loader B 单独加载时最多给 draft：断言脚本在不在都不能证明断言有效。
    // （补齐设计 §3.2；变更二：脚本存在但未经校验也不给 verified）
    status: "draft",
```

并把上面那段「断言脚本的期望落点」注释改成：

```js
  // 断言脚本的期望落点。恒填——「脚本该放哪」是卡片的属性；
  // 「脚本在不在」由 P2 的判题器判断（缺失 → compile_error），
  // 「脚本对不对」由 P4 的 verify 判断（变异测试抓不住 → rejected）。
  // **脚本存在不代表断言有效**，所以 loader B 不据此给 verified。
```

- [ ] **Step 4: 改既有两条断言**

`tests/unit-loader-b.test.js`，把：

```js
test("README 与 main.py 都在 → verified", function () {
  const dir = makeCard("mvcc")
  const res = loaderB.parseCardDirectory(dir, { track: "database" })
  assert.equal(res.unit.status, "verified")
})
```

改成：

```js
test("README 与 main.py 都在 → draft（verified 只能由 verify 写回）", function () {
  const dir = makeCard("mvcc")
  const res = loaderB.parseCardDirectory(dir, { track: "database" })
  assert.equal(res.unit.status, "draft")
})
```

`tests/p2-loader-b.test.js`，把：

```js
    assert.strictEqual(out.unit.status, "verified")
```

改成：

```js
    assert.strictEqual(out.unit.status, "draft", stem + " 未经 verify 裁决只能是 draft")
```

- [ ] **Step 5: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
node tests/unit-loader-b.test.js
node tests/p2-loader-b.test.js
```

Expected: 三个文件全部 PASS，无 FAIL。

- [ ] **Step 6: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/unit/loader-b.js apps/study-hub/tests/unit-loader-b.test.js apps/study-hub/tests/p2-loader-b.test.js apps/study-hub/tests/remediation-loader-status.test.js
git commit -m "fix(study-hub): verified 只由 loader C 承载，loader B 一律给 draft"
git push origin main
```

---

### Task 3: `verify` 建单元文件时讲解写占位符

**Files:**
- Modify: `projects/apps/study-hub/core/supply/unit-file.js`（导出 `EMPTY_EXPLAIN`）
- Modify: `projects/apps/study-hub/core/supply/verify.js:185-213`（`writeVerdict`）
- Test: `projects/apps/study-hub/tests/remediation-loader-status.test.js`（追加用例）

**Interfaces:**
- Consumes: `unitFilePath(unitsDir, unit)`、`renderUnitFile(fields, opts)`
- Produces: `unit-file.js` 导出 `EMPTY_EXPLAIN`（值 `"（讲解正文还没生成）"`）；
  `writeVerdict` 新建文件时 `## 讲解` 段写 `EMPTY_EXPLAIN`，不再塞 `unit.statement`

- [ ] **Step 1: 写失败的测试**

在 `tests/remediation-loader-status.test.js` 末尾追加（**Task 2 已建这个文件并写了 3 条用例，
追加到末尾、不要重写整份**——那 3 条钉住 loader B 一律给 draft）：

```js
const verify = require("../core/supply/verify.js")
const unitFile = require("../core/supply/unit-file.js")

test("verify 新建单元文件时讲解段是占位符，不是教材原文", function () {
  const root = tmpDir("study-hub-writeverdict-")
  const unitsDir = path.join(root, "units")
  fs.mkdirSync(path.join(unitsDir, "database"), { recursive: true })
  const unit = {
    id: "db:mvcc",
    track: "database",
    kind: "card",
    title: "MVCC",
    statement: "# MVCC\n\n这是 README 原文，不该进讲解段。\n",
    entry: { demo: "scaffold/grokking/mvcc/main.py", script: "units/database/mvcc.assert.py", language: "python" },
    source: "grokking",
  }
  const written = verify.writeVerdict(unit, "verified", {
    unitsDir: unitsDir,
    repoRoot: root,
    stateFile: path.join(root, ".self-written.json"),
  })
  assert.ok(written.ok, written.reason)
  const text = fs.readFileSync(path.join(unitsDir, "database", "mvcc.md"), "utf8")
  assert.ok(text.indexOf("README 原文") === -1, "教材原文不该塞进讲解段")
  assert.ok(text.indexOf(unitFile.EMPTY_EXPLAIN) !== -1, "讲解段应是占位符")
  assert.ok(/^status: verified$/m.test(text), "status 要写回 verified")
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
```

Expected: FAIL —— `unitFile.EMPTY_EXPLAIN` 为 `undefined`（当前 `unit-file.js` 没导出它），或断言「教材原文不该进讲解段」失败。

- [ ] **Step 3: 导出 `EMPTY_EXPLAIN`**

`core/supply/unit-file.js`，在 `FRONTMATTER_ORDER` 常量之后加：

```js
/** 单元文件里「讲解还没生成」的占位符。与 core/supply/plan.js 的同名常量保持一致。 */
const EMPTY_EXPLAIN = "（讲解正文还没生成）"
```

并把 `module.exports` 里加一行：

```js
  EMPTY_EXPLAIN: EMPTY_EXPLAIN,
```

- [ ] **Step 4: 改 `writeVerdict`**

`core/supply/verify.js`，把 `writeVerdict` 里：

```js
  const content = renderUnitFile(fields, {
    explain: String(unit.statement || ""),
    related: [],
  })
```

改成：

```js
  // 讲解段一律写占位符，**不写 unit.statement**。
  // unit.statement 是 README + NOTES 的**教材原文**（loader B 拼出来的），
  // 塞进「## 讲解」会让 plan 的 EMPTY_EXPLAIN 判定失效——
  // 缺口页再也不会报「缺讲解正文」，人也就不会去补真正的学习讲解。
  // 补讲解走 generate 的 write-explain 场景，它只替换「## 讲解」小节。
  const content = renderUnitFile(fields, {
    explain: EMPTY_EXPLAIN,
    related: [],
  })
```

并在该文件顶部的 `require("./unit-file.js")` 解构列表里补上 `EMPTY_EXPLAIN`
（该文件第 23–29 行已有解构导入，**不要另写一行 require**）：

```js
const {
  renderUnitFile,
  patchUnitFile,
  writeFileChecked,
  unitFilePath,
  stemOf,
  EMPTY_EXPLAIN,
} = require("./unit-file.js")
```

- [ ] **Step 5: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
node tests/supply-verify.test.js
node tests/supply-e2e.test.js
```

Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/supply/unit-file.js apps/study-hub/core/supply/verify.js apps/study-hub/tests/remediation-loader-status.test.js
git commit -m "fix(study-hub): verify 建单元文件时讲解写占位符，别拿教材原文冒充讲解"
git push origin main
```

---

### Task 4: 缺口扫描纳入「没有 loader C 单元文件」

**Files:**
- Modify: `projects/apps/study-hub/core/supply/plan.js:72-103`（`missingOf`）
- Test: `projects/apps/study-hub/tests/remediation-loader-status.test.js`（追加用例）

**Interfaces:**
- Consumes: `missingOf(unit, opts)`，`opts.learningRoot` / `opts.contentRoots`
- Produces: 卡类单元的缺口种类里，缺断言脚本时返回 `["asserts"]`；
  **讲解缺口判定新增**：单元文件里没有「## 讲解」正文时返回含 `"statement"`

- [ ] **Step 1: 写失败的测试**

在 `tests/remediation-loader-status.test.js` 追加：

```js
const plan = require("../core/supply/plan.js")

test("卡类单元：没有 loader C 单元文件时，讲解算缺口", function () {
  const root = tmpDir("study-hub-gap-")
  const unit = {
    id: "db:mvcc",
    track: "database",
    kind: "card",
    title: "MVCC",
    statement: "# MVCC\n\n教材原文\n",
    entry: { demo: "scaffold/grokking/mvcc/main.py", script: "units/database/mvcc.assert.py" },
  }
  const missing = plan.missingOf(unit, { learningRoot: root, contentRoots: [root] })
  assert.ok(missing.indexOf("asserts") !== -1, "缺断言脚本要算缺口：" + JSON.stringify(missing))
})

test("卡类单元：单元文件的讲解段是占位符时，讲解算缺口", function () {
  const root = tmpDir("study-hub-gap2-")
  const unitsDir = path.join(root, "units", "database")
  fs.mkdirSync(unitsDir, { recursive: true })
  fs.writeFileSync(
    path.join(unitsDir, "mvcc.md"),
    "---\nid: db:mvcc\ntrack: database\nkind: card\nstatus: verified\n---\n\n## 讲解\n\n（讲解正文还没生成）\n\n## 关联\n",
    "utf8"
  )
  const unit = {
    id: "db:mvcc",
    track: "database",
    kind: "card",
    title: "MVCC",
    statement: "（讲解正文还没生成）",
    entry: { demo: "scaffold/grokking/mvcc/main.py", script: "units/database/mvcc.assert.py" },
  }
  const missing = plan.missingOf(unit, { learningRoot: root, contentRoots: [root] })
  assert.ok(missing.indexOf("statement") !== -1, "占位符讲解要算缺口：" + JSON.stringify(missing))
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
```

Expected: 第二个用例 FAIL —— 讲解段是占位符时 `missing` 里没有 `"statement"`（当前 `missingOf` 只看 `unit.statement` 的空/占位，而 loader B 给的 `statement` 是教材原文，不为空）。

- [ ] **Step 3: 改 `missingOf`**

`core/supply/plan.js`，把卡类分支：

```js
  if (kind === "card") {
    if (!hasAssertScript(unit, o.learningRoot || null)) missing.push("asserts")
    if (statement === "" || statement === EMPTY_EXPLAIN) missing.push("statement")
    return missing
  }
```

改成：

```js
  if (kind === "card") {
    if (!hasAssertScript(unit, o.learningRoot || null)) missing.push("asserts")
    if (statement === "" || statement === EMPTY_EXPLAIN) missing.push("statement")
    // 单元文件里的「## 讲解」段是占位符 → 讲解还没生成，也算缺口。
    // loader B 给的 statement 是**教材原文**（README + NOTES），不是学习讲解，
    // 所以必须看单元文件那一段，不能只看 unit.statement。
    if (missing.indexOf("statement") === -1 && !hasRealExplain(unit, o.learningRoot || null)) {
      missing.push("statement")
    }
    return missing
  }
```

并在该文件里 `hasAssertScript` 之后加一个新函数：

```js
/**
 * 单元文件里的「## 讲解」段是不是真有正文。
 *
 * 读不到文件（还没生成单元文件）→ 返回 false（讲解算缺口）。
 * 读到占位符或空段 → false。
 * @param {object} unit
 * @param {string|null} learningRoot
 * @returns {boolean}
 */
function hasRealExplain(unit, learningRoot) {
  if (!learningRoot) return false
  const file = path.join(learningRoot, String(unit.track || ""), String(stemOf(unit)) + ".md")
  if (!fs.existsSync(file)) return false
  let text = ""
  try {
    text = fs.readFileSync(file, "utf8")
  } catch (e) {
    return false
  }
  const m = /##\s*讲解\s*\r?\n([\s\S]*?)(?:\r?\n##\s|$)/.exec(text)
  if (!m) return false
  const body = String(m[1] || "").trim()
  return body !== "" && body !== EMPTY_EXPLAIN
}
```

并在该文件顶部补 import（`plan.js` 第 227 行已有 `require("./unit-file.js")`，
但那是**函数内**的局部 require；本任务要的是文件顶部的模块级 import，所以新增一行）：

```js
const { stemOf } = require("./unit-file.js")
```

若 `stemOf` 已在文件里被定义或从别处导入，则**不加这行**，直接用现有来源。

- [ ] **Step 4: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-loader-status.test.js
node tests/supply-plan.test.js
```

Expected: 全部 PASS。

- [ ] **Step 5: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/supply/plan.js apps/study-hub/tests/remediation-loader-status.test.js
git commit -m "fix(study-hub): 缺口扫描认单元文件里的占位符讲解，别拿教材原文顶替"
git push origin main
```

---

### Task 5: 抽检只对已达标单元开放

**Files:**
- Modify: `projects/apps/study-hub/core/supply/review.js:56-76`（`pickReviewTargets`）
- Modify: `projects/apps/study-hub/core/supply/review.js:95-140`（`applyReview`）
- Test: `projects/apps/study-hub/tests/remediation-review.test.js`（新建）

**Interfaces:**
- Consumes: `pickReviewTargets(units, opts)`、`applyReview(opts)`
- Produces: `pickReviewTargets` 只返回 `status === "verified"` 且 `reviewed !== true` 的单元；
  `applyReview` 对非 `verified` 单元返回 `{ok: false, code: "invalid"}`

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-review.test.js`：

```js
"use strict"
/**
 * remediation-review.test.js —— 抽检语义闸门
 *
 * 补齐设计 §6.2：缺口是「还没补齐的东西」，抽检是「人看过之后给个结论」。
 * 两者不能混：没达标（draft / todo / rejected）的单元不配被抽检，
 * 更不该能被打回——那等于用人的一次点击覆盖执行器的裁决。
 */

const test = require("node:test")
const assert = require("node:assert/strict")
const fs = require("node:fs")
const path = require("node:path")

const review = require("../core/supply/review.js")
const { tmpDir } = require("./helpers/tmp.js")

function unit(id, status, reviewed) {
  return {
    id: id,
    track: "database",
    kind: "card",
    title: id,
    statement: "讲解",
    entry: { demo: "scaffold/grokking/x/main.py", script: "units/database/x.assert.py" },
    status: status,
    reviewed: reviewed === true,
  }
}

test("待抽检列表只收 verified 且没抽检过的", function () {
  const targets = review.pickReviewTargets(
    [
      unit("db:a", "verified", false),
      unit("db:b", "draft", false),
      unit("db:c", "todo", false),
      unit("db:d", "rejected", false),
      unit("db:e", "verified", true),
    ],
    {}
  )
  const ids = targets.map(function (t) { return t.id })
  assert.deepStrictEqual(ids, ["db:a"])
})

test("给未达标的单元写回抽检结论要被拒", function () {
  const root = tmpDir("study-hub-review-")
  const unitsDir = path.join(root, "units", "database")
  fs.mkdirSync(unitsDir, { recursive: true })
  fs.writeFileSync(
    path.join(unitsDir, "b.md"),
    "---\nid: db:b\ntrack: database\nkind: card\nstatus: draft\nreviewed: false\nreviewed_at: \"\"\n---\n\n## 讲解\n\n正文\n\n## 关联\n",
    "utf8"
  )
  const applied = review.applyReview({
    unit: unit("db:b", "draft", false),
    passed: true,
    unitsDir: path.join(root, "units"),
    repoRoot: root,
    stateFile: path.join(root, ".self-written.json"),
    today: "2026-11-22",
  })
  assert.strictEqual(applied.ok, false)
  assert.strictEqual(applied.code, "invalid")
  assert.ok(applied.reason.indexOf("还没通过校验") !== -1, applied.reason)
  // 文件一个字节都不该动
  const after = fs.readFileSync(path.join(unitsDir, "b.md"), "utf8")
  assert.ok(after.indexOf("reviewed: true") === -1, "被拒的抽检不该写文件")
})
```

**注意**：`applyReview` 内部会先查 git 状态（`writeFileChecked` → `checkWritable`），
所以临时目录**不是 git 仓**时它会返回 `code: "blocked"`（不是 `"invalid"`）。
因此本用例必须在 `applyReview` 的**状态检查之前**返回——即 Task 18 的 Step 4 把
「未达标」的判断放在 `unitsDir` 检查**之前**。

实测确认（2026-11-22）：当前 `applyReview` 对 `status: draft` 的单元，
在非 git 临时目录里返回 `{ok:false, code:"blocked"}`；
把状态检查前置后应返回 `{ok:false, code:"invalid"}`。
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-review.test.js
```

Expected: FAIL —— `pickReviewTargets` 返回了 `db:b` / `db:c` / `db:d`；`applyReview` 对 draft 单元返回 `ok: true`。

- [ ] **Step 3: 改 `pickReviewTargets`**

`core/supply/review.js`，把过滤条件：

```js
    .filter(function (unit) {
      if (only !== "" && String(unit.track || "") !== only) return false
      return unit.reviewed !== true
    })
```

改成：

```js
    .filter(function (unit) {
      if (only !== "" && String(unit.track || "") !== only) return false
      // 抽检只对**已达标**的单元开放：verified（执行器与变异测试都过了）且还没被人看过。
      // draft / todo / rejected 是「还没补齐」或「没过校验」，不是抽检对象。
      if (String(unit.status || "") !== "verified") return false
      return unit.reviewed !== true
    })
```

- [ ] **Step 4: 改 `applyReview`**

`core/supply/review.js`，在 `applyReview` 的 `fail` 函数之后、**`if (unitsDir === "" ...)` 之前**插入：

```js
  // 未达标的单元不配被抽检：人的一次点击不该覆盖执行器的裁决。
  // 这一条必须排在 unitsDir / repoRoot 检查**之前**——
  // 否则在非 git 的临时目录里，它会先被「读不到 git 状态」挡成 blocked，
  // 掩盖掉「这个单元本来就不该被抽检」这个真正的理由。
  if (String(unit.status || "") !== "verified") {
    return fail(
      "invalid",
      "这个单元还没通过校验（当前状态：" + String(unit.status || "todo") + "），不能抽检"
    )
  }
```

- [ ] **Step 5: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-review.test.js
node tests/supply-cli.test.js
node tests/supply-api.test.js
```

Expected: 全部 PASS。若 `supply-api.test.js` 因新规则失败，改的是**测试的期望**（不再期望缺口单元能抽检），不是删规则。

- [ ] **Step 6: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/supply/review.js apps/study-hub/tests/remediation-review.test.js
git commit -m "fix(study-hub): 抽检只对已达标单元开放，缺口不再挂着通过/打回"
git push origin main
```

---

### Task 6: 判题解释器可配置（服务端 + 离线 CLI）

**Files:**
- Modify: `projects/apps/study-hub/server/api-session.js:756-841`（`PUT /api/settings` 白名单，插入点在 829 行后）
- Modify: `projects/apps/study-hub/server/api-session.js:142-150`（`createEnvProbe` 缓存）
- Modify: `projects/apps/study-hub/server/api-session.js:131-134`（`probeEnv` 回值加 version/cmd）
- Modify: `projects/apps/study-hub/server/app.js:349-352`（单元索引的 pythonOverride + 重扫入口）
- Modify: **`projects/apps/study-hub/tools/supply.js:373-378` 与 `:588-594`**（离线 CLI 也读同一解释器配置 —— 差异清单 D-13b）
- Test: `projects/apps/study-hub/tests/remediation-settings-python.test.js`（新建）

**Interfaces:**
- Consumes: `detectPython(override)`（`judge/sandbox.js`）、`resolvePythonOverride(env)`（`core/paths.js`）
- Produces: `PUT /api/settings` 接受 `python_cmd` 字段；
  `GET /api/settings` 的 `env` 段里含 `python.cmd` / `python.args` / `numpy.version`；
  **离线 `tools/supply.js` 的 `verify` 与 `generate` 也遵守同一解释器优先级**

**⚠️ 差异清单 D-13b（评审发现，必须一并修）**：当前 `tools/supply.js` 的
`loadUnits({...})`（第 373–378 行）与 `verifyBatch({...})`（第 588–594 行）**都没传 `pythonOverride`**，
全文也没有 `resolvePythonOverride` / `STUDY_HUB_PYTHON`（实测 0 处）。
后果：`node tools/supply.js verify --track ai` 会走自动探测落到没有 numpy 的 `python`（3.11），
把 13 张 AI 卡全判成「环境缺失跳过」——**这正是设计 §5.1 描述的三处不一致的原症状**。
本任务把它一起修，否则 R2/R3 校验 AI 卡会全跳过。

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-settings-python.test.js`：

```js
"use strict"
/**
 * remediation-settings-python.test.js —— 判题解释器配置闸门
 *
 * 补齐设计 §5：本机装了多个 Python，默认探测到的那个可能没有 numpy
 * （实测：python 3.11 无 numpy，py -3 3.12 有 numpy 2.5.5）。
 * 解释器要能从设置页改，且环境自检、判题、loader 警告用同一个口径。
 */

const test = require("node:test")
const assert = require("node:assert/strict")
const http = require("node:http")

const sessionRoutes = require("../server/api-session.js")
const { detectPython, detectNumpy } = require("../judge/sandbox.js")

/**
 * 起一个只挂设置路由的假服务。
 * 路由的 handler 签名是 (req, res)，body 由 readJsonBody 从 req 流里读，
 * 所以这里要把请求体原样灌进 req。
 */
function startServer(ctx) {
  const routes = sessionRoutes.buildRoutes(ctx)
  const server = http.createServer(function (req, res) {
    const url = new URL(req.url, "http://127.0.0.1")
    const route = routes.find(function (r) {
      return r.method === req.method && r.pattern === url.pathname
    })
    if (!route) {
      res.writeHead(404)
      res.end("{}")
      return
    }
    route.handler(req, res).catch(function () {
      res.writeHead(500)
      res.end("{}")
    })
  })
  return new Promise(function (resolve) {
    server.listen(0, "127.0.0.1", function () {
      resolve({ server: server, base: "http://127.0.0.1:" + server.address().port })
    })
  })
}

function fakeStore(settings) {
  const map = Object.assign({}, settings || {})
  return {
    getSetting: function (k) { return map[k] === undefined ? null : map[k] },
    setSetting: function (k, v) { map[k] = String(v) },
    listUnits: function () { return [] },
    listSessions: function () { return [] },
    listQueue: function () { return [] },
    listReviewCards: function () { return [] },
    getSession: function () { return null },
    _map: map,
  }
}

/** 一个只够设置接口用的 ctx。 */
function fakeCtx(store, envProbe) {
  return {
    store: store,
    learning: { ok: false, root: null, reason: "没连上" },
    sendJson: function (res, code, body) {
      res.writeHead(code, { "content-type": "application/json" })
      res.end(JSON.stringify(body))
    },
    envProbe: envProbe || function () {
      return { python: { ok: true, detail: "python" }, numpy: { ok: false, detail: "缺 numpy" } }
    },
  }
}

test("PUT /api/settings 接受 python_cmd，并写进 settings", async function () {
  const store = fakeStore()
  const s = await startServer(fakeCtx(store))
  const res = await fetch(s.base + "/api/settings", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ python_cmd: "py -3" }),
  })
  assert.strictEqual(res.status, 200)
  assert.strictEqual(store._map["judge.python.cmd"], "py -3")
  s.server.close()
})

test("PUT /api/settings 拒绝空白的 python_cmd", async function () {
  const store = fakeStore()
  const s = await startServer(fakeCtx(store))
  const res = await fetch(s.base + "/api/settings", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ python_cmd: "   " }),
  })
  assert.strictEqual(res.status, 400)
  const body = await res.json()
  assert.ok(body.error.indexOf("解释器") !== -1, JSON.stringify(body))
  s.server.close()
})

test("PUT /api/settings 拒绝探测不到的解释器，不写入", async function () {
  const store = fakeStore()
  const s = await startServer(fakeCtx(store))
  const res = await fetch(s.base + "/api/settings", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ python_cmd: "definitely-not-a-python-xyz" }),
  })
  assert.strictEqual(res.status, 400)
  assert.strictEqual(store._map["judge.python.cmd"], undefined, "探测不到就不该写入")
  s.server.close()
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-settings-python.test.js
```

Expected: FAIL —— 第一个用例 `store._map["judge.python.cmd"]` 是 `undefined`（当前 `PUT /api/settings` 不认 `python_cmd`）。

- [ ] **Step 3: 在 `PUT /api/settings` 里加 `python_cmd`**

`server/api-session.js`，在 `if (body.count_trigger_k !== undefined ...)` 这段之后、`// 全部校验通过，才真正落盘` 之前插入：

```js
      if (body.python_cmd !== undefined && body.python_cmd !== null) {
        const raw = String(body.python_cmd).trim()
        if (raw === "") {
          ctx.sendJson(res, 400, { error: "判题解释器不能是空白；要恢复自动探测就清空它" })
          return
        }
        // 写入前先探一次：探测不到就拒绝，不把无效配置写进 settings。
        // 探测用 detectPython（走 judge/sandbox.js 的候选顺序）。
        const probe = detectPython(raw)
        if (!probe) {
          ctx.sendJson(res, 400, {
            error: "找不到这个 Python 解释器：" + raw + "（可用：python3 / python / py -3）",
          })
          return
        }
        writes.push([KEY_PYTHON, raw])
      }
```

并在该文件顶部的 import 处补上（若已有 `detectPython` 则跳过）：

```js
const { detectPython } = require("../judge/sandbox.js")
```

- [ ] **Step 4: 让环境探测不缓存旧结果**

`server/api-session.js`，把 `createEnvProbe` 改成**按解释器键缓存**，解释器一变就重探：

```js
function createEnvProbe(ctx) {
  let cachedKey = null
  let cached = null
  return function () {
    const key = String((ctx.store && ctx.store.getSetting(KEY_PYTHON)) || "")
    if (cached !== null && cachedKey === key) return cached
    cachedKey = key
    cached = probeEnv({ override: key || null })
    return cached
  }
}
```

- [ ] **Step 5: `GET /api/settings` 的 env 段带上解释器与 numpy 版本**

`server/api-session.js`，`probeEnv` 里的 numpy 探测改成取版本号：

```js
  let numpyOk = false
  let numpyDetail = ""
  let numpyVersion = ""
  try {
    const res = spawn(cmd, args.concat(["-c", "import numpy; print(numpy.__version__)"]), {
      encoding: "utf8",
      timeout: 5000,
    })
    numpyOk = !!(res && res.status === 0)
    numpyVersion = numpyOk ? String((res && res.stdout) || "").trim() : ""
    numpyDetail = numpyOk
      ? "numpy 可用（" + cmd + "，" + numpyVersion + "）"
      : "缺 numpy：" + String((res && res.stderr) || "导入失败").trim().split("\n")[0]
  } catch (err) {
    numpyOk = false
    numpyDetail = "numpy 探测失败：" + String(err && err.message ? err.message : err)
  }
  return {
    python: { ok: true, detail: cmd + (args.length ? " " + args.join(" ") : ""), cmd: cmd, args: args },
    numpy: { ok: numpyOk, detail: numpyDetail, version: numpyVersion },
  }
```

同时把该函数顶部的 JSDoc `@returns` 改成：

```js
 * @returns {{python: {ok: boolean, detail: string, cmd?: string, args?: string[]},
 *            numpy: {ok: boolean, detail: string, version?: string}}}
```

- [ ] **Step 6: 单元索引用同一个解释器口径**

`server/app.js`，`loadUnitsIndex` 函数里给 `loadUnits` 补上 `pythonOverride`：

```js
    return loadUnits({
      learningRoot: learning.root,
      localBank: options.localBank === null ? null : localBankDir(env, options.localBank),
      unitsDir: path.join(learning.root, "units"),
      grokkingDir: path.join(learning.root, "scaffold", "grokking"),
      // numpy 探测与判题用同一个解释器（settings 优先，其次 STUDY_HUB_PYTHON）
      pythonOverride: store.getSetting("judge.python.cmd") || resolvePythonOverride(env) || null,
    })
```

（`loadUnitsIndex` 当前签名里没有 `store`。若它拿不到 `store`，
就把 `pythonOverride` 作为**新参数**传进去：`loadUnitsIndex(learning, env, options, store)`，
并在调用处（第 395 行）改成 `loadUnitsIndex(learning, env, options, store)`。
该函数内的 `store` 引用要相应调整。）

同时 `server/app.js` 第 349 行的 `unitOpts.pythonOverride` 保持与上面同一口径
（当前已经是 `store.getSetting("judge.python.cmd") || resolvePythonOverride(env) || null`，**不用改**）。

- [ ] **Step 7: 改完解释器后重建单元索引**

在 `server/api-session.js` 的 `PUT /api/settings` handler 里，全部校验通过、`writes.forEach` 落盘之后、`ctx.sendJson` 之前插入：

```js
      // 解释器改了 → 单元索引要重扫：loader 的 numpy 警告依赖解释器口径。
      if (body.python_cmd !== undefined && body.python_cmd !== null && typeof ctx.reloadUnits === "function") {
        ctx.reloadUnits()
      }
```

在 `server/app.js` 里，给会话路由的 ctx 补上这个能力：

```js
  // 改了解释器就重扫一次单元索引：loader 的 numpy 警告跟着解释器走。
  // 不重扫的话，自检说「有 numpy」而列表还报「缺 numpy」——又是两套口径。
  function reloadUnits() {
    const fresh = loadUnitsIndex(learning, env, options, store)
    const freshUnits = fresh.units || []
    const freshById = fresh.byId || {}
    refreshUnitIndex(store, unitOpts, fresh)
    Object.keys(supplyUnitsById).forEach(function (key) {
      delete supplyUnitsById[key]
    })
    Object.assign(supplyUnitsById, freshById)
    supplyUnits.length = 0
    freshUnits.forEach(function (u) { supplyUnits.push(u) })
  }
```

并把它挂到会话路由的 ctx 上（`buildRoutes({...})` 的参数里加一行）：

```js
    reloadUnits: reloadUnits,
```

**注意**：`units` 变量（第 395 行 `const units = options.units || loadUnitsIndex(...)`）是 `const`，
不能重新赋值。若判题接口用的是这个 `units`，则 `reloadUnits` 里还要更新它——
但它是 `const` 绑定，改不了。**处理办法**：把第 395 行改成 `let`：

```js
  let units = options.units || loadUnitsIndex(learning, env, options, store)
```

然后在 `reloadUnits` 里补：

```js
    units = freshUnits
```

（`units` 被 `api-units.js` / `api-unit-run.js` / `api-session.js` 三处引用，
改 `let` 不影响它们——它们拿到的是同一个数组对象的引用，而 `reloadUnits` 用
`units.length = 0` + `push` **原地**改同一个数组，引用不变，行为一致。）

为稳妥，`reloadUnits` 里用原地修改而不是重新赋值：

```js
  function reloadUnits() {
    const fresh = loadUnitsIndex(learning, env, options, store)
    const freshUnits = fresh.units || []
    const freshById = fresh.byId || {}
    refreshUnitIndex(store, unitOpts, fresh)
    Object.keys(supplyUnitsById).forEach(function (key) { delete supplyUnitsById[key] })
    Object.assign(supplyUnitsById, freshById)
    supplyUnits.length = 0
    freshUnits.forEach(function (u) { supplyUnits.push(u) })
    units.length = 0
    freshUnits.forEach(function (u) { units.push(u) })
  }
```

这样 `units` 数组的**引用不变**、内容更新，所有持有引用的地方自动看到新数据。
（因此第 395 行的 `const units` **不用改**成 `let`。）

- [ ] **Step 8: 离线 CLI 也读同一解释器配置（差异清单 D-13b）**

`tools/supply.js` 改两处，让 `verify` 与 `generate` 都遵守
`settings.judge.python.cmd > STUDY_HUB_PYTHON > 自动探测` 这条优先级。

(a) 文件顶部 import 补上（`core/paths.js` 已在该文件被 require 过，把 `resolvePythonOverride`
加进已有的解构列表）：

```js
const { resolveLearningRoot, localBankDir, resolvePythonOverride } = require("../core/paths.js")
```

(b) `loadUnits({...})`（第 373–378 行）补 `pythonOverride`：

```js
    const loaded = loadUnits({
      learningRoot: learning.root,
      localBank: localBank,
      unitsDir: unitsDir,
      grokkingDir: grokkingDir,
      // 与判题、环境自检同一口径：settings 优先，其次 STUDY_HUB_PYTHON。
      // 不传的话 loader 的 numpy 警告会按自动探测算，跟判题结论矛盾。
      pythonOverride: (c.store && typeof c.store.getSetting === "function"
        ? c.store.getSetting("judge.python.cmd")
        : "") || resolvePythonOverride(env) || null,
    })
```

(c) `verifyBatch({...})`（第 588–594 行）补 `pythonOverride`：

```js
    const pythonOverride = (c.store && typeof c.store.getSetting === "function"
      ? c.store.getSetting("judge.python.cmd")
      : "") || resolvePythonOverride(env) || null
    const batch = await verifyBatch({
      units: targets,
      learningRoot: learning.root,
      unitsDir: unitsDir,
      repoRoot: learning.root,
      stateFile: stateFile,
      pythonOverride: pythonOverride,
    })
```

（`verifyBatch` 已经支持这个参数：`core/supply/verify.js:295` 的
`resolveToolchain({ pythonOverride: p.pythonOverride || null })` 就是读它。）

- [ ] **Step 9: 补一条 CLI 的验证用例**

在 `tests/remediation-settings-python.test.js` 末尾追加：

```js
const supplyCli = require("../tools/supply.js")

test("CLI 的 loadUnits 与 verifyBatch 都带上同一个 pythonOverride", async function () {
  // 只验参数是否被传下去，不真跑 python：注入一个假的 loadUnits 不方便，
  // 所以直接读源码里有没有这个键——这是防回归的最小闸门。
  const src = require("node:fs").readFileSync(
    require("node:path").join(__dirname, "..", "tools", "supply.js"),
    "utf8"
  )
  const loadUnitsAt = src.indexOf("const loaded = loadUnits({")
  assert.ok(loadUnitsAt !== -1, "找不到 loadUnits 调用")
  const loadUnitsBlock = src.slice(loadUnitsAt, loadUnitsAt + 600)
  assert.ok(loadUnitsBlock.indexOf("pythonOverride") !== -1, "loadUnits 没传 pythonOverride")

  const batchAt = src.indexOf("await verifyBatch({")
  assert.ok(batchAt !== -1, "找不到 verifyBatch 调用")
  const batchBlock = src.slice(batchAt, batchAt + 400)
  assert.ok(batchBlock.indexOf("pythonOverride") !== -1, "verifyBatch 没传 pythonOverride")
})
```

- [ ] **Step 10: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-settings-python.test.js
node tests/p1-api-session.test.js
node tests/api.test.js
node tests/supply-cli.test.js
```

Expected: 全部 PASS。

再手动确认 CLI 的解释器结论真的变了：

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
$env:STUDY_HUB_PYTHON='py -3'
node tools/supply.js verify --track ai 2>&1 | Select-String '环境缺失|已验证|跳过' | Select-Object -First 5
```

Expected: **不再**出现「环境缺失：本机没有装 numpy」；13 张卡要么「已验证」要么因断言脚本缺失而报别的理由。

- [ ] **Step 11: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/server/api-session.js apps/study-hub/server/app.js apps/study-hub/tools/supply.js apps/study-hub/tests/remediation-settings-python.test.js
git commit -m "feat(study-hub): 判题解释器可配置，环境自检、判题与离线 CLI 同一口径"
git push origin main
```

---

### Task 7: 深挖概念接线（路由 + 单元页入口）

**Files:**
- Modify: `projects/apps/study-hub/server/api-unit-run.js:244-281`（在 `/api/units/:id/ask` 之后加路由）
- Modify: `projects/apps/study-hub/web/pages/unit.js:429`（加按钮）
- Test: `projects/apps/study-hub/tests/remediation-deepen.test.js`（新建）

**Interfaces:**
- Consumes: `llm.deepen({unit, question, context, sessionId})`（`core/llm/service.js` 已有）
- Produces: `POST /api/units/:id/deepen`，入参 `{question}`，回 `{text, model}`；
  LLM 关闭时回 200 + 中文降级文案

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-deepen.test.js`：

```js
"use strict"
/**
 * remediation-deepen.test.js —— 深挖概念接线闸门
 *
 * 原设计 §7.1 场景 5「深挖概念」：core/llm/service.js 的 deepen 早就实现了，
 * 但 server/ 没有路由、web/ 没有入口——功能等于不存在。本任务补上。
 */

const test = require("node:test")
const assert = require("node:assert/strict")
const http = require("node:http")

const unitRoutes = require("../server/api-unit-run.js")

const UNIT = {
  id: "db:mvcc",
  track: "database",
  kind: "card",
  title: "MVCC",
  statement: "讲解",
  entry: { demo: "", reference: "", graded: "script", script: "" },
}

/**
 * 起一个只挂单元运行路由的假服务。
 * 路由的 handler 签名是 (req, res, params, query)，
 * body 从 req 上读（readJsonBody 读的是 req 的流），所以这里要先把 body 灌进 req。
 */
function startServer(ctx) {
  const routes = unitRoutes.buildUnitRunRoutes(ctx)
  const server = http.createServer(function (req, res) {
    const url = new URL(req.url, "http://127.0.0.1")
    const route = routes.find(function (r) {
      return r.method === req.method && r.pattern === url.pathname
    })
    if (!route) {
      res.writeHead(404, { "content-type": "application/json" })
      res.end(JSON.stringify({ error: "没这条路由" }))
      return
    }
    const chunks = []
    req.on("data", function (c) { chunks.push(c) })
    req.on("end", function () {
      const params = { id: decodeURIComponent(url.pathname.split("/")[3] || "") }
      route.handler(req, res, params, url.searchParams).catch(function () {
        res.writeHead(500, { "content-type": "application/json" })
        res.end(JSON.stringify({ error: "炸了" }))
      })
    })
  })
  return new Promise(function (resolve) {
    server.listen(0, "127.0.0.1", function () {
      resolve({ server: server, base: "http://127.0.0.1:" + server.address().port })
    })
  })
}

test("POST /api/units/:id/deepen 把问题交给 LLM 并回文本", async function () {
  let got = null
  const s = await startServer({
    units: [UNIT],
    unitsById: { "db:mvcc": UNIT },
    learning: { ok: false, root: null, reason: "" },
    llm: {
      deepen: async function (req) {
        got = req
        return { text: "再挖一层：版本链怎么长出来的", model: "fake-model" }
      },
    },
    sendJson: function (res, code, body) {
      res.writeHead(code, { "content-type": "application/json" })
      res.end(JSON.stringify(body))
    },
  })
  const res = await fetch(s.base + "/api/units/db:mvcc/deepen", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question: "版本链怎么长出来的" }),
  })
  assert.strictEqual(res.status, 200)
  const body = await res.json()
  assert.strictEqual(body.text, "再挖一层：版本链怎么长出来的")
  assert.strictEqual(body.model, "fake-model")
  assert.ok(got, "deepen 应当被调用")
  assert.strictEqual(got.unit.id, "db:mvcc")
  s.server.close()
})

test("LLM 没装配时深挖回 200 + 中文降级文案", async function () {
  const s = await startServer({
    units: [UNIT],
    unitsById: { "db:mvcc": UNIT },
    learning: { ok: false, root: null, reason: "" },
    llm: null,
    sendJson: function (res, code, body) {
      res.writeHead(code, { "content-type": "application/json" })
      res.end(JSON.stringify(body))
    },
  })
  const res = await fetch(s.base + "/api/units/db:mvcc/deepen", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question: "x" }),
  })
  assert.strictEqual(res.status, 200)
  const body = await res.json()
  assert.ok(body.text.indexOf("LLM") !== -1, JSON.stringify(body))
  s.server.close()
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-deepen.test.js
```

Expected: FAIL —— 404「没这条路由」。

- [ ] **Step 3: 加路由**

`server/api-unit-run.js`，在 `/api/units/:id/ask` 那条路由的 `})` 之后、`// 环境自检` 之前插入：

```js
  // 深挖概念（原设计 §7.1 场景 5）：在线场景，与「问 LLM」同族但不同路——
  // 讲解是从头讲一遍，深挖是针对用户追问再往下挖一层。
  routes.push({
    method: "POST",
    pattern: "/api/units/:id/deepen",
    handler: async function (req, res, params) {
      const unit = pickUnit(ctx, params.id)
      if (!unit) {
        notFound(res, params.id)
        return
      }
      const body = await readJsonBody(req)
      if (!llm || typeof llm.deepen !== "function") {
        // LLM 没装配不是错误：单元页照常能读能判，只是深挖不了（G10 同款降级）
        ctx.sendJson(res, 200, {
          text: "LLM 没装配，深挖不了。可以先自己读讲解、跑一遍断言。",
          model: "null",
        })
        return
      }
      try {
        const result = await llm.deepen({
          unit: unit,
          question: String((body && body.question) || ""),
          context: body && body.context ? body.context : undefined,
          sessionId: body && body.sessionId ? body.sessionId : undefined,
        })
        ctx.sendJson(res, 200, { text: result.text, model: result.model })
      } catch (err) {
        throw toHttpError(err)
      }
    },
  })
```

- [ ] **Step 4: 加单元页入口**

`web/pages/unit.js`，在 `onAsk` 函数之后（`onAsk` 结束于第 378 行）加：

```js
  /**
   * 深挖：针对单元追问一层。
   * LLM 关掉时接口也是 200 + 中文降级文案，这里照样显示。
   */
  async function onDeepen() {
    const unit = pageState.unit
    if (!unit) return
    const question = window.prompt("想深挖哪个点？留空就再挖一层")
    if (question === null) return
    try {
      const res = await A.postJson("/api/units/" + encodeURIComponent(unit.id) + "/deepen", {
        question: String(question || ""),
      })
      pageState.llmText = String((res && res.text) || "")
    } catch (err) {
      pageState.llmText = "深挖不了：" + String((err && err.message) || err)
    }
    paintResult(pageState.resultBox)
  }
```

并在按钮区（`el("button", { class: "btn", id: "unit-ask", text: "问 LLM", onclick: onAsk })` 之后）加：

```js
    el("button", { class: "btn", id: "unit-deepen", text: "深挖一层", onclick: onDeepen }),
```

**注意**：`pageState.llmText` + `paintResult(pageState.resultBox)` 是该文件里 `onAsk` 已在用的写法，
照抄即可，不要新造 `showResult` 之类的函数名。

- [ ] **Step 5: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-deepen.test.js
node tests/p2-unit-page.test.js
node tests/ui-hierarchy.test.js
```

Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/server/api-unit-run.js apps/study-hub/web/pages/unit.js apps/study-hub/tests/remediation-deepen.test.js
git commit -m "feat(study-hub): 深挖概念接上路由与单元页入口"
git push origin main
```

---

### Task 8: 供给页语义分离

**Files:**
- Modify: `projects/apps/study-hub/web/pages/supply.js:67-160`（hero / gap 面板）
- Modify: `projects/apps/study-hub/server/api-supply.js:34-52`（状态响应加待抽检列表）
- Test: `projects/apps/study-hub/tests/remediation-supply-web.test.js`（新建）

**Interfaces:**
- Consumes: `GET /api/supply/status` 的 `{tracks, gaps, warnings}`
- Produces: 状态响应新增 `reviewable` 数组（待抽检单元）；
  供给页缺口项**只读**（无「通过 / 打回」按钮），抽检入口独立成一块

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-supply-web.test.js`：

```js
"use strict"
/**
 * remediation-supply-web.test.js —— 供给页语义闸门
 *
 * 补齐设计 §6.2：缺口是「还没补齐的东西」，抽检是「人看过之后给个结论」。
 * 缺口项上不该再挂「通过 / 打回」按钮——那是把两个动作混成一件事。
 */

const test = require("node:test")
const assert = require("node:assert/strict")

const supply = require("../web/pages/supply.js")

function textOf(node) {
  if (node === null || node === undefined) return ""
  if (typeof node === "string") return node
  if (node.textContent !== undefined && node.textContent !== null) return String(node.textContent)
  if (node.children && node.children.length) {
    return node.children.map(textOf).join("\n")
  }
  return ""
}

test("缺口清单里没有「通过 / 打回」按钮", function () {
  const nodes = supply.buildSupplyView({
    tracks: [],
    gaps: [{ id: "db:mvcc", track: "database", title: "MVCC", missing: ["asserts"] }],
    warnings: [],
    reviewable: [],
  })
  const text = nodes.map(textOf).join("\n")
  assert.ok(text.indexOf("缺断言脚本") !== -1, "缺口要显示缺什么")
  const buttons = []
  nodes.forEach(function (n) {
    if (n.tagName === "BUTTON") buttons.push(String(n.textContent || ""))
  })
  buttons.forEach(function (label) {
    assert.ok(
      label !== "通过" && label !== "打回",
      "缺口清单里不该有抽检按钮，实际有：" + buttons.join("/")
    )
  })
})

test("待抽检清单里有「通过 / 打回」按钮", function () {
  const nodes = supply.buildSupplyView({
    tracks: [],
    gaps: [],
    warnings: [],
    reviewable: [{ id: "db:mvcc", track: "database", title: "MVCC", status: "verified" }],
  })
  const buttons = []
  nodes.forEach(function (n) {
    if (n.tagName === "BUTTON") buttons.push(String(n.textContent || ""))
  })
  assert.ok(buttons.indexOf("通过") !== -1, "待抽检要有通过按钮：" + buttons.join("/"))
  assert.ok(buttons.indexOf("打回") !== -1, "待抽检要有打回按钮：" + buttons.join("/"))
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-web.test.js
```

Expected: FAIL —— 缺口清单里现在有「通过」「打回」按钮；且 `buildSupplyView` 不认 `reviewable`。

- [ ] **Step 3: 服务端给出待抽检列表**

`server/api-supply.js`，`GET /api/supply/status` 的 handler（当前第 48–52 行的 `c.sendJson`）改成：

```js
        // 待抽检：只有已达标（verified）且还没被人看过的单元才配被抽检。
        // 缺口（draft / todo / rejected）是「还没补齐」，不在这里出现。
        const allUnits = Array.isArray(c.units) ? c.units : []
        const reviewable = allUnits
          .filter(function (unit) {
            return String(unit.status || "") === "verified" && unit.reviewed !== true
          })
          .slice(0, 50)
          .map(function (unit) {
            return {
              id: String(unit.id || ""),
              track: String(unit.track || ""),
              kind: String(unit.kind || ""),
              title: String(unit.title || ""),
              status: String(unit.status || ""),
            }
          })
        c.sendJson(res, 200, {
          tracks: result.tracks,
          gaps: result.gaps,
          reviewable: reviewable,
          warnings: result.warnings,
        })
```

同时把第 38 行那个「没连上 learning 仓」的降级响应也补上 `reviewable` 字段（保持响应形状一致）：

```js
          c.sendJson(res, 200, { tracks: [], gaps: [], reviewable: [], warnings: [LOCAL_WARNING] })
```

- [ ] **Step 4: 前端拆分缺口与抽检**

`web/pages/supply.js`：

(a) `gapPanel` 改成只读——把

```js
        el("div", { class: "row" }, [
          statusPill("缺：" + kinds.join("、")),
          el("button", { class: "primary", text: "通过", onclick: function () { onReview(gap, true) } }),
          el("button", { text: "打回", onclick: function () { onReview(gap, false) } }),
        ]),
```

改成

```js
        el("div", { class: "row" }, [
          statusPill("缺：" + kinds.join("、")),
          el("span", {
            class: "faint",
            text: "补缺口跑命令行：node tools/supply.js generate --track " + String(gap.track || ""),
          }),
        ]),
```

`gapPanel` 的第二个参数 `onReview` 此时不再使用——**保留签名**（调用处不用改），
或在改完后把签名改成 `function gapPanel(gaps) {` 并把调用处 `gapPanel(gaps, onReview)` 改成 `gapPanel(gaps)`。
二选一，不要留一个不用的形参。

(b) 新增一个待抽检面板：

```js
  /** 待抽检清单：只有已达标（verified）且没被人看过的单元才配被抽检。 */
  function reviewPanel(reviewable, onReview) {
    const children = []
    if (!reviewable || reviewable.length === 0) {
      children.push(el("p", { class: "muted", text: "没有待抽检的单元（都被人看过了，或者还没通过校验）。" }))
      return UI ? UI.panel({ title: "待抽检", children: children }) : el("section", { class: "panel" }, children)
    }
    reviewable.forEach(function (item) {
      children.push(el("div", { class: "kv" }, [
        el("div", {}, [
          document.createTextNode(String(item.id || "") + "　"),
          el("span", { text: String(item.title || "") }),
        ]),
        el("div", { class: "row" }, [
          statusPill("已验证"),
          el("button", { class: "primary", text: "通过", onclick: function () { onReview(item, true) } }),
          el("button", { text: "打回", onclick: function () { onReview(item, false) } }),
        ]),
      ]))
    })
    return UI ? UI.panel({ title: "待抽检", children: children }) : el("section", { class: "panel" }, children)
  }
```

(c) `heroPanel` 改成三参并把按钮指向待抽检清单：
把 `function heroPanel(gaps, onReview) {` 改成 `function heroPanel(gaps, onReview, reviewable) {`，
并把那段「抽检第一个缺口 / 打回第一个缺口」按钮换成：

```js
    if (Array.isArray(reviewable) && reviewable.length > 0) {
      children.push(el("div", { class: "row" }, [
        el("button", { class: "primary", text: "抽检第一个", onclick: function () { onReview(reviewable[0], true) } }),
        el("button", { text: "打回第一个", onclick: function () { onReview(reviewable[0], false) } }),
      ]))
    }
```

（缺口本身**不再有**抽检按钮——缺口是「还没补齐」，不是「人看过给结论」。）

(d) `buildSupplyView` 里读 `reviewable` 并挂上待抽检面板：

在 `const warnings = ...` 那行之后加：

```js
    const reviewable = Array.isArray(data.reviewable) ? data.reviewable : []
```

把 `nodes.push(heroPanel(gaps, onReview))` 改成：

```js
    nodes.push(heroPanel(gaps, onReview, reviewable))
```

在 `nodes.push(gapPanel(gaps, onReview))` 之后加：

```js
    nodes.push(reviewPanel(reviewable, onReview))
```

- [ ] **Step 5: 改既有供给页测试的期望**

`tests/supply-web.test.js` 里有两个用例的期望已经过时（它们假设缺口项上挂着抽检按钮）：

(a) 把「供给页：缺口清单里每个单元都有「通过」和「打回」两个入口」改成：

```js
test("供给页：缺口清单里没有抽检按钮（缺口是只读的）", async function () {
  const posted = []
  stubFetch({ "/api/supply/status": STATUS }, posted)
  const view = mountView()
  await PAGES.supply.render(view)
  const buttons = findAllByTag(view, "button")
  const labels = buttons.map(function (b) { return b.textContent })
  assert.ok(labels.indexOf("通过") === -1, "缺口清单里不该有通过按钮：" + labels.join("/"))
  assert.ok(labels.indexOf("打回") === -1, "缺口清单里不该有打回按钮：" + labels.join("/"))
})
```

(b) 把「供给页：点「通过」会 POST 到 /api/supply/review/:id」改成针对**待抽检清单**：

```js
test("供给页：点待抽检里的「通过」会 POST 到 /api/supply/review/:id", async function () {
  const posted = []
  const withReviewable = Object.assign({}, STATUS, {
    reviewable: [{ id: "db:demo", track: "database", kind: "card", title: "演示卡", status: "verified" }],
  })
  stubFetch({ "/api/supply/status": withReviewable }, posted)
  const view = mountView()
  await PAGES.supply.render(view)
  const buttons = findAllByTag(view, "button")
  const pass = buttons.find(function (b) { return b.textContent === "通过" })
  assert.ok(pass, "待抽检清单里要有通过按钮")
  pass.dispatch("click")
  await new Promise(function (resolve) { setTimeout(resolve, 0) })
  assert.strictEqual(posted.length, 1, "要点一次就发一次")
  assert.ok(posted[0].url.indexOf("/api/supply/review/db%3Ademo") !== -1, posted[0].url)
  assert.ok(posted[0].body.indexOf('"passed":true') !== -1, posted[0].body)
})
```

(c) 给 `STATUS` 加一行 `reviewable: []`：

```js
const STATUS = {
  tracks: [
    { track: "algorithm", total: 0, todo: 0, draft: 0, verified: 0, rejected: 0, reviewed: 0 },
    { track: "database", total: 1, todo: 0, draft: 1, verified: 0, rejected: 0, reviewed: 0 },
    { track: "ai", total: 0, todo: 0, draft: 0, verified: 0, rejected: 0, reviewed: 0 },
  ],
  gaps: [
    { id: "db:demo", track: "database", kind: "card", title: "演示卡", missing: ["asserts", "statement"] },
  ],
  reviewable: [],
  warnings: [],
}
```

- [ ] **Step 6: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-web.test.js
node tests/supply-web.test.js
node tests/supply-api.test.js
```

Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/web/pages/supply.js apps/study-hub/server/api-supply.js apps/study-hub/tests/remediation-supply-web.test.js
git commit -m "fix(study-hub): 供给页把缺口与抽检分开，缺口不再挂着通过/打回"
git push origin main
```

---

### Task 9: 标题与品牌文案

**Files:**
- Modify: `projects/apps/study-hub/web/index.html:6,12`
- Test: `projects/apps/study-hub/tests/remediation-brand.test.js`（新建）

**Interfaces:**
- Consumes: 无
- Produces: `web/index.html` 的 `<title>` 与页头 `<h1>` 用 study-hub 口径的中文名

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-brand.test.js`：

```js
"use strict"
/**
 * remediation-brand.test.js —— 品牌文案闸门
 *
 * 补齐设计 §6.2：应用已从「算法能力计划」改名 study-hub，
 * 浏览器标签页与页头还挂着旧名。
 */

const test = require("node:test")
const assert = require("node:assert/strict")
const fs = require("node:fs")
const path = require("node:path")

const WEB = path.resolve(__dirname, "..", "web")

test("index.html 的标题是学习中枢，不是「算法能力计划」", function () {
  const html = fs.readFileSync(path.join(WEB, "index.html"), "utf8")
  assert.ok(html.indexOf("算法能力计划") === -1, "还留着旧标题")
  assert.ok(html.indexOf("学习中枢") !== -1, "标题该用「学习中枢」")
})

test("index.html 的页头副标提到三轨", function () {
  const html = fs.readFileSync(path.join(WEB, "index.html"), "utf8")
  assert.ok(html.indexOf("算法") !== -1, "副标要提算法")
  assert.ok(html.indexOf("数据库") !== -1, "副标要提数据库")
  assert.ok(html.indexOf("AI") !== -1, "副标要提 AI")
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-brand.test.js
```

Expected: FAIL —— `index.html` 里还有「算法能力计划」。

- [ ] **Step 3: 改 `web/index.html`**

把：

```html
  <title>算法能力计划</title>
```

改成：

```html
  <title>学习中枢 · study-hub</title>
```

把：

```html
    <h1>算法能力计划<span>本地题库 · 判题 · 间隔复习 · 能力诊断</span></h1>
```

改成：

```html
    <h1>学习中枢<span>算法 · 数据库 · AI 三轨 · 判题 · 间隔复习 · 能力诊断</span></h1>
```

- [ ] **Step 4: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-brand.test.js
node tests/smoke.test.js
```

Expected: 全部 PASS。

- [ ] **Step 5: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/web/index.html apps/study-hub/tests/remediation-brand.test.js
git commit -m "fix(study-hub): 标题与页头改成学习中枢口径"
git push origin main
```

---

### Task 10: 设置页的解释器输入框

**Files:**
- Modify: `projects/apps/study-hub/web/pages/settings.js:120-135`（`envRows`）、`:300-360`（环境自检卡）
- Test: `projects/apps/study-hub/tests/remediation-settings-python.test.js`（追加前端用例）

**Interfaces:**
- Consumes: `GET /api/settings` 的 `env.python.cmd` / `env.numpy.version`；
  `PUT /api/settings` 的 `python_cmd`
- Produces: `buildPayload` 支持 `python_cmd`；设置页有解释器输入框并显示当前生效解释器

- [ ] **Step 1: 写失败的测试**

在 `tests/remediation-settings-python.test.js` 追加：

```js
const settingsPage = require("../web/pages/settings.js")

test("buildPayload 把 python_cmd 一起发出去", function () {
  const payload = settingsPage.buildPayload({
    session_count: 3,
    count_trigger_k: 5,
    weights: {},
    enabled: {},
    python_cmd: "py -3",
  })
  assert.strictEqual(payload.python_cmd, "py -3")
})

test("解释器为空白时校验拦下", function () {
  const errors = settingsPage.validatePayload({
    session_count: 3,
    count_trigger_k: 5,
    track_weights: {},
    track_enabled: {},
    python_cmd: "   ",
  })
  assert.ok(errors.length > 0, "空白解释器要拦")
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-settings-python.test.js
```

Expected: FAIL —— `buildPayload` 里没有 `python_cmd`；`validatePayload` 不报空白解释器。

- [ ] **Step 3: 改 `buildPayload`**

`web/pages/settings.js`，把 `buildPayload` 的返回改成：

```js
    const payload = {
      session_count: Number(f.session_count),
      count_trigger_k: Number(f.count_trigger_k),
      track_weights: weights,
      track_enabled: enabled,
    }
    if (f.python_cmd !== undefined && f.python_cmd !== null) {
      payload.python_cmd = String(f.python_cmd).trim()
    }
    return payload
```

- [ ] **Step 4: 改 `validatePayload`**

在 `validatePayload` 里，权重校验之后、返回之前插入：

```js
    if (p.python_cmd !== undefined && p.python_cmd !== null) {
      const cmd = String(p.python_cmd).trim()
      if (cmd === "") {
        errors.push("判题解释器不能是空白")
      } else if (!/^[A-Za-z0-9_\\:.\-\\/ ]+$/.test(cmd)) {
        errors.push("判题解释器只能是解释器命令，不许带参数或路径分隔之外的字符")
      }
    }
```

- [ ] **Step 5: 环境自检卡加解释器输入框**

`web/pages/settings.js`，在 `envRows` 之后加一个渲染函数：

```js
  /**
   * 判题解释器输入框。
   * 本机可能装了多个 Python（实测：默认探测到的没有 numpy，另一个有），
   * 所以让用户能改，并且把当前生效的解释器与 numpy 版本显示出来。
   * @param {object} env
   * @param {object} fields 表单状态
   * @returns {HTMLElement}
   */
  function pythonRow(env, fields) {
    const e = env || {}
    const detail = e.python || {}
    const input = el("input", {
      type: "text",
      "data-field": "python_cmd",
      class: "setting-input",
      placeholder: "留空 = 自动探测（python3 / python / py -3）",
    })
    input.value = String(fields.python_cmd || "")
    input.addEventListener("change", function () {
      fields.python_cmd = String(input.value).trim()
    })
    return el("div", { class: "setting-row" }, [
      el("span", { class: "setting-name", text: "判题解释器" }),
      input,
      el("span", {
        class: "setting-hint",
        text: detail.detail
          ? "当前：" + detail.detail + (e.numpy && e.numpy.ok ? "（numpy " + String(e.numpy.version || "") + "）" : "（无 numpy）")
          : "当前：自动探测",
      }),
    ])
  }
```

在 `render` 里，`const fields = { ... }`（当前第 193–198 行）的对象里加上 `python_cmd` 一项：

```js
    const fields = {
      session_count: Number(sessionCfg.default_count || 3),
      count_trigger_k: Number(reviewCfg.count_trigger_k || 5),
      weights: {},
      enabled: {},
      python_cmd: String((cfg.env && cfg.env.python && cfg.env.python.cmd) || ""),
    }
```

（`env.python.cmd` 是 Task 6 Step 5 加的字段；若接口形状不同，
就改用 `cfg.env.python.detail` 的第一段作为初值。）

并在「环境自检」静默卡里，把 `envChildren.push(...)` 之前加上：

```js
    envChildren.push(pythonRow(cfg.env, fields))
```

- [ ] **Step 6: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-settings-python.test.js
node tests/p1-web-settings.test.js
node tests/ui-hierarchy.test.js
```

Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/web/pages/settings.js apps/study-hub/tests/remediation-settings-python.test.js
git commit -m "feat(study-hub): 设置页加判题解释器输入框"
git push origin main
```

---

### Task 11: `.env.example` 与密钥配置说明

**Files:**
- Create: `projects/apps/study-hub/.env.example`
- Modify: `projects/apps/study-hub/README.md`（环境变量段）

**Interfaces:**
- Consumes: `core/llm/client.js` 认的环境变量名
- Produces: 一份**不含真实值**的模板文件；README 指向它

- [ ] **Step 1: 写 `.env.example`**

创建 `projects/apps/study-hub/.env.example`：

```bash
# study-hub 的本地配置模板。复制成 .env 后填自己的值。
# .env 已被 projects/.gitignore 忽略，不会进 git。
# 已存在的环境变量优先——.env 不覆盖命令行传的值。

# ── 学习仓与题库 ─────────────────────────────────
# learning 仓根目录。不设就是「纯本地模式」（只有 SQLite，不与 learning 仓同步）
STUDY_HUB_LEARNING_ROOT=C:/code/learning

# 判题用的 Python 解释器。本机装了多个、numpy 只装在其中一个时用它指定。
# 本机实测：默认探测到的 python(3.11) 没有 numpy；py -3(3.12) 有 numpy 2.5.5。
STUDY_HUB_PYTHON=py -3

# 服务端口
PORT=5173

# ── LLM（二选一即可；不配就只用离线功能）────────────
# 方舟
ARK_API_KEY=
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# Anthropic
ANTHROPIC_API_KEY=

# LLM 总开关：0 / false / off = 关。不设 = 按密钥自动判断
STUDY_HUB_LLM_ENABLED=
# provider：ark / anthropic；不设 = 按密钥推断
STUDY_HUB_LLM_PROVIDER=
# 模型名要写完整版本化 ID
STUDY_HUB_LLM_MODEL=

# 成本护栏
STUDY_HUB_LLM_SESSION_LIMIT=20
STUDY_HUB_LLM_DAILY_LIMIT=100
```

- [ ] **Step 2: 确认 `.env` 仍被忽略**

Run:

```powershell
cd C:\code\projects
git check-ignore -v apps/study-hub/.env
```

Expected: 打印 `.gitignore` 里匹配 `.env` 的那一行（说明 `.env` 被忽略，`.env.example` 不会被忽略）。

再确认模板文件**能**进 git：

```powershell
cd C:\code\projects
git status --porcelain apps/study-hub/.env.example
```

Expected: 打印 `?? apps/study-hub/.env.example`（未被忽略）。

- [ ] **Step 3: README 加一段**

在 `projects/apps/study-hub/README.md` 的「## 环境变量」小节**之前**插入：

```markdown
## 配置：`.env` 与 `.env.example`

密钥与本机路径都写在 `.env` 里。仓库里有一份**不含真实值**的模板
`apps/study-hub/.env.example`，复制成 `.env` 再填：

```bash
cd projects/apps/study-hub
cp .env.example .env
```

- `.env` 已被 `projects/.gitignore` 忽略，不会进 git。
- **已存在的环境变量优先**：`.env` 不覆盖命令行传的值。
- 密钥只从环境变量 / `.env` 读，**不写进 settings 表、不进代码、不进生成产物**。
- 本机装了多个 Python 时用 `STUDY_HUB_PYTHON` 指定（实测：`python` 是 3.11 没有 numpy，
  `py -3` 是 3.12 有 numpy 2.5.5——AI 轨能不能跑取决于这个）。

```

- [ ] **Step 4: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/.env.example apps/study-hub/README.md
git commit -m "docs(study-hub): 补 .env.example 模板与配置说明"
git push origin main
```

---

### Task 12: 全量回归与 R1 验收记录

**Files:**
- Create: `C:\code\docs\superpowers\specs\2026-11-22-study-hub-r1-acceptance.md`

**Interfaces:**
- Consumes: 全部前置任务的产出
- Produces: 一份 R1 验收记录（真实命令输出，不靠描述）

- [ ] **Step 1: 跑全量测试**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/run-all.js 2>&1 | Select-Object -Last 3
```

Expected: `111 / 111 套件通过` 之后的套件数**不少于** 111（本计划新增 6 个测试文件），且 `fail` 数为 0。

若某个既有套件因新规则失败：**先判断是规则错了还是测试期望过时**。
规则错了 → 改规则并补新测试；测试期望过时 → 改测试的期望，并在验收记录里写明改了什么、为什么。

- [ ] **Step 2: 起服务做三轨冒烟**

Run（后台）:

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
$env:STUDY_HUB_PYTHON='py -3'
$env:PORT='5199'
node server/main.js
```

另开一个 shell 逐个打：

```powershell
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/health' -UseBasicParsing; $r.StatusCode
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/supply/status' -UseBasicParsing; ($r.Content | ConvertFrom-Json).tracks | Format-Table -AutoSize
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/env' -UseBasicParsing; $r.Content
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/settings' -UseBasicParsing; ($r.Content | ConvertFrom-Json).env | Format-List
```

Expected:
- `/api/health` → 200
- `/api/supply/status` 的 database 轨 `verified` 数**下降**（原 16 → 现在 0~2，取决于 learning 仓里有没有单元文件）；
  `gaps` 里 database 轨的缺口条数 = 16（每张卡都缺讲解或断言）
- `/api/env` 的 `numpy.available` 为 `true`（因为设了 `STUDY_HUB_PYTHON=py -3`）
- `/api/settings` 的 `env.python.cmd` 为 `py`

- [ ] **Step 3: 验证解释器切换真的生效**

```powershell
$body = @{ python_cmd = 'py -3' } | ConvertTo-Json
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/settings' -Method PUT -ContentType 'application/json' -Body $body -UseBasicParsing
($r.Content | ConvertFrom-Json).env | Format-List
```

Expected: `numpy.ok` 为 `True`、`numpy.detail` 含版本号。

再切回自动探测：

```powershell
$body = @{ python_cmd = 'python' } | ConvertTo-Json
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/settings' -Method PUT -ContentType 'application/json' -Body $body -UseBasicParsing
($r.Content | ConvertFrom-Json).env | Format-List
```

Expected: `numpy.ok` 为 `False`——**同一台机器、只改解释器，结论就翻转**，说明口径统一了。

- [ ] **Step 4: 验证深挖接口**

```powershell
$body = @{ question = '版本链是怎么长出来的' } | ConvertTo-Json
try {
  $r = Invoke-WebRequest 'http://127.0.0.1:5199/api/units/db:mvcc/deepen' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
  $r.StatusCode
} catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: **200**（LLM 没配时是降级文案，不是 404、不是 500）。

- [ ] **Step 5: 停服务并确认 learning 仓没被写脏**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: **空输出**。R1 只改规则，不产生学习内容。

（若不为空，说明某个冒烟命令写了东西——查清来源并清掉，不能带着脏工作区往下走。）

- [ ] **Step 6: 写验收记录**

创建 `C:\code\docs\superpowers\specs\2026-11-22-study-hub-r1-acceptance.md`，内容用**真实命令输出**填：

```markdown
# study-hub R1 验收记录（规则与工具修复）

> 日期：2026-11-22
> 范围：Task 1–12
> 设计：[2026-11-22-study-hub-remediation-design.md](2026-11-22-study-hub-remediation-design.md)

## 测试

- 命令：`node tests/run-all.js`
- 结果：<贴真实的「N / N 套件通过」那一行>
- 新增测试文件：remediation-loader-status / remediation-review / remediation-settings-python /
  remediation-deepen / remediation-supply-web / remediation-brand

## 三轨冒烟

| 命令 | 期望 | 实际 |
|---|---|---|
| `GET /api/health` | 200 | <填> |
| `GET /api/supply/status` | database verified 数下降 | <填实际数字> |
| `GET /api/env`（STUDY_HUB_PYTHON=py -3） | numpy 可用 | <填> |
| `PUT /api/settings {python_cmd}` | numpy 状态随解释器翻转 | <填> |
| `POST /api/units/db:mvcc/deepen` | 200 | <填> |

## 状态门槛的实际影响

| 轨 | 改门前 verified | 改门后 verified |
|---|---|---|
| database | 16 | <填> |
| ai | 13 | <填> |
| algorithm | 53 | <填> |

## 已知未做

- R2/R3 的内容补齐（等 LLM 密钥）
- R2/R3 完成后回来把本记录里的「状态门槛的实际影响」一节更新成最终数字
```

- [ ] **Step 7: 提交**

```bash
cd C:\code
git add docs/superpowers/specs/2026-11-22-study-hub-r1-acceptance.md
git commit -m "docs(验收): 记录 study-hub R1 实测结果"
git push origin main
```

---

## 计划自检

| 检查项 | 结果 |
|---|---|
| 规格覆盖 | 设计 §3.2→Task 2/3/4；§3.3→Task 3/4；§3.4→R3 计划（本计划不涉及）；§4.4→Task 3；§5→Task 6/10；§6.1→Task 1；§6.2→Task 7/8/9；§7.1→Task 11；§8 R0/R1→Task 1/12 |
| 占位符扫描 | 无 TBD / TODO / 「类似 Task N」；每个代码步骤都给了完整代码 |
| 类型一致 | `EMPTY_EXPLAIN`（unit-file.js 导出，plan.js 与 verify.js 共用）；`reviewable`（api-supply 出、supply.js 消费）；`python_cmd`（api-session 收、settings.js 发）；`judge.python.cmd`（settings 键名，全计划一致） |
| 关键修正 | 设计 §3.2 变更二（脚本存在但未校验也不给 verified）已落到 Task 2 的测试里 |
