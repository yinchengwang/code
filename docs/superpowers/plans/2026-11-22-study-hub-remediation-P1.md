# study-hub 补齐与收尾 — R2/R3 实施计划（内容补齐与验收）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 DB/AI 的 29 张卡补齐讲解与断言脚本，把算法轨 687 道空骨架题补齐四件套，
全部经过真实执行校验与分层人工抽检。

**Architecture:** 内容由既有供给流水线产出（`core/supply/` + `core/llm/`），本计划**不新建生成逻辑**——
只补三处流水线缺陷（讲��重写、抽检分层、脚本内容不足），然后按批驱动既有命令。

**Tech Stack:** Node ≥ 24、零 npm 依赖、Python 3（卡片断言）、g++ 14.2.0（算法题编译）。

## Global Constraints

- 前置：**必须先完成 [R0/R1 计划](2026-11-22-study-hub-remediation-P0.md)**。门槛与口径没修之前，
  生成出来的内容**不可信**（`verified` 的含义会不对）。
- 应用目录：`C:\code\projects\apps\study-hub`；学习仓：`C:\code\learning`
- 设计文档：`C:\code\docs\superpowers\specs\2026-11-22-study-hub-remediation-design.md`
- **LLM 密钥由用户在执行 R2/R3 前提供**：只放 `apps/study-hub/.env`（已被 gitignore）或环境变量。
  **密钥不出现在任何命令参数、文件内容、日志、提交里。**
- **绝不自动 `git add` / `git commit`** learning 仓的内容产物；只打印 diff，提交由人决定。
- 每批生成后跑真实校验；**只有校验通过 + 抽检完成的单元才报告为「已补齐」**。
- 单批次调用上限 `supply.batch.session_limit`（默认 800）、当日上限 `supply.batch.daily_limit`（默认 800）、
  最小间隔 `supply.batch.rate_ms`（默认 1200ms）、单题最多 `1 + max_retries`（默认 3）次尝试。
- **算法轨与卡内容共用同一 LLM 配额**：两轨的批次必须**串行**跑，不要并行。

---

## 文件结构（本次会改动的文件）

| 文件 | 职责 | 动作 |
|---|---|---|
| `core/supply/review.js` | 抽检写回 + 目标挑选 | 改：新增分层抽样 |
| `core/supply/algorithm-cli.js` | 算法轨专线 CLI | 改：`review` 子命令支持分层抽样 |
| `core/llm/prompts.js` | 按轨提示词模板表 | 改：断言脚本模板要求覆盖关键结论 |
| `learning/units/database/*.assert.py` | 卡片断言脚本 | 新增/重写（内容产物） |
| `learning/units/database/*.md` | 卡片单元文件 | 新增（内容产物） |
| `learning/units/ai/*.assert.py` | AI 卡断言脚本 | 新增（内容产物） |
| `learning/units/ai/*.md` | AI 卡单元文件 | 新增（内容产物） |
| `learning/units/algorithm/*` | 算法题四件套 | 新增（内容产物） |
| `docs/superpowers/specs/2026-11-22-study-hub-r3-acceptance.md` | R3 验收记录 | 新建 |

---

### Task 13: 断言脚本模板要求「覆盖关键结论」

**Files:**
- Modify: `projects/apps/study-hub/core/llm/prompts.js:622-740`（`generate-assert` 的三个轨模板）
- Test: `projects/apps/study-hub/tests/remediation-supply-prompt.test.js`（新建）

**Interfaces:**
- Consumes: `buildSupplyPrompt("generate-assert", track, context)`
- Produces: 三个轨的 `generate-assert` 模板都要求：**断言脚本必须覆盖 demo 的每个主要结论**，
  且脚本要**检查具体数值/字符串**，不能只检查「跑完了」

**为什么必须先修**：`mvcc` 与 `index_design` 的脚本失败原因实测为**断言覆盖不足**——
`mvcc` 只断言了「快照隔离」那句，变异后 demo 走到 `else` 分支输出「读到了新数据」，
脚本照样 `exit 0`；`index_design` 只断言了「最左前缀原则」那几行，
而变异器改坏的是 `explain()` 的 `return`（第 107 行），脚本根本没看 a/b/c/d 四条 EXPLAIN 结果。
模板不修，新生成的脚本会重犯同一个错。

- [ ] **Step 1: 写失败的测试**

新建 `projects/apps/study-hub/tests/remediation-supply-prompt.test.js`：

```js
"use strict"
/**
 * remediation-supply-prompt.test.js —— 断言脚本提示词闸门
 *
 * 实测教训：mvcc / index_design 的断言脚本只覆盖 demo 的一部分结论，
 * 变异测试因此抓不住被改坏的逻辑。模板必须明确要求「覆盖每个主要结论、
 * 检查具体内容」，否则新生成的脚本会重犯同一个错。
 */

const test = require("node:test")
const assert = require("node:assert/strict")

const prompts = require("../core/llm/prompts.js")

const TRACKS = ["algorithm", "database", "ai"]

test("三个轨的 generate-assert 模板都要求覆盖主要结论", function () {
  TRACKS.forEach(function (track) {
    const built = prompts.buildSupplyPrompt("generate-assert", track, {
      title: "t",
      statement: "s",
      demo: "print(1)\n",
      readme: "",
      notes: "",
      question: "",
      topics: "x",
      difficulty: "medium",
    })
    const text = String(built.user || "")
    assert.ok(text.indexOf("覆盖") !== -1, track + " 模板要提「覆盖」")
    assert.ok(text.indexOf("每个") !== -1, track + " 模板要提「每个」")
  })
})

test("模板要求断言具体内容，不许只断言「跑完了」", function () {
  TRACKS.forEach(function (track) {
    const built = prompts.buildSupplyPrompt("generate-assert", track, {
      title: "t",
      statement: "s",
      demo: "print(1)\n",
      readme: "",
      notes: "",
      question: "",
      topics: "x",
      difficulty: "medium",
    })
    const text = String(built.user || "")
    assert.ok(text.indexOf("具体") !== -1, track + " 模板要提「具体」")
  })
})

test("模板要求脚本能区分被测逻辑被改坏的情形", function () {
  TRACKS.forEach(function (track) {
    const built = prompts.buildSupplyPrompt("generate-assert", track, {
      title: "t",
      statement: "s",
      demo: "print(1)\n",
      readme: "",
      notes: "",
      question: "",
      topics: "x",
      difficulty: "medium",
    })
    const text = String(built.user || "")
    assert.ok(text.indexOf("改坏") !== -1, track + " 模板要提「改坏」")
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-prompt.test.js
```

