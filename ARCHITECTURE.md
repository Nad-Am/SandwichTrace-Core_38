# Architecture / 架构概览

> [English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>
## English

`SandwichTrace-Core_38` uses a six-layer unidirectional architecture:

```text
CLI -> Application -> Core -> Contracts
                 \-> Dataset
Evaluation -> Application + Dataset + Contracts
```

The implementation enforces strict boundary rules:

- `core/` receives validated `DetectionInput` objects only.
- `core/` never reads files, JSON, Ground Truth, RPC endpoints, or databases.
- `dataset/` resolves swap actors from `Transaction.from_address` before schema validation.
- `evaluation/` invokes `DetectionService.detect(input)` exclusively for predictions.
- `DetectionResult.matches` supports zero, one, or multiple `SandwichMatch` objects per block.

See [docs/en/02_ARCHITECTURE.md](./docs/en/02_ARCHITECTURE.md) for the full specification.

---

<a name="简体中文"></a>
## 简体中文

`SandwichTrace-Core_38` 采用六层单向依赖架构：

```text
CLI -> Application -> Core -> Contracts
                 \-> Dataset
Evaluation -> Application + Dataset + Contracts
```

核心依赖与边界约束如下：

- `core/` 仅接收已完成校验的 `DetectionInput` 强类型对象。
- `core/` 严禁直接读取本地文件、JSON、Ground Truth 标注、RPC 节点或数据库。
- `dataset/` 在契约校验前完成 `Transaction.from_address` 到 `SwapEvent.actor` 的发起者身份关联。
- `evaluation/` 仅通过 `DetectionService.detect(input)` 标准入口获取预测结果。
- `DetectionResult.matches` 支持单区块内零个、一个或多个 `SandwichMatch` 结果。

详细架构规范请参阅 [docs/zh-CN/02_ARCHITECTURE.md](./docs/zh-CN/02_ARCHITECTURE.md)。
