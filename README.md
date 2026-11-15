# code

个人代码仓的**顶层聚合仓**。这里不放业务代码，只放**四个仓库之间的关系**、引导脚本与目录规范。

## 四个仓库

| 仓 | 路径 | 获取方式 | 放什么 |
|---|---|---|---|
| projects | `projects/` | submodule | 引擎代码、小程序、项目级文档、agent 规约 |
| learning | `learning/` | submodule | 学习笔记、脚手架、算法题解 |
| ai-docs | `ai-docs/` | submodule | 跨项目复用的模板与方法论 |
| reference | `reference/` | submodule + `update=none` | 第三方源码镜像 + 源码笔记 |

```text
code/                                  ← 顶层聚合仓：只放关系，不放业务代码
├── projects/            ← submodule ──▶ github.com/yinchengwang/projects.git
│   ├── vendor/third_part/googletest   ← 嵌套 submodule（各仓自理）
│   └── engine/third_part/uthash       ← 嵌套 submodule（各仓自理）
├── learning/            ← submodule ──▶ github.com/yinchengwang/learning.git
│   └── third_part/googletest          ← 嵌套 submodule（各仓自理）
├── ai-docs/             ← submodule ──▶ github.com/yinchengwang/AI-DOCS.git
└── reference/           ← submodule ──▶ github.com/yinchengwang/reference.git
    └── reference/<model>/<name>/       ← 95 个上游库 submodule，按需拉取
```

## 关系的权威定义在哪

| 文件 | 作用 |
|---|---|
| [`repos.yaml`](repos.yaml) | 机器可读的四仓清单 —— **唯一权威的「关系」定义**（URL / 角色 / 拉取策略 / `must_contain`） |
| [`docs/architecture.md`](docs/architecture.md) | 目录树与归属判定规则总览 |
| [`docs/superpowers/specs/`](docs/superpowers/specs/) | 设计文档原件 |
| [`docs/superpowers/plans/`](docs/superpowers/plans/) | 执行计划与阶段审计报告 |
| `.gitmodules` | git 原生事实：4 条子仓 pin（含 reference 的 `update = none`） |

`repos.yaml` 承载语义，`.gitmodules` 承载 git 事实，两者由 `scripts/check_consistency.py` 保证不漂移。

## 为什么 reference 用 `update = none`

`reference` 内部有 95 个第三方库 submodule，递归初始化会一次性拉取约 **25 GB / 53.6 万文件**。因此它在 `.gitmodules` 里标 `update = none`：

- 普通的 `git submodule update` 会**跳过**它，不会误触发大规模下载；
- `scripts/bootstrap.sh` 用 `git -c submodule.reference.update=checkout` 显式覆盖一次；
- 它内部的上游库仍按 `reference/reference/catalog.yml` 的 commit 声明、按需克隆。

> ⚠️ **任何时候都不要裸用 `git submodule update --init --recursive`** —— 它会拉 reference 内部的 95 个库。

## 快速开始

```bash
git clone https://github.com/yinchengwang/code.git
cd code
bash scripts/bootstrap.sh                     # 拉起 4 个 submodule（reference 显式覆盖 update=none）
bash scripts/fetch-reference.sh --tier core   # 按需拉第三方库（可选）
```

Windows PowerShell 用 `scripts/bootstrap.ps1`。

## 常用脚本

| 脚本 | 作用 |
|---|---|
| `scripts/bootstrap.sh` / `.ps1` | 初始化四个 submodule + 一致性校验 |
| `scripts/fetch-reference.sh` | 按 catalog 拉取 reference 的上游源码 |
| `scripts/check_consistency.py` | 校验 `repos.yaml` ↔ `.gitmodules` ↔ 实际目录 |

```bash
bash scripts/fetch-reference.sh --tier core        # 按 tier 拉（默认 core）
bash scripts/fetch-reference.sh --name faiss       # 拉单个
bash scripts/fetch-reference.sh --model vector     # 按分类拉
bash scripts/fetch-reference.sh --check            # 只校验清单与磁盘，不拉取
python scripts/check_consistency.py                # 四仓一致性校验
```

## 常见问题

### 为什么第一次 `git clone` 后 submodule 目录是空的？

远程初始化仓只包含 code 自身的 Git 跟踪文件，不包含 submodule 工作树内容。请在 code 根运行：

```bash
bash scripts/bootstrap.sh
```

该脚本会初始化四个直接 submodule，并执行一致性检查。手动初始化时可用 `git submodule update --init`；由于 reference 在 `.gitmodules` 标记了 `update = none`，该命令会跳过 reference。bootstrap 脚本显式覆盖该设置并初始化 reference 的仓库本身；它**不会**递归初始化 reference 内部的 95 个第三方库。按需获取这些源码请使用 `scripts/fetch-reference.sh`。

### `git clone --recurse-submodules` 会做什么？

会尝试递归初始化四个直接 submodule，再向下递归。reference 的 `update = none` **已在沙盒实测**：裸 `git submodule update --init` 会打印 `Skipping submodule 'child'` 并保持未初始化；只有显式 `-c submodule.<name>.update=checkout` 才会初始化，且该覆盖**不会**向下递归它的上游。

> 当前 Stage A 的 clean clone 检查仍有一项未完成：learning 的克隆在本机超时，**因此完整 clean clone 不能宣称验证通过**。递归 clone 本身被推荐避开（不是因为它会拉 25 GB，而是因为一旦 Git 行为与预期不同，代价极高）；推荐普通 clone 后运行 bootstrap。

### 如何检查 code 与子仓 pin 一致？

```bash
python scripts/check_consistency.py
 git submodule status
```

`repos.yaml` 是仓角色、路径和策略的语义清单；`.gitmodules` 与 index 中的 gitlink 是 Git URL/update/pin 的实际记录。子仓独立提交推送后，需要在 code 仓更新相应 gitlink。

## 迁移资料

目录重构、Stage A0 仓库审计和数据库收敛总设计保存在 [`docs/superpowers/`](docs/superpowers/)；执行步骤与验证门保存在 [`docs/superpowers/plans/2026-11-15-code-umbrella-and-db-convergence.md`](docs/superpowers/plans/2026-11-15-code-umbrella-and-db-convergence.md)。

## 归谁管什么

| 内容 | 归属 |
|---|---|
| 引擎、小程序、项目级文档、agent 规约 | `projects/` |
| 学习笔记、课程进度、题解、Obsidian vault | `learning/` |
| 跨项目复用的模板、方法论、模式、提示词 | `ai-docs/` |
| 第三方源码镜像与带行号的源码笔记 | `reference/` |
| 四仓关系、bootstrap、目录规范 | **本仓（code）** |