Expected: FAIL —— 当前模板里没有「覆盖」「每个」「具体」「改坏」这些词。

- [ ] **Step 3: 改三个轨的 `generate-assert` 模板**

`core/llm/prompts.js`，在 `database`（第 622 行起）、`ai`（第 743 行起）两个轨的 `generate-assert` 段里，
以及 `algorithm` 轨的对应段里，**给「要求写什么」那段补上以下三句**（三轨都要补，措辞可微调但三个关键词必须在）：

```text
断言脚本必须**覆盖 demo 输出的每一个主要结论**（每一段、每一个关键数字、每一条结论行），
不能只检查「跑完了」这种笼统信号；要**具体**检查 demo 该段输出的内容（具体字符串或具体数值）。
脚本必须能在「被测逻辑被改坏」时失败：只要 demo 里某个结论变了、被改成一个错值，
脚本就必须 exit 1——否则这个脚本等于没断言。
```

`algorithm` 轨的 `generate-assert`（如果该轨模板里没有这一段，就加在 `generate-unit` 的用例要求里），
额外要求：

```text
测试用例要**覆盖边界情况**（空输入、单个元素、极值），不能只有一条happy path；
用例的期望输出要**具体**（精确的 stdout 字符串），不要写「大概对」这种描述。
```

- [ ] **Step 4: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-prompt.test.js
node tests/llm-supply-prompt.test.js
node tests/supply-algorithm-prompt.test.js
```

Expected: 全部 PASS。若 `llm-supply-prompt.test.js` 因模板内容变化而失败，
检查是不是它断言了模板的**精确文本**——若是，改那条断言的期望（模板变了，期望要跟着变）。

- [ ] **Step 5: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/llm/prompts.js apps/study-hub/tests/remediation-supply-prompt.test.js
git commit -m "fix(study-hub): 断言脚本模板要求覆盖每个主要结论，能抓住被改坏的逻辑"
git push origin main
```

---

### Task 14: 抽检支持分层抽样

**Files:**
- Modify: `projects/apps/study-hub/core/supply/review.js:56-76`（`pickReviewTargets`）
- Modify: `projects/apps/study-hub/core/supply/algorithm-cli.js`（算法轨 `review` 分支）
- Test: `projects/apps/study-hub/tests/remediation-review.test.js`（追加用例）

**Interfaces:**
- Consumes: `pickReviewTargets(units, opts)`；`opts.sample`、`opts.track`
- Produces: `pickReviewTargets(units, {stratify: true})` 时按「来源 × 难度」分层，
  **每层至少 5 题**、层内按比例抽；`opts.stratify` 默认 `false`（保持 DB/AI 的 10% 口径）

**算法轨实测分层**（2026-11-22，687 道）：

| 来源 | 难度 | 题数 | 至少抽 |
|---|---|---|---|
| leetcode | medium | 404 | 41 |
| leetcode | easy | 226 | 23 |
| nowcoder | easy | 29 | 5 |
| nowcoder | medium | 28 | 5 |

合计 **≥ 74 题**。

- [ ] **Step 1: 写失败的测试**

在 `tests/remediation-review.test.js` 末尾追加：

```js
test("分层抽样：每层至少 5 题，层内按比例", function () {
  const units = []
  const sources = [
    { src: "leetcode", dif: "medium", n: 404 },
    { src: "leetcode", dif: "easy", n: 226 },
    { src: "nowcoder", dif: "easy", n: 29 },
    { src: "nowcoder", dif: "medium", n: 28 },
  ]
  sources.forEach(function (g) {
    for (let i = 0; i < g.n; i += 1) {
      units.push({
        id: g.src + ":" + g.dif + ":" + i,
        track: "algorithm",
        kind: "problem",
        title: "题 " + i,
        statement: "题面",
        entry: { demo: "", reference: "", graded: "user", script: "" },
        status: "verified",
        reviewed: false,
        source: g.src,
        difficulty: g.dif,
      })
    }
  })
  const targets = review.pickReviewTargets(units, { stratify: true })
  const layers = {}
  targets.forEach(function (t) {
    const key = String(t.source || "") + "|" + String(t.difficulty || "")
    layers[key] = (layers[key] || 0) + 1
  })
  assert.strictEqual(targets.length >= 74, true, "至少抽 74 题，实际 " + targets.length)
  // 每层至少 5 题
  Object.keys(layers).forEach(function (key) {
    assert.ok(layers[key] >= 5, key + " 层只抽了 " + layers[key] + " 题")
  })
  // 四层都要抽到
  assert.strictEqual(Object.keys(layers).length, 4, JSON.stringify(layers))
})

test("分层抽样：同一层的题不重复", function () {
  const units = []
  for (let i = 0; i < 20; i += 1) {
    units.push({
      id: "leetcode:easy:" + i,
      track: "algorithm",
      kind: "problem",
      title: "题 " + i,
      statement: "题面",
      entry: { demo: "", reference: "", graded: "user", script: "" },
      status: "verified",
      reviewed: false,
      source: "leetcode",
      difficulty: "easy",
    })
  }
  const targets = review.pickReviewTargets(units, { stratify: true })
  const ids = targets.map(function (t) { return t.id })
  assert.strictEqual(new Set(ids).size, ids.length, "不该有重复")
})
```

- [ ] **Step 2: 跑测试确认失败**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-review.test.js
```

Expected: FAIL —— `pickReviewTargets` 不认 `stratify`，会把 687 道全返回。

- [ ] **Step 3: 实现分层抽样**

`core/supply/review.js`，加一个分层函数并在 `pickReviewTargets` 里分流：

```js
/** 分层抽样的最小层样本量 */
const STRATUM_MIN = 5

/**
 * 按「来源 × 难度」分层抽样。
 *
 * 每层至少 STRATUM_MIN 题，层内按比例分配（比例按层大小，总量由 sample 定）。
 * 层的键是 source|difficulty；字段缺失的归入 (空) 层，照样至少抽 STRATUM_MIN 题。
 * @param {object[]} units
 * @param {{sample?: number}} opts
 * @returns {object[]}
 */
