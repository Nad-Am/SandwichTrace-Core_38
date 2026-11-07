# 2. ARCHITECTURE.md — Architecture Design

> **English** | [简体中文](../zh-CN/02_ARCHITECTURE.md)

## 2.1 Architectural Positioning

`SandwichTrace-Core_38` adopts a six-layer modular architecture that strictly decouples core detection algorithms from dataset loading, CLI interaction, and benchmark evaluation.

The system operates as an offline Python detection kernel with zero dependency on web frontends, HTTP APIs, external databases, or live RPC nodes.

## 2.2 Six-Layer Architecture

The codebase is organized into six layers:

1. **CLI**: Command-line entry point and argument parsing.
2. **Application**: Workflow orchestration.
3. **Core**: Pure sandwich attack detection pipeline.
4. **Contracts**: Strongly typed Pydantic data contracts.
5. **Dataset**: Fixture loading, actor resolution, and input assembly.
6. **Evaluation**: Ground-truth comparison and metric aggregation.

## 2.3 Module Responsibilities

### CLI (`cli.py`)

Parses user commands and formats output streams:

- `replay`: Runs a single fixture through the detection pipeline.
- `evaluate`: Evaluates a fixture directory or manifest and outputs aggregate metrics.

The CLI contains no detection logic.

### Application (`application/`)

Coordinates dataset loading and engine execution:

- `detect_fixture(path)`: Loads a fixture and runs detection on its `DetectionInput`.
- `detect(input)`: Executes detection directly on a validated `DetectionInput`.

### Core (`core/detector/`)

The pure algorithmic detection layer:

- `candidate.py`: Filters valid swap events and groups candidates by pool.
- `matcher.py`: Searches ordered non-adjacent `A/B/C` triplets and deduplicates matches.
- `verifier.py`: Validates core sandwich invariants and computes the gross profit signal.
- `engine.py`: Orchestrates candidate selection, matching, and verification into a `DetectionResult`.

`Core` depends exclusively on `Contracts`. It never reads files, parses JSON, queries RPC endpoints, or accesses Ground Truth labels.

### Contracts (`contracts/`)

Defines shared, immutable Pydantic models across layers:

- `Block`
- `Transaction`
- `SwapEvent`
- `PoolSnapshot`
- `DetectionInput`
- `SandwichMatch`
- `DetectionResult`
- `VerifierConfig`
- `RuleVersion`

### Dataset (`dataset/`)

Responsible for:

- Reading and validating JSON fixture files and manifests.
- Resolving each swap's `actor` from `Transaction.from_address`.
- Separating `ground_truth` from `DetectionInput`.
- Assembling validated `DetectionInput` instances.

`Ground Truth` is exposed only to `Evaluation` and is never passed into `Core`.

### Evaluation (`evaluation/`)

Responsible for:

- Invoking `Application` across a fixture set.
- Comparing predicted triplets against `Ground Truth` identities.
- Computing `TP`, `FP`, `FN`, `Precision`, `Recall`, and `F1`.
- Rendering structured JSON evaluation reports.

## 2.4 Dependency Graph

```text
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

Core dependency invariants:

- `Core` does not depend on `Dataset`, `CLI`, or `Evaluation`.
- `Core` has zero access to `Ground Truth`.
- `Dataset` normalizes raw JSON fixtures into `DetectionInput`.
- `Evaluation` consumes `DetectionService.detect(input)` without bypassing the pipeline.

## 2.5 Detection Data Flow

```text
Local JSON Fixture
       │
       ▼
Dataset Loader
       │
       ├── Parse Block
       ├── Parse Transaction
       ├── Parse SwapEvent
       └── Resolve Actor (Transaction.from_address -> SwapEvent.actor)
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
       ├── Candidate Filtering
       ├── Triplet Matching
       └── Rule Verification
       │
       ▼
DetectionResult
       │
       ▼
CLI JSON Output / Evaluation Report
```

## 2.6 Directory Layout

```text
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
├── STRATEGIC_ANALYSIS.md
├── docs/
│   ├── en/
│   │   ├── 01_DESIGN_BACKGROUND.md
│   │   ├── 02_ARCHITECTURE.md
│   │   ├── 03_SCOPE_AND_BOUNDARIES.md
│   │   ├── 04_DATA_CONTRACTS.md
│   │   └── 05_DETECTION_RULES.md
│   └── zh-CN/
│       ├── 01_DESIGN_BACKGROUND.md
│       ├── 02_ARCHITECTURE.md
│       ├── 03_SCOPE_AND_BOUNDARIES.md
│       ├── 04_DATA_CONTRACTS.md
│       └── 05_DETECTION_RULES.md
├── LICENSE
└── pyproject.toml
```

## 2.7 Execution & Boundary Guarantees

- `CLI` invokes detection exclusively via `application.detection_service`.
- `Application` loads fixtures, strips Ground Truth, and calls `DetectionEngine`.
- `Engine` orchestrates `Candidate`, `Matcher`, and `Verifier` to produce `DetectionResult`.
- `Evaluation` obtains predictions solely via `DetectionService.detect(input)`.
- Cross-layer payloads are enforced by frozen Pydantic V2 models in `contracts/`.
- `DetectionResult.matches` supports zero, one, or multiple `SandwichMatch` records per block.
