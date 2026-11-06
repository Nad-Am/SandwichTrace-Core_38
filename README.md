# SandwichTrace-Core_38

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)

`SandwichTrace-Core_38` 是一个面向 Ethereum / Uniswap V2 交易场景的**轻量级、离线可验证三明治攻击检测与评测内核**。

项目采用分层模块化架构与契约化设计，为区块链安全研究者与开发者提供一个不依赖 RPC、数据库和后端的攻击三联体匹配基准。

当前版本使用人工构造的离线 Fixtures 验证规则逻辑，不代表已经完成真实链上全量检测实验。

---

## 核心特性

- **轻量纯粹**：纯 Python 实现，零以太坊节点 RPC 依赖，可直接离线回放 JSON Fixtures。
- **确定性判定流水线**：严格按执行顺序（$A < B < C$）、同池约束、发起者关系、交易方向与 Quote Token 毛收益信号进行综合裁决。
- **强类型数据契约**：基于 Pydantic 构建统一的数据模型（`Transaction`、`SwapEvent`、`DetectionInput`、`SandwichMatch`），保证数据流转规范。
- **内置基准评测体系**：内置 9 个覆盖攻击、正常 Swap 与边界异常的离线 Fixtures，支持自动化 Precision / Recall / F1-Score 评测。
- **可解释结果**：每条命中保留稳定规则原因，并区分核心检测条件与可选价格影响证据。
- **多命中支持**：一个区块的检测结果可以包含零个、一个或多个独立 `SandwichMatch`。

---

## 快速上手

### 1. 环境准备
```bash
git clone git@github.com:Nad-Am/SandwichTrace-Core_38.git
cd SandwichTrace-Core_38
python -m pip install -e ".[dev]"
```

### 2. 执行单样本检测回放（Replay）
```bash
python cli.py replay --fixture dataset/fixtures/attacks/attack_standard.json
```

### 3. 执行全量测试集评测（Evaluate）
```bash
python cli.py evaluate --dataset dataset/fixtures
```

也可以按照显式清单执行：

```bash
python cli.py evaluate --manifest dataset/manifest.json
```

### 4. 运行自动化测试
```bash
python -m pytest
```

当前测试集包含 33 个测试，覆盖契约校验、数据装配、候选筛选、非连续三联体匹配、误报边界、检测引擎、评测指标和 CLI。

---

## 当前能力边界

- 支持 Ethereum / Uniswap V2 风格的标准化离线事件。
- 仅检测同一区块、单个 Pool、单跳、单次 Swap 三联体。
- 使用交易发起者 EOA 关联攻击者身份。
- 毛收益仅计算 `C.amount_out - A.amount_in`，不扣除 Gas 或手续费。
- `PoolSnapshot` 和 `price_impact_confirmed` 作为扩展点保留，价格影响尚未参与核心判定。
- 暂不实现 RPC、Mempool、Reorg、多跳路由、多地址协同、FastAPI、数据库和 Vue。

---

## 项目设计与战略文档体系

本项目将设计背景、系统架构、能力边界、数据契约、检测规则以及商业战略拆离为独立的设计文档，避免架构与实现细节相互混杂：

| 文档 | 核心定位与主要解决的问题 | 边界与归属 |
| :--- | :--- | :--- |
| [`docs/01_DESIGN_BACKGROUND.md`](./docs/01_DESIGN_BACKGROUND.md) | **设计背景**：为什么做该项目？问题定义、核心目标与应用价值 | 当前 Core 规格 |
| [`docs/02_ARCHITECTURE.md`](./docs/02_ARCHITECTURE.md) | **架构设计**：系统整体如何组织？六层分层架构、模块单一职责与数据流 | 当前 Core 规格 |
| [`docs/03_SCOPE_AND_BOUNDARIES.md`](./docs/03_SCOPE_AND_BOUNDARIES.md) | **范围与边界**：当前 MVP 做什么、不做什么？与后续全栈演进的刚性边界隔离 | 当前 Core 规格 |
| [`docs/04_DATA_CONTRACTS.md`](./docs/04_DATA_CONTRACTS.md) | **数据契约**：模块间传递什么数据？强类型 Pydantic 模型与字段约束 | 当前 Core 规格 |
| [`docs/05_DETECTION_RULES.md`](./docs/05_DETECTION_RULES.md) | **检测规则**：如何判定攻击？9 项核心条件、毛收益信号口径与评测标准 | 当前 Core 规格 |
| [`STRATEGIC_ANALYSIS.md`](./STRATEGIC_ANALYSIS.md) | **项目战略分析**：行业洞察、竞争壁垒、战略控制点与中长期演进 | 项目发展规划 |

---

## 开源许可证

本项目遵循 [Apache License 2.0](./LICENSE) 开放源代码，允许商业与学术用途，并附带明确的专利授权保护条款。
