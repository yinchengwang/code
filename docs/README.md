# docs

本目录是 `code` 聚合仓的**权威文档目录**（受 git 跟踪）。

历史说明：`C:\code\docs` 曾经是 `StillEvolving/docs` 的手工镜像副本，只用于 WorkBuddy 交接期间的临时存放。该角色已取消 —— 现在只有这一份，不再有镜像，也不会漂移。

## 内容

| 路径 | 作用 |
|---|---|
| [`architecture.md`](architecture.md) | 目录规范总览：四个仓的目录树、归属判定规则、操作红线 |
| [`architecture-review-2026-10-25.md`](architecture-review-2026-10-25.md) | 2026-10-25 切仓设计的架构评审记录 |
| [`repos.yaml.sample.yaml`](repos.yaml.sample.yaml) | `repos.yaml` 的示例与字段说明 |
| [`superpowers/specs/`](superpowers/specs/) | 设计文档原件（binding authority） |
| [`superpowers/plans/`](superpowers/plans/) | 执行计划与阶段审计报告 |

## 读改规则

- **机器可读的仓关系**在仓库根目录的 `repos.yaml`，不在本目录。
- `superpowers/specs/` 与 `superpowers/plans/` 里的历史文档保留当时的措辞与路径（包括 `StillEvolving` 字样）—— 它们是决策记录，不是当前操作指引，**不做批量重写**。
- 需要改当前的目录规范时，改 `architecture.md`。
