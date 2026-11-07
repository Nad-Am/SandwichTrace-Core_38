# 3. SCOPE_AND_BOUNDARIES.md — Scope & Boundary Control

> **English** | [简体中文](../zh-CN/03_SCOPE_AND_BOUNDARIES.md)

## 3.1 Current MVP Scope

| Dimension | Supported in MVP |
| :--- | :--- |
| **Blockchain** | Ethereum |
| **DEX Model** | Uniswap V2-style constant-product AMM |
| **Pool Scope** | Single liquidity pool per triplet |
| **Block Scope** | Intra-block transactions |
| **Attack Pattern** | Canonical Front-run / Victim / Back-run (`A < B < C`) |
| **Routing** | Single-hop swap |
| **Actor Attribution** | Shared EOA (`Transaction.from_address`) between `A` and `C` |
| **Input Source** | Offline JSON fixtures |
| **Profit Metric** | Quote Token gross profit signal (`amount_out_C - amount_in_A`) |
| **Execution Mode** | Standalone Python CLI |

## 3.2 Out-of-Scope Capabilities (Deferred to Roadmap)

The current MVP intentionally excludes:

- Cross-pool or multi-hop arbitrage/sandwich routing.
- Multi-EOA or sybil-coordinated attacker attribution.
- Multi-block sandwich correlation.
- Live Mempool monitoring or transaction interception.
- Live RPC block/log streaming.
- Automated call-trace extraction and full forensic proof chains.
- Net profit accounting (deducting Gas, bribes, or builder tips).
- Chain reorganization (Reorg) state machine rollbacks.
- FastAPI web services and Vue frontends.

These capabilities belong to the broader platform roadmap and are strictly isolated from the offline detection kernel.

## 3.3 Core Boundary Constraints

### Data Boundary

`Core` accepts only validated `DetectionInput` Python objects. Raw JSON parsing, schema validation, and transaction-to-event correlation are handled strictly by `Dataset`.

### Algorithmic Boundary

The detector identifies canonical triplets satisfying explicit structural invariants; it does not claim to capture generalized multi-hop or cross-contract MEV strategies.

### Actor Attribution Boundary

Attacker identity is attributed by matching `Transaction.from_address` across the front-run (`A`) and back-run (`C`) transactions, rather than relying on `SwapEvent.sender` (which is typically a router contract). Proxy contracts, multi-EOA collusion, and account abstraction are outside the MVP attribution model.

### Profit Accounting Boundary

`gross_profit_signal` measures the raw Quote Token delta (`amount_out_C - amount_in_A`) in minimal integer units. It represents neither the attacker's net profit after Gas/bribes nor the victim's exact financial loss.

### Price-Impact Boundary

`PoolSnapshot` is retained as an optional contract extension. Core detection does not require `PoolSnapshot`, nor is price-impact confirmation a mandatory precondition for a match. Absence of reserve snapshots yields `price_impact_confirmed = None` (unverified) rather than verification failure.

## 3.4 Isolation Between Core and Future Platform Layers

When integrating live on-chain data in future iterations, an external ingestion/adapter layer must normalize RPC blocks, receipts, and traces into the existing `Contracts` schemas. Network I/O, RPC clients, and database persistence must never be embedded into `Core`.
