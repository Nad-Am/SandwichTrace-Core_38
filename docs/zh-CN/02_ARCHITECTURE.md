# 2. ARCHITECTURE.md —— 架构设计

> [English](../en/02_ARCHITECTURE.md) | **????**

## 2.1 架构定位

SandwichTrace-Core_38 采用分层模块化架构，核心检测逻辑与数据加载、命令行交互、评测流程解耦。

当前系统是一个离线运行的 Python 检测内核，不依赖前端、Web API、数据库或实时 RPC 服务。

## 2.2 总体架构

系统划分为六个层次：

1. CLI：命令行交互入口。
2. Application：应用流程编排。
3. Core：攻击检测核心算法。
4. Contracts：统一数据契约。
5. Dataset：测试数据加载与组装。
6. Evaluation：检测结果评估。

## 2.3 模块职责

### CLI

负责接收用户命令、解析参数和输出结果。

当前支持：

- replay：对指定 Fixture 执行检测。
- evaluate：对数据集执行批量评测。

CLI 不直接实现检测算法。

### Application

负责协调数据加载与检测引擎。

主要接口：

- detect_fixture(path)：加载 Fixture 并执行检测。
- detect(input)：接收标准化 DetectionInput 并执行检测。

Application 不参与具体攻击判定。

### Core

系统的核心检测层。

主要模块：

- candidate.py：候选交易筛选。
- matcher.py：攻击三联体匹配。
- verifier.py：攻击条件验证。
- engine.py：统一组织检测流程并生成检测结果。

Core 只依赖 Contracts，不读取 JSON、不访问文件、不调用 RPC，也不接触 Ground Truth。

### Contracts

定义各模块之间共享的数据结构，包括：

- Block
- Transaction
- SwapEvent
- PoolSnapshot
- DetectionInput
- SandwichMatch
- DetectionResult
- VerifierConfig
- RuleVersion

Contracts 不承担业务流程编排。

### Dataset

负责：

- JSON Fixture 文件读取。
- Pydantic 数据校验。
- Transaction 与 SwapEvent 关联。
- 标注数据 Ground Truth 加载。
- 标准化 DetectionInput 组装。

Ground Truth 只提供给 Evaluation，不传入 Core。

### Evaluation

负责：

- 批量调用 Application。
- 获取 Ground Truth。
- 对比预测结果和标注结果。
- 计算 TP、FP、FN、Precision、Recall、F1。
- 输出评测报告。

## 2.4 模块依赖关系

```
CLI
 │
 ▼
Application
 ├──────────────► Core
 │                  │
 │                  ▼
 │              Contracts
 │
 └──────────────► Dataset
                    │
                    ▼
                 Contracts

Evaluation
 ├──────────────► Application
 ├──────────────► Dataset
 └──────────────► Contracts
```

核心依赖约束：

- Core 不依赖 Dataset。
- Core 不依赖 CLI。
- Core 不依赖 Evaluation。
- Core 不读取 Ground Truth。
- Dataset 负责将原始 Fixture 转换为标准化输入。
- Evaluation 负责评测，不参与检测逻辑。

## 2.5 检测数据流

```
本地 JSON Fixture
       │
       ▼
Dataset Loader
       │
       ├── 解析 Block
       ├── 解析 Transaction
       ├── 解析 SwapEvent
       └── 关联交易与事件
       │
       ▼
DetectionInput
       │
       ▼
Application Service
       │
       ▼
DetectionEngine
       │
       ├── Candidate 筛选
       ├── Matcher 匹配
       └── Verifier 验证
       │
       ▼
DetectionResult
       │
       ▼
CLI JSON 输出 / Evaluation 评测
```

## 2.6 目录结构

```
SandwichTrace-Core_38/
├── cli.py
├── application/
│   └── detection_service.py
├── core/
│   └── detector/
│       ├── candidate.py
│       ├── matcher.py
│       ├── verifier.py
│       └── engine.py
├── contracts/
│   ├── block.py
│   ├── transaction.py
│   ├── swap_event.py
│   ├── pool_snapshot.py
│   ├── detection_input.py
│   ├── detection_result.py
│   ├── sandwich_match.py
│   ├── enums.py
│   └── config.py
├── dataset/
│   ├── loader.py
│   ├── assemble.py
│   ├── manifest.json
│   └── fixtures/
│       ├── attacks/
│       ├── normal/
│       └── boundary/
├── evaluation/
│   ├── runner.py
│   ├── metrics.py
│   └── report.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── docs/
│   ├── 01_DESIGN_BACKGROUND.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_SCOPE_AND_BOUNDARIES.md
│   ├── 04_DATA_CONTRACTS.md
│   └── 05_DETECTION_RULES.md
├── LICENSE
└── pyproject.toml
```

## 2.7 可执行模块与依赖约束

- CLI 通过 `application.detection_service` 调用检测流程。
- Application 负责加载 Fixture、拆分 Ground Truth 和调用 Engine。
- Engine 通过 Candidate、Matcher、Verifier 生成 `DetectionResult`。
- Evaluation 仅通过 Application 的 `detect(input)` 入口获取预测结果。
- 所有跨层数据使用 `contracts/` 下的 Pydantic 模型。
- `DetectionResult.matches` 支持零个、一个或多个 `SandwichMatch`。