function pickStratifiedTargets(units, opts) {
  const o = opts || {}
  const list = (Array.isArray(units) ? units : []).filter(function (unit) {
    return unit.reviewed !== true
  })
  if (list.length === 0) return []

  const strata = {}
  const order = []
  list.forEach(function (unit) {
    const key = String(unit.source || "(空)") + "|" + String(unit.difficulty || "(空)")
    if (!strata[key]) {
      strata[key] = []
      order.push(key)
    }
    strata[key].push(unit)
  })

  const total = list.length
  const wanted = Number(o.sample) > 0 ? Number(o.sample) : list.length
  const perLayer = {}
  order.forEach(function (key) {
    const bySize = Math.round((strata[key].length / total) * wanted)
    perLayer[key] = Math.max(STRATUM_MIN, bySize)
  })
  // 总量超了就从最多的层往下削，削到不低于 STRATUM_MIN 为止
  let sum = order.reduce(function (acc, key) { return acc + perLayer[key] }, 0)
  while (sum > wanted) {
    let biggest = ""
    order.forEach(function (key) {
      if (perLayer[key] > STRATUM_MIN && (biggest === "" || perLayer[key] > perLayer[biggest])) {
        biggest = key
      }
    })
    if (biggest === "") break
    perLayer[biggest] -= 1
    sum -= 1
  }

  const out = []
  order.forEach(function (key) {
    const take = Math.min(perLayer[key], strata[key].length)
    out.push.apply(out, strata[key].slice(0, take))
  })
  return out
}
```

把 `pickReviewTargets` 改成：

```js
function pickReviewTargets(units, opts) {
  const o = opts || {}
  const only = o.track ? String(o.track) : ""
  const list = (Array.isArray(units) ? units : [])
    .filter(function (unit) {
      if (only !== "" && String(unit.track || "") !== only) return false
      // 抽检只对**已达标**的单元开放：verified（执行器与变异测试都过了）且还没被人看过。
      // draft / todo / rejected 是「还没补齐」或「没过校验」，不是抽检对象。
      if (String(unit.status || "") !== "verified") return false
      return unit.reviewed !== true
    })
    .slice()
    .sort(function (a, b) {
      const pa = STATUS_PRIORITY[String(a.status || "todo")] === undefined ? 9 : STATUS_PRIORITY[String(a.status || "todo")]
      const pb = STATUS_PRIORITY[String(b.status || "todo")] === undefined ? 9 : STATUS_PRIORITY[String(b.status || "todo")]
      if (pa !== pb) return pa - pb
      const ia = String(a.id || "")
      const ib = String(b.id || "")
      return ia < ib ? -1 : ia > ib ? 1 : 0
    })
  if (o.stratify === true) {
    return pickStratifiedTargets(list, o)
  }
  const sample = Number(o.sample) > 0 ? Number(o.sample) : list.length
  return list.slice(0, sample)
}
```

并把 `pickStratifiedTargets` 与 `STRATUM_MIN` 加进 `module.exports`：

```js
  STRATUM_MIN: STRATUM_MIN,
  pickStratifiedTargets: pickStratifiedTargets,
```

- [ ] **Step 4: 算法轨 CLI 接上分层抽样**

`core/supply/algorithm-cli.js` 的 `COMMANDS`（当前第 30 行）改成：

```js
const COMMANDS = ["plan", "generate", "verify", "report", "review", "accept", "doctor"]
```

`USAGE`（当前第 32–41 行）加一行：

```js
  "  node tools/supply.js review  --track algorithm [--sample <n>]",
```

`parseAlgorithmArgs` 的选项白名单里加上 `sample`（当前算法轨只认 `--track` / `--limit` / `--session` / `--unit` / `--batch` / `--resume` / `--retry-rejected` / `--dry-run`）：

```js
    if (arg === "--sample") {
      // 后面跟一个正整数
      const value = String(args[i + 1] || "")
      if (!/^[0-9]+$/.test(value)) {
        error = "--sample 要一个正整数"
        break
      }
      options.sample = Number(value)
      i += 2
      continue
    }
```

（照该文件里 `--limit` 的解析写法改，键名与变量名以实际代码为准。）

同时把 `runAlgorithmCommand` 里那句「算法轨只接 plan / generate / verify / report」的提示改成：

```js
    say("子命令非法：" + (options.command || "（空）") + "。算法轨接 plan / generate / verify / report / review / accept / doctor。")
```

然后在 `runAlgorithmCommand` 的分派里，`report` / `accept` 附近加一条 `review` 分支：

```js
  // 抽检：算法轨按「来源 × 难度」分层抽样，每层至少 5 题。
  // 本分支只做「分层挑选 + 分层计数报告」；交互式写回复用
  // core/supply/review.js 的 applyReview（DB/AI 轨的 review 子命令已在用它）。
  if (options.command === "review") {
    const { pickReviewTargets } = require("./review.js")
    const { loadUnits } = require("../unit/index.js")
    const learningRoot = resolveLearningRoot(o.env || process.env, o.learningRoot)
    const localBank = localBankDir(o.env || process.env, o.localBank || null)
    const loaded = loadUnits({
      learningRoot: learningRoot,
      localBank: localBank,
      unitsDir: learningRoot ? path.join(learningRoot, "units") : null,
      grokkingDir: learningRoot ? path.join(learningRoot, "scaffold", "grokking") : null,
    })
    const targets = pickReviewTargets(loaded.units || [], {
      sample: options.sample,
      track: "algorithm",
      stratify: true,
    })
    if (targets.length === 0) {
      say("没有待抽检的算法单元")
      return { code: 0, output: lines.join("\n") + "\n" }
    }
    const layers = {}
    targets.forEach(function (unit) {
      const key = String(unit.source || "(空)") + " | " + String(unit.difficulty || "(空)")
      layers[key] = (layers[key] || 0) + 1
    })
    say("待抽检算法单元 " + targets.length + " 个（按来源 × 难度分层，每层至少 5 题）")
    Object.keys(layers).forEach(function (key) {
      say("  " + key + "：抽 " + layers[key] + " 题")
    })
    say("")
    say("题目清单：")
    targets.forEach(function (unit) {
      say("  " + unit.id + "  " + unit.title)
    })
    return { code: 0, output: lines.join("\n") + "\n" }
  }
