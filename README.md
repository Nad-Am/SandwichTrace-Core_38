# SandwichTrace-Core_38

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Tests: 33 Passed](https://img.shields.io/badge/Tests-33%20Passed-success.svg)]()
[![Type Checking: Strict](https://img.shields.io/badge/Typing-Pydantic_V2-blueviolet.svg)]()

> [English](#english) | [中文说明](#中文说明)

---

<a name="english"></a>
## English

`SandwichTrace-Core_38` is a lightweight, offline-verifiable detection and evaluation core for **Uniswap V2 sandwich attacks** on Ethereum. 

Designed under a layered modular architecture with strict typed data contracts, it provides blockchain security researchers and engineers with a standalone, RPC-free, database-free matching benchmark for transaction triplets.

*Note: The current MVP operates on curated offline fixtures to evaluate matching logic and ground-truth metrics, rather than streaming live on-chain blocks.*

### Key Features

- **Pure & Lightweight**: 100% Python implementation with zero dependency on live RPC nodes or external databases. Replays and verifies JSON fixtures in $<5\text{ms}$.
- **Deterministic Pipeline**: Evaluates candidate triplets strictly based on intra-block execution order ($A < B < C$), single-pool invariants, opposite trade directions, actor relationship, and positive Quote Token gross profit signals.
- **Typed Data Contracts**: Robust schema definitions built upon Pydantic V2 (`Transaction`, `SwapEvent`, `DetectionInput`, `SandwichMatch`), ensuring contract-first data flow.
- **Built-in Benchmark & Evaluation**: Includes 9 offline scenarios across typical attacks, benign swaps, and boundary edge cases with automated Precision, Recall, and F1-score evaluation.
- **Explainable Diagnostics**: Every detected match retains deterministic rule triggers, explicitly decoupling core invariants from optional price-impact signals.
- **Multi-Match Support**: A single block payload can yield zero, one, or multiple independent `SandwichMatch` instances.

### Quick Start

#### 1. Setup Environment
```bash
git clone git@github.com:Nad-Am/SandwichTrace-Core_38.git
cd SandwichTrace-Core_38
python -m pip install -e ".[dev]"
```

#### 2. Replay Single Fixture
```bash
python cli.py replay --fixture dataset/fixtures/attacks/attack_standard.json
```

#### 3. Evaluate Dataset
```bash
python cli.py evaluate --dataset dataset/fixtures
# Or via explicit manifest
python cli.py evaluate --manifest dataset/manifest.json
```

#### 4. Run Test Suite
```bash
python -m pytest
```
*Current test suite contains 33 unit and integration tests covering contracts validation, dataset assembly, candidate filtering, non-adjacent matching, false-positive boundaries, engine execution, metrics, and CLI workflows.*

### Scope & Boundaries (MVP)

- **Supported**: Single-pool, single-hop, intra-block triplets on Ethereum / Uniswap V2 AMM models.
- **Actor Attribution**: Relies on EOA `Transaction.from_address` consistency between front-run and back-run.
- **Profit Metric**: Evaluates Quote Token gross profit signal (`C.amount_out - A.amount_in`) without deducting Gas or execution overhead.
- **Deferred to Future Roadmap**: Real-time RPC streaming, Mempool interception, Reorg state machine rollbacks, multi-hop routing, multi-address collusion, FastAPI daemon, and Vue 3 frontend.

### Documentation & Strategic Architecture

| Document | Primary Focus | Boundary / Scope |
| :--- | :--- | :--- |
| [`docs/01_DESIGN_BACKGROUND.md`](./docs/01_DESIGN_BACKGROUND.md) | **Design Background**: Motivation, problem formulation, and core value | Current Core Spec |
| [`docs/02_ARCHITECTURE.md`](./docs/02_ARCHITECTURE.md) | **Architecture**: 6-layer decoupled system layout, responsibilities, and data flow | Current Core Spec |
| [`docs/03_SCOPE_AND_BOUNDARIES.md`](./docs/03_SCOPE_AND_BOUNDARIES.md) | **Scope & Boundaries**: MVP supported features vs. deferred roadmap boundaries | Current Core Spec |
| [`docs/04_DATA_CONTRACTS.md`](./docs/04_DATA_CONTRACTS.md) | **Data Contracts**: Pydantic schema models, field constraints, and structures | Current Core Spec |
| [`docs/05_DETECTION_RULES.md`](./docs/05_DETECTION_RULES.md) | **Detection Rules**: 9 core criteria, profit calculation, and benchmark metrics | Current Core Spec |
| [`STRATEGIC_ANALYSIS.md`](./STRATEGIC_ANALYSIS.md) | **Strategic Analysis**: Huawei "5-Looks & 3-Determines" strategic positioning & roadmap | Course & Project Plan |

---

<a name="中文说明"></a>
## 中文说明

`SandwichTrace-Core_38` 是一个面向以太坊（Ethereum）/ Uniswap V2 交易场景的**轻量级、离线可验证三明治攻击检测与评测内核**。

项目采用分层模块化架构与契约化设计，为区块链安全研究者与开发者提供一个不依赖 RPC 节点、数据库和 Web 服务的交易三联体匹配基准。

*注：当前版本使用离线基准固件（JSON Fixtures）评测判定逻辑与指标，聚焦于离线可重现的核心算法实现。*

### 核心特性

- **轻量纯粹**：纯 Python 实现，零以太坊节点 RPC 依赖，直接离线回放测试固件，单次检测耗时 $<5\text{ms}$。
- **确定性判定流水线**：严格按区块内执行顺序（$A < B < C$）、同池约束、发起者对冲关系、交易方向与 Quote Token 毛收益信号进行综合裁决。
- **强类型数据契约**：基于 Pydantic V2 构建统一的数据模型（`Transaction`、`SwapEvent`、`DetectionInput`、`SandwichMatch`），保证数据流转规范。
- **内置基准评测体系**：内置 9 个覆盖攻击、正常 Swap 与边界异常的离线固件，支持自动化 Precision / Recall / F1-Score 评测。
- **可解释性结果**：每条命中保留稳定的规则触发原因，并解耦核心检测条件与可选价格影响证据。
- **多命中支持**：单区块内支持零个、一个或多个独立 `SandwichMatch` 实例的并行提取。

### 快速上手

#### 1. 环境准备
```bash
git clone git@github.com:Nad-Am/SandwichTrace-Core_38.git
cd SandwichTrace-Core_38
python -m pip install -e ".[dev]"
```

#### 2. 执行单样本检测回放（Replay）
```bash
python cli.py replay --fixture dataset/fixtures/attacks/attack_standard.json
```

#### 3. 执行全量测试集评测（Evaluate）
```bash
python cli.py evaluate --dataset dataset/fixtures
# 或通过显式清单执行
python cli.py evaluate --manifest dataset/manifest.json
```

#### 4. 运行自动化测试
```bash
python -m pytest
```
*当前测试集包含 33 个单元与集成测试，覆盖契约校验、数据装配、候选筛选、非连续三联体匹配、误报边界、检测引擎、评测指标与 CLI。*

### 当前能力边界（MVP）

- 支持 Ethereum / Uniswap V2 风格的标准化离线事件。
- 仅检测同一区块、单个流动性池、单跳、单次 Swap 三联体。
- 基于交易发起者 EOA 关联攻击者身份。
- 毛收益仅计算 `C.amount_out - A.amount_in`，不扣除 Gas 或外部手续费。
- `PoolSnapshot` 和 `price_impact_confirmed` 作为扩展点保留，价格影响不作为必要前置条件。
- 暂不引入实时 RPC 抓取、Mempool 监听、Reorg 状态机、多跳路由、多地址协同、FastAPI 服务与前端看板。

### 项目设计与战略文档体系

| 文档 | 核心定位与主要解决的问题 | 边界与归属 |
| :--- | :--- | :--- |
| [`docs/01_DESIGN_BACKGROUND.md`](./docs/01_DESIGN_BACKGROUND.md) | **设计背景**：为什么做该项目？问题定义、核心目标与应用价值 | 当前 Core 规格 |
| [`docs/02_ARCHITECTURE.md`](./docs/02_ARCHITECTURE.md) | **架构设计**：系统整体如何组织？六层分层架构、模块单一职责与数据流 | 当前 Core 规格 |
| [`docs/03_SCOPE_AND_BOUNDARIES.md`](./docs/03_SCOPE_AND_BOUNDARIES.md) | **范围与边界**：当前 MVP 做什么、不做什么？与后续全栈演进的刚性边界隔离 | 当前 Core 规格 |
| [`docs/04_DATA_CONTRACTS.md`](./docs/04_DATA_CONTRACTS.md) | **数据契约**：模块间传递什么数据？强类型 Pydantic 模型与字段约束 | 当前 Core 规格 |
| [`docs/05_DETECTION_RULES.md`](./docs/05_DETECTION_RULES.md) | **检测规则**：如何判定攻击？9 项核心条件、毛收益信号口径与评测标准 | 当前 Core 规格 |
| [`STRATEGIC_ANALYSIS.md`](./STRATEGIC_ANALYSIS.md) | **项目战略分析**：华为“五看三定”行业洞察、竞争壁垒、战略控制点与演进路线 | 结课考核项(5) |

---

## 许可证 (License)

本项目遵循 [Apache License 2.0](./LICENSE) 开放源代码，允许商业与学术用途，并附带明确的专利授权保护条款。
