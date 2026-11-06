# Architecture

SandwichTrace-Core_38 uses a six-layer architecture:

```text
CLI -> Application -> Core -> Contracts
                 \-> Dataset
Evaluation -> Application + Dataset + Contracts
```

The implementation follows these dependency rules:

- `core/` receives validated `DetectionInput` objects only.
- `core/` never reads files, JSON, Ground Truth, RPC or databases.
- `dataset/` resolves swap actors from `Transaction.from_address` before validation.
- `evaluation/` uses only `DetectionService.detect(input)` for predictions.
- `DetectionResult.matches` supports zero, one or multiple `SandwichMatch` objects.

See [docs/02_ARCHITECTURE.md](docs/02_ARCHITECTURE.md) for the detailed design.