```

**注意**：`loadUnits` 是 `core/unit/index.js` 导出的（该文件第 17–21 行有
`loaderA` / `loaderB` / `loaderC` 的导入，`loadUnits` 是它的导出）。
`resolveLearningRoot` 与 `localBankDir` 来自 `core/paths.js`（该文件第 20 行已导入）。
`path` 也在第 18 行已导入。**不要重复 require。**

- [ ] **Step 5: 跑测试确认通过**

Run:

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-review.test.js
node tests/supply-cli.test.js
node tests/supply-algorithm-cli.test.js
```

Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/core/supply/review.js apps/study-hub/core/supply/algorithm-cli.js apps/study-hub/tests/remediation-review.test.js
git commit -m "feat(study-hub): 抽检支持按来源×难度分层抽样，每层至少 5 题"
git push origin main
```

---

### Task 15: 修 `mvcc` 与 `index_design` 的断言脚本

**Files:**
- Modify: `learning/units/database/mvcc.assert.py`
- Modify: `learning/units/database/index_design.assert.py`
- Test: 真实跑 `node tools/supply.js verify --unit <id>`

**Interfaces:**
- Consumes: `learning/scaffold/grokking/mvcc/main.py`（**一个字都不许改**）
- Produces: 两个脚本通过变异测试（`verify` 判 `verified`）

**实测根因**（不是断言写错，是**覆盖不足**）：

- `mvcc`：demo 唯一的条件分支是第 102 行 `if bal1 == bal2:`（第 193 行的 `__main__` 守卫被变异器跳过）。
  变异把 102 行改成 `if False:` → demo 走 `else` 分支，输出变成「读到了新数据（非快照隔离）」。
  **原脚本只断言「快照隔离」那句，没断言 else 分支那句**，所以变异后照样 `exit 0`。
- `index_design`：demo 第 107 行 `return cur.fetchone()[2]`（`explain` 函数）。
  变异改成 `return None` → `plan_a` 变 `None` → 打印 `a) WHERE last_name — 走索引: None`。
  **原脚本只断言了「最左前缀原则」那几行，没断言 a/b/c/d 四条 EXPLAIN 结果**，所以照样通过。

- [ ] **Step 1: 跑 verify 确认当前是 rejected**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js verify --unit db:mvcc
node tools/supply.js verify --unit db:index_design
```

Expected: 两个都是「已打回 变异测试未捕获，断言无效」。

- [ ] **Step 2: 补 `mvcc` 断言**

在 `learning/units/database/mvcc.assert.py` 的 `CHECKS` 列表里**追加**下列条目
（不要删原有的——原有的要保留，它们仍是有意义的检查）：

```python
    # 变异测试会改坏第 102 行的 `if bal1 == bal2:`（改成 if False）。
    # demo 于是走 else 分支，输出「读到了新数据（非快照隔离）」——
    # 这两条断言把两条分支都盯住，变异才会被抓住。
    ("快照隔离分支", "→ 快照隔离！Reader 看到的是事务开始时的快照"),
    ("非快照分支", "→ 读到了新数据（非快照隔离）"),
    # 版本链那一段的具体数值：被改坏 balance 时会变
    ("版本链初始值", "balance=1000, version=1"),
    ("版本链改后值", "balance=800.0, version=2"),
    # 写写冲突那一段的具体结论
    ("写写冲突结论", "MVCC + 行锁：写操作序列化，读操作无阻塞"),
```

（这些字符串与 `main.py` 的实际输出一一对应。跑 demo 确认：
`py -3 main.py` 的输出里有「修改后: id=1, name=Alice, balance=800.0, version=2」、
「→ 快照隔离！Reader 看到的是事务开始时的快照」、
「最终 Bob 余额 = 2100.0（2000 - 100 + 200 = 2100 [OK]）」、
「MVCC + 行锁：写操作序列化，读操作无阻塞」。）

- [ ] **Step 3: 补 `index_design` 断言**

在 `learning/units/database/index_design.assert.py` 的 `CHECKS` 里**追加**：

```python
    # 变异测试会改坏 explain() 的 `return cur.fetchone()[2]`（改成 return None），
    # 于是 a/b/c/d 四条 EXPLAIN 结果变成 None。这四条把每条结果都盯住。
    ("a 走索引", "a) WHERE last_name — 走索引:"),
    ("b 走索引", "b) WHERE last_name+first_name — 走索引:"),
    ("c 不走索引", "c) WHERE first_name — 不走索引（跳过了最左列）:"),
    ("d 部分走索引", "d) WHERE last_name+age — 走索引（但只用 last_name 列）:"),
    # 覆盖索引那一段的具体结论
    ("覆盖索引结论行", "覆盖索引避免回表，仅访问索引页面即可返回数据"),
```

**注意**：这四条断言只检查**前缀**（`a) WHERE last_name — 走索引:` 后面跟什么值不检查）。
变异把值改成 `None` 时前缀仍然在——所以还必须检查**值不是 None**。
为此在脚本里加一个额外的检查：demo 输出里**不能**出现 `走索引: None` 或 `不走索引（跳过了最左列）: None`。

在 `main()` 里，`failed = []` 之后加：

```python
    # 变异后 explain() 返回 None，打印出来就是「走索引: None」。
    # 前缀断言抓不住这个，所以单独查一遍：出现 None 就说明结果被改坏了。
    if "走索引: None" in out or "不走索引（跳过了最左列）: None" in out:
        failed.append("EXPLAIN 结果是 None：查询计划没算出来，索引结论不成立")
```

- [ ] **Step 4: 跑 verify 确认通过**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js verify --unit db:mvcc
node tools/supply.js verify --unit db:index_design
```

Expected: 两个都是「已验证 断言脚本通过，且变异测试证明断言有效」。

若仍是「变异未捕获」，说明补的断言没盯住被改坏的那一处——
读 verify 输出的 `technique`（会写明改的是哪条手法：`assert` / `if` / `return`），
针对那处补断言，**不要改 demo**。

- [ ] **Step 5: 确认 learning 仓的状态**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: 只列出 `units/database/mvcc.md`、`units/database/index_design.md`、
`units/database/mvcc.assert.py`、`units/database/index_design.assert.py` 这几个文件。
**不要自动提交**——把 diff 摆给用户看，由用户决定。

- [ ] **Step 6: 提交（只提交工程仓的测试改动；learning 仓由用户提交）**

本任务的代码改动全在 learning 仓（内容产物），工程仓**不需要**改动。
因此**不执行 git commit**。改为在对话里向用户报告：

```bash
cd C:\code\learning
git diff --stat
git diff learning  # 或 git diff
```

Expected: 打印出两个 `.assert.py` 的 diff，供用户审阅。

---

### Task 16: DB/AI 内容试跑（2 张）

**Files:**
- Create: `learning/units/database/<stem>.md` 与 `<stem>.assert.py`（由流水线产出）
- Test: 真实跑 `node tools/supply.js verify --track <轨>`

**Interfaces:**
- Consumes: `ARK_API_KEY` 或 `ANTHROPIC_API_KEY`（在 `.env` 或环境变量里）
- Produces: 2 张卡的断言脚本 + 讲解，落到 `learning/units/<track>/`

- [ ] **Step 1: 确认密钥已就位**

```powershell
cd C:\code\projects\apps\study-hub
node tools/supply.js doctor --track algorithm 2>&1 | Select-String '密钥'
```

（若 `doctor` 不接 `--track`，直接 `node tools/supply.js doctor`；该命令只报**有没有**密钥，不显示内容。）

Expected: 报「LLM 密钥 ok」。

若报缺失：在 `apps/study-hub/.env` 里填 `ARK_API_KEY=...`（或 `ANTHROPIC_API_KEY=...`），
**不要**写进命令行参数。

- [ ] **Step 2: 试跑 2 张**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js generate --track database --limit 2 --session db-trial
```

Expected: 输出「本次要补 2 个单元」，逐个打印「断言脚本已生成」「讲解正文已写入」。

- [ ] **Step 3: 校验试跑的 2 张**

```powershell
node tools/supply.js verify --track database
```

Expected: 校验数里至少 2 个是「已验证」。

若被判「已打回」，读它给出的原因，按 Task 15 的思路补断言后重跑。

- [ ] **Step 4: 人工看一遍质量**

打开 `learning/units/database/<stem>.md` 与 `<stem>.assert.py`，逐条确认：

| 检查项 | 通过标准 |
|---|---|
| 讲解有实质内容 | 不是 README/NOTES 原文的复制；有「这是什么 → 为什么这样 → 工程含义」的结构 |
| 断言盯住了关键结论 | `CHECKS` 里覆盖 demo 的**每一段**输出，不只是最后一句「演示完成」 |
| 断言检查具体值 | 至少有一条断言检查具体数值或具体字符串 |
| 脚本独立 | 断言脚本在 `learning/units/<track>/` 下，**没有**改 `scaffold/grokking/<stem>/main.py` |

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: `scaffold/` 下**没有**任何改动（教学资产零污染）。

- [ ] **Step 5: 决定是否放量**

若试跑质量达标 → 继续 Task 17。
若不达标 → **先改提示词模板**（Task 13），重新试跑，**不要**直接放量——批量返工更贵。

---

### Task 17: DB/AI 内容放量（25 张）

**Files:**
- Create: `learning/units/database/*.md`、`*.assert.py`（12 张缺脚本 + 讲解）
- Create: `learning/units/ai/*.md`、`*.assert.py`（13 张）
- Test: `node tools/supply.js verify --track database` / `--track ai`

- [ ] **Step 1: 补齐 database 轨剩下的缺口**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js generate --track database --session db-all
```

Expected: 逐个生成；若中途撞到配额上限，会停下并提示用 `--resume` 接着跑。

- [ ] **Step 2: 补齐 ai 轨**

```powershell
node tools/supply.js generate --track ai --session ai-all
```

**注意**：AI 轨的 13 张卡都依赖 numpy。本机默认解释器 `python`(3.11) 没有 numpy，
所以**判题要用 `py -3`**：

```powershell
$env:STUDY_HUB_PYTHON='py -3'
node tools/supply.js verify --track ai
```

Expected: 13 张全部「已验证」。

若判「跳过：环境缺失 numpy」，确认 `$env:STUDY_HUB_PYTHON` 已设。

- [ ] **Step 3: 补齐讲解（已通过校验但缺讲解的卡）**

`generate` 一次会同时产断言与讲解；但对**已有断言脚本**的 4 张卡
（`sql_fundamentals`、`transaction`、`mvcc`、`index_design`），要单独补讲解：

```powershell
node tools/supply.js generate --track database --limit 30 --session db-explain
```

若 CLI 的 `generate` 只挑「缺断言脚本」的单元（`pickGenerateTargets` 当前就是这样），
那么讲解要靠 Task 18 的补齐路径补上——**先记录这个缺口，继续下一步**。

- [ ] **Step 4: 全量校验两轨**

```powershell
$env:STUDY_HUB_PYTHON='py -3'
node tools/supply.js verify --track database
node tools/supply.js verify --track ai
```

Expected:
- database：16 个单元，14 个「已验证」（含 Task 15 修的 2 张），0 个「已打回」
- ai：13 个单元，13 个「已验证」

若还有「已打回」，按 Task 15 的思路修断言后重验，直到全绿或明确记录原因。

- [ ] **Step 5: 确认状态与缺口**

```powershell
node tools/supply.js plan --track database
node tools/supply.js plan --track ai
node tools/supply.js report --track database
node tools/supply.js report --track ai
```

Expected: `report` 里两轨的「欠账」都归零（讲解与断言都齐）。

- [ ] **Step 6: 确认 learning 仓状态**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: 只有 `units/` 下的新增文件；**`scaffold/` 零改动**。

**不要自动提交**——把改动量与 diff 摘要报给用户。

---

### Task 18: 讲解补齐兜底路径

**Files:**
- Modify: `projects/apps/study-hub/core/supply/plan.js`（`pickGenerateTargets` 或新增 `pickExplainTargets`）
- Modify: `projects/apps/study-hub/tools/supply.js`（`generate` 子命令）
- Test: `projects/apps/study-hub/tests/remediation-supply-prompt.test.js`（追加）

**Interfaces:**
- Consumes: `core/llm/service.js` 的 `writeExplain({unit, batchId})`（已实现）
- Produces: `node tools/supply.js generate --track <轨> --explain-only` 只补讲解，不重写断言脚本

**为什么需要**：Task 17 Step 3 会发现 `generate` 只挑「缺断言脚本」的单元，
于是**已有断言但缺讲解**的卡（4 张）补不上讲解。这个子命令补上这个洞。

- [ ] **Step 1: 写失败的测试**

在 `tests/remediation-supply-prompt.test.js` 追加：

```js
const supplyCli = require("../tools/supply.js")

test("generate 支持 --explain-only（只补讲解，不碰断言脚本）", function () {
  const parsed = supplyCli.parseArgs(["generate", "--track", "database", "--explain-only"])
  assert.strictEqual(parsed.error, "")
  assert.strictEqual(parsed.options.explainOnly, true)
})

test("--explain-only 与 --limit 可以同时给", function () {
  const parsed = supplyCli.parseArgs(["generate", "--track", "ai", "--explain-only", "--limit", "3"])
  assert.strictEqual(parsed.error, "")
  assert.strictEqual(parsed.options.explainOnly, true)
  assert.strictEqual(parsed.options.limit, 3)
})
```

- [ ] **Step 2: 跑测试确认失败**

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-prompt.test.js
```

Expected: FAIL —— `parseArgs` 遇到 `--explain-only` 会报「不接受选项」。

- [ ] **Step 3: 加参数解析**

`tools/supply.js` 有三张选项表要改（都在文件顶部）：

(a) `BOOLEAN_OPTIONS`（当前第 60 行 `const BOOLEAN_OPTIONS = ["all"]`）改成：

```js
const BOOLEAN_OPTIONS = ["all", "explain-only"]
```

(b) `ALLOWED_OPTIONS`（当前第 51–57 行）的 `generate` 一行改成：

```js
  generate: ["track", "limit", "session", "explain-only"],
```

(c) `VALUE_OPTIONS`（当前第 63 行）**不用改**——`explain-only` 是布尔开关，不带值。

改完后 `parseArgs(["generate", "--track", "database", "--explain-only"])` 会得到
`options["explain-only"] === true`（注意键名带连字符）。

**因此 Task 18 的测试要按带连字符的键名写**——把 Step 1 的测试改成：

```js
const supplyCli = require("../tools/supply.js")

test("generate 支持 --explain-only（只补讲解，不碰断言脚本）", function () {
  const parsed = supplyCli.parseArgs(["generate", "--track", "database", "--explain-only"])
  assert.strictEqual(parsed.error, "")
  assert.strictEqual(parsed.options["explain-only"], true)
})

test("--explain-only 与 --limit 可以同时给", function () {
  const parsed = supplyCli.parseArgs(["generate", "--track", "ai", "--explain-only", "--limit", "3"])
  assert.strictEqual(parsed.error, "")
  assert.strictEqual(parsed.options["explain-only"], true)
  assert.strictEqual(parsed.options.limit, "3")
})
```

（`--limit` 的值是**字符串** `"3"`，不是数字 3——`parseArgs` 不做类型转换。）

- [ ] **Step 4: 加挑选「缺讲解」的单元**

`tools/supply.js` 里新增一个函数（放在 `pickGenerateTargets` 旁边）：

```js
/**
 * 挑要补讲解正文的单元：卡类、还缺讲解的。
 * 判据是单元文件里「## 讲解」段是占位符或空的。
 * @param {object[]} units
 * @param {{track?: string, limit?: number, learningRoot?: string|null}} opts
 * @returns {object[]}
 */
function pickExplainTargets(units, opts) {
  const o = opts || {}
  const only = o.track ? String(o.track) : ""
  const limit = Number(o.limit) > 0 ? Number(o.limit) : 999
  const root = o.learningRoot || null
  const out = []
  ;(units || []).forEach(function (unit) {
    if (out.length >= limit) return
    if (String(unit.kind || "") !== "card") return
    if (only !== "" && String(unit.track || "") !== only) return
    const file = root ? path.join(root, "units", String(unit.track || ""), String(unit.id || "").split(":").pop() + ".md") : null
    if (!file || !fs.existsSync(file)) return
    const text = fs.readFileSync(file, "utf8")
    const m = /##\s*讲解\s*\r?\n([\s\S]*?)(?:\r?\n##\s|$)/.exec(text)
    const body = m ? String(m[1] || "").trim() : ""
    if (body === "" || body === "（讲解正文还没生成）") out.push(unit)
  })
  return out
}
```

并把它加进 `module.exports`：

```js
  pickExplainTargets: pickExplainTargets,
```

- [ ] **Step 5: `generate` 子命令分流**

`tools/supply.js` 的 `generate` 分支里，在挑完 `targets` 之后加：

```js
      if (options["explain-only"] === true) {
        const explainTargets = pickExplainTargets(units, {
          track: track,
          limit: limit > 0 ? limit : 999,
          learningRoot: learning.root,
        })
        if (explainTargets.length === 0) {
          say("没有缺讲解的单元")
          return done(EXIT_OK)
        }
        say("本次要补讲解 " + explainTargets.length + " 个单元")
        let wrote = 0
        for (const unit of explainTargets) {
          say("—— " + unit.id + " " + unit.title + " ——")
          try {
            const explained = await service.writeExplain({ unit: unit, batchId: batchId })
            say("  讲解正文已写入：" + path.relative(learning.root, explained.file))
            wrote += 1
          } catch (e) {
            warn("  " + unit.id + " 讲解失败：" + String((e && e.message) || e))
          }
        }
        say("本次补讲解：" + wrote + " 个")
        return done(EXIT_OK)
      }
```

（`service`、`batchId`、`learning`、`units` 这些变量名以该文件当前 `generate` 分支里的实际用法为准；
`batchId` 在该分支里是 `String(options.session || "supply")`。）

- [ ] **Step 6: 跑测试确认通过**

```powershell
cd C:\code\projects\apps\study-hub
node tests/remediation-supply-prompt.test.js
node tests/supply-cli.test.js
```

Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
cd C:\code\projects
git add apps/study-hub/tools/supply.js apps/study-hub/tests/remediation-supply-prompt.test.js
git commit -m "feat(study-hub): generate 加 --explain-only，只补讲解不碰断言脚本"
git push origin main
```

---

### Task 19: 回补 4 张已有断言卡的讲解

**Files:**
- Modify: `learning/units/database/*.md`（4 张卡的「## 讲解」小节）

- [ ] **Step 1: 确认哪些卡缺讲解**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js plan --track database
```

Expected: 输出里「缺讲解正文」的卡列出 `sql_fundamentals`、`transaction`、`mvcc`、`index_design`。

- [ ] **Step 2: 补讲解**

```powershell
node tools/supply.js generate --track database --explain-only --session db-explain
```

Expected: 逐个打印「讲解正文已写入」。

- [ ] **Step 3: 确认缺口归零**

```powershell
node tools/supply.js plan --track database
node tools/supply.js report --track database
```

Expected: database 轨不再报「缺讲解正文」；`report` 的欠账归零。

- [ ] **Step 4: 确认 learning 仓状态**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: 只有 `units/database/` 下的文件改动。**不要自动提交**。

---

### Task 20: 算法轨 687 道批量补齐

**Files:**
- Create: `learning/units/algorithm/<stem>.md`、`<stem>.reference.cpp`、`<stem>.negative.cpp`

- [ ] **Step 1: 环境自检**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js doctor --track algorithm
```

Expected: 各项 `✅`；g++ 可用、learning 仓通、密钥有。

若该子命令不在当前 CLI 里，直接跑 `node tools/supply.js plan --track algorithm` 看清单。

- [ ] **Step 2: 先 dry-run 看计划（不花钱）**

```powershell
node tools/supply.js plan --track algorithm
```

Expected: 打印「算法轨缺口清单（共 N 题）」，N = 687 附近。

- [ ] **Step 3: 先试跑 3 道**

```powershell
node tools/supply.js generate --track algorithm --batch --limit 3 --session algo-trial
```

Expected: 产出 3 道四件套。

- [ ] **Step 4: 校验试跑的 3 道**

```powershell
node tools/supply.js verify --track algorithm --limit 3
```

（若 `--limit` 不被 `verify` 接受，就用 `node tools/supply.js verify --track algorithm` 全量跑，
或逐个 `--unit <id>` 校验。）

Expected: 3 道都是「已验证」。

若被判「已打回」，读原因：
- 「负例全过」→ 用例太弱，要加强用例
- 「负例编译失败」→ 负例本身写错了，要重生成
- 「参考解法没全 AC」→ 用例或解法有问题，要重生成

**先修好试跑，再放量**——不要带着已知缺陷跑 687 道。

- [ ] **Step 5: 人工看一遍 3 道**

打开 `learning/units/algorithm/<stem>.md`、`<stem>.reference.cpp`、`<stem>.negative.cpp`，确认：

| 检查项 | 通过标准 |
|---|---|
| 题面完整 | 有可读的题目描述，不是占位 |
| 用例真实 | 测试用例表里有具体输入输出，不是空的 |
| 参考解法合理 | 能编译、逻辑对、不是「打印正确答案」的作弊 |
| 负例真实 | 是**错的解法**，不是随机垃圾 |

- [ ] **Step 6: 放量（分批，可断点续跑）**

```powershell
node tools/supply.js generate --track algorithm --batch --session algo-all
```

Expected: 跑到配额上限就停，提示「用 `--resume` 接着跑」。

```powershell
node tools/supply.js generate --track algorithm --batch --resume --session algo-all
```

重复到不再有待生成的题。

**注意**：687 道 × 每道至少 1 次 LLM 调用，加上重试，调用量可能上千次。
按 `supply.batch.daily_limit`（默认 800）分天跑完是正常的，不是故障。

- [ ] **Step 7: 全量校验**

```powershell
node tools/supply.js verify --track algorithm
```

Expected: 打印「校验了 N 个单元：通过 X，打回 Y，跳过 Z」。

**这一条会真编译 687 道题**，耗时可达 40–70 分钟。跑之前确认 g++ 可用。

- [ ] **Step 8: 重打回的那些**

```powershell
node tools/supply.js generate --track algorithm --batch --retry-rejected --session algo-fix
node tools/supply.js verify --track algorithm
```

Expected: 打回数下降。

若某几道反复打回（负例编译不过之类），把它们**单独列出来**，
在验收记录里写明「这 N 道没补齐，原因是 ___」，**不要**假装全绿。

- [ ] **Step 9: 看覆盖报告与交付审计**

```powershell
node tools/supply.js report --track algorithm
node tools/supply.js accept --track algorithm
```

Expected: `report` 打出欠账；`accept` 的 12 条自查表逐条 `✅` / `❌` / `…`。
有 `❌` 就按它指出的问题修，修完重跑 `accept`。

- [ ] **Step 10: 确认 learning 仓状态**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: 只有 `units/algorithm/` 下的新增文件；`bank/` 与 `scaffold/` **零改动**。

**不要自动提交**。

---

### Task 21: DB/AI 分层抽检

**Files:**
- Modify: `learning/units/database/*.md`、`learning/units/ai/*.md`（写回 `reviewed` / `reviewed_at`）

- [ ] **Step 1: 抽检 database 轨**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js review --track database --sample 2
```

Expected: 交互式显示每个单元的题面与断言脚本，输入 `y` 通过 / `n` 打回 / `q` 退出。

- [ ] **Step 2: 抽检 ai 轨**

```powershell
node tools/supply.js review --track ai --sample 2
```

（13 张卡的 10% 是 1.3 → 至少 1 个；这里抽 2 个。）

- [ ] **Step 3: 确认抽检写回**

```powershell
cd C:\code\learning
git diff --stat
```

Expected: 被抽检的单元文件里 `reviewed: true` 与 `reviewed_at: <今天>` 有变化。

- [ ] **Step 4: 打回项的处理**

若有打回（`status: rejected`）：

```powershell
cd C:\code\projects\apps\study-hub
node tools/supply.js generate --track database --session db-fix
node tools/supply.js verify --track database
node tools/supply.js review --track database --sample 2
```

Expected: 修订 → 重验 → 重新抽检。

---

### Task 22: 算法轨分层抽检（≥74 题）

**Files:**
- Modify: `learning/units/algorithm/*.md`（写回 `reviewed` / `reviewed_at`）

- [ ] **Step 1: 跑分层抽样并看分层计数**

```powershell
cd C:\code\projects\apps\study-hub
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
node tools/supply.js review --track algorithm
```

Expected: 打印每层的抽样数，合计 ≥ 74。

- [ ] **Step 2: 逐层抽检**

按打印的层次逐个抽检。检查项：

| 检查项 | 通过标准 |
|---|---|
| 题面 | 能读懂、有完整描述，不是占位文字 |
| 测试用例 | 有具体输入输出，覆盖了边界情况 |
| 参考解法 | 逻辑正确、能编译，不是作弊（直接打印期望答案） |
| 负例 | 确实是**错解**（编译得过但答案错），不是垃圾代码 |
| 负例不外泄 | `<stem>.md` 里**没有**负例代码（`accept` 的审计会查这一条） |

- [ ] **Step 3: 失败层扩样**

某一层出现打回 → **该层抽检量扩大到原来的 2 倍**（最少 +5），重新抽检该层。

```powershell
node tools/supply.js review --track algorithm
```

（若 CLI 不支持按层扩样，就在验收记录里写明「该层扩样到 N 题，由人工逐题核对」，
并列出扩样后的实际题目清单。）

- [ ] **Step 4: 确认抽检写回**

```powershell
cd C:\code\learning
git diff --stat | Select-Object -Last 5
```

Expected: 抽检过的单元文件有 `reviewed: true`。

---

### Task 23: R3 全量验收与文档回写

**Files:**
- Create: `C:\code\docs\superpowers\specs\2026-11-22-study-hub-r3-acceptance.md`
- Modify: `C:\code\docs\superpowers\plans\2026-11-12-study-hub-P0-*.md` 等 P0–P5 计划（勾选与实测回写）

- [ ] **Step 1: 跑全量测试**

```powershell
cd C:\code\projects\apps\study-hub
node tests/run-all.js 2>&1 | Select-Object -Last 3
```

Expected: 全绿，套件数 ≥ 111 + 本轮新增。

- [ ] **Step 2: 三轨冒烟**

起服务（后台）：

```powershell
$env:STUDY_HUB_LEARNING_ROOT='C:\code\learning'
$env:STUDY_HUB_PYTHON='py -3'
$env:PORT='5199'
node server/main.js
```

逐个打：

```powershell
(Invoke-WebRequest 'http://127.0.0.1:5199/api/health' -UseBasicParsing).StatusCode
(Invoke-WebRequest 'http://127.0.0.1:5199/api/supply/status' -UseBasicParsing).Content
(Invoke-WebRequest 'http://127.0.0.1:5199/api/diagnose?view=mastery' -UseBasicParsing).Content
```

Expected:
- `/api/health` → 200
- `/api/supply/status` 的 database 与 ai 轨 `verified` 分别是 16 与 13；`gaps` 为空
- `/api/diagnose?view=mastery` 三轨都有非零 unitCount

**再验一条真判题**：

```powershell
$body = @{} | ConvertTo-Json
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/units/db:mvcc/judge' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
($r.Content | ConvertFrom-Json) | Select-Object verdict, passed, total, message | Format-List
```

Expected: `verdict = pass`，`passed = total`。

再验一条 AI 卡（需要 numpy）：

```powershell
$r = Invoke-WebRequest 'http://127.0.0.1:5199/api/units/ai:cnn/judge' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
($r.Content | ConvertFrom-Json) | Select-Object verdict, message | Format-List
```

Expected: `verdict = pass`（服务必须带 `STUDY_HUB_PYTHON=py -3` 启动，否则是环境缺失）。

- [ ] **Step 3: 停服务并确认 learning 仓**

```powershell
cd C:\code\learning
git status --porcelain
```

Expected: 只有 `units/` 下的内容产物。**这是预期的**——内容产物要由人审阅后提交。

- [ ] **Step 4: 写 R3 验收记录**

创建 `C:\code\docs\superpowers\specs\2026-11-22-study-hub-r3-acceptance.md`：

```markdown
# study-hub R3 验收记录（内容补齐与验收）

> 日期：<填>
> 范围：Task 13–23
> 设计：[2026-11-22-study-hub-remediation-design.md](2026-11-22-study-hub-remediation-design.md)

## 内容产出（四项计数，缺一不可）

| 轨 | verified | rejected | 仍 todo | 已抽检 |
|---|---|---|---|---|
| database | <填> | <填> | <填> | <填> |
| ai | <填> | <填> | <填> | <填> |
| algorithm | <填> | <填> | <填> | <填> |

## 算法轨分层抽检

| 来源 | 难度 | 总题数 | 抽检数 | 打回数 |
|---|---|---|---|---|
| leetcode | medium | 404 | <填> | <填> |
| leetcode | easy | 226 | <填> | <填> |
| nowcoder | easy | 29 | <填> | <填> |
| nowcoder | medium | 28 | <填> | <填> |

抽检合计 <填>（下限 74）。

## 测试与冒烟

- `node tests/run-all.js` → <贴真实结果>
- 三轨冒烟：<贴真实结果>

## 未补齐的部分

| 单元 | 原因 | 打算怎么办 |
|---|---|---|
| <填> | <填> | <填> |

（没有就写「无」。有就一条条列清楚——**不写「全部完成」却有欠账**。）
```

- [ ] **Step 5: 回写 P0–P5 计划的勾选与实测**

对 `C:\code\docs\superpowers\plans\2026-11-12-study-hub-P0-*.md` 到 `P5-*.md` 六个文件：
把**实际完成**的 Step 从 `- [ ]` 改成 `- [x]`，并在文件末尾加一节「实测结果回写」：

```markdown
## 实测结果回写（2026-11-22）

- 本计划涉及的单元：<填>
- 实际改动：<填文件清单>
- 验证方式：<填命令与结果>
- 与原计划的偏差：<填，没有就写「无」>
```

**只勾真正做完的**。没做完的保持 `- [ ]`，并在偏差一节说明原因。

- [ ] **Step 6: 提交文档**

```bash
cd C:\code
git add docs/superpowers/specs/2026-11-22-study-hub-r3-acceptance.md docs/superpowers/plans/2026-11-12-study-hub-P*.md
git commit -m "docs(验收): 记录 study-hub R3 内容补齐实测结果并回写 P0-P5 计划"
git push origin main
```

---

## 计划自检

| 检查项 | 结果 |
|---|---|
| 规格覆盖 | 设计 §4.1→Task 15/16/17/18/19/21；§4.2→Task 20；§3.3→Task 13/15/20；§3.4→Task 14/21/22；§8 R2/R3→Task 16–23 |
| 占位符扫描 | 代码步骤全部给全；验收记录模板里的 `<填>` 是**运行时填实测数字**的位置，不是未写的代码 |
| 类型一致 | `pickReviewTargets(units, {stratify})`（Task 14 定义、Task 14/21/22 使用）；`pickExplainTargets`（Task 18 定义并导出、Task 18/19 使用）；`--explain-only`（Task 18 定义、Task 19 使用）；`EMPTY_EXPLAIN`（R0 Task 3 定义、R0 Task 4/18 使用） |
| 关键修正 | `mvcc` / `index_design` 的失败根因是**断言覆盖不足**（实测定位到 demo 的具体行号），Task 15 给的是补断言的具体条目，不是「改一下试试」 |
| 依赖 | 明确前置：R0/R1 必须先做完；算法轨与卡内容共用配额，两轨串行 |
