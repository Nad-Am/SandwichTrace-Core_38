# 5. DETECTION_RULES.md — Detection Rules

> **English** | [简体中文](../zh-CN/05_DETECTION_RULES.md)

## 5.1 Canonical Sandwich Pattern

```text
A (Front-run) : Attacker swaps Quote Token -> Base Token
B (Victim)    : Victim swaps Quote Token   -> Base Token
C (Back-run)  : Attacker swaps Base Token  -> Quote Token
```

## 5.2 Nine Core Verification Conditions

A candidate swap triplet `(A, B, C)` is verified as a sandwich attack if and only if all 9 conditions hold:

1. `A`, `B`, and `C` occur in the **same liquidity pool** (`pool_address`).
2. `A`, `B`, and `C` belong to the **same block** (`block_number`).
3. `A`, `B`, and `C` strictly satisfy intra-block execution order `A < B < C` (`(tx_index, log_index)`).
4. `A` and `C` share the **same initiating actor** (`A.actor == C.actor`).
5. `B` has a **distinct initiating actor** from `A` (`B.actor != A.actor`).
6. `A` and `B` execute in the **same trade direction** (`A.token_in == B.token_in` and `A.token_out == B.token_out`).
7. `C` executes in the **exact opposite direction** (`C.token_in == A.token_out` and `C.token_out == A.token_in`).
8. `A`'s input asset matches `C`'s output asset (the **Quote Token**).
9. `C`'s Quote Token output strictly exceeds `A`'s Quote Token input (`C.amount_out - A.amount_in >= min_gross_profit`).

## 5.3 Gross Profit Signal

```text
gross_profit_signal = amount_out_C - amount_in_A
```

Preconditions for computation:

- `A.token_in` and `C.token_out` refer to the exact same Quote Token address.
- Both amounts are expressed in raw minimal integer units (`int`).
- Floating-point arithmetic is never used for token accounting.

This metric captures the attacker's gross Quote Token delta between the front-run and back-run swaps; it does not deduct Gas costs or builder tips, nor does it equal the victim's slippage loss.

## 5.4 Triplet Matching & Deduplication

The matching pipeline performs:

1. Per-pool candidate grouping.
2. Deterministic sorting by `(tx_index, log_index)`.
3. Directional pre-filtering across ordered `A/B/C` combinations.
4. Structural and profit verification.
5. Canonical deduplication by attack identity.

**Why non-adjacent matching is required**: Unrelated transfers or swaps on other pools can legitimately occur between `A`, `B`, and `C` within the same block. Therefore, the matcher does not impose an arbitrary fixed `K`-transaction distance window that would silently drop valid non-adjacent attacks.

## 5.5 Explainable Reason Codes

Each verified match emits deterministic `DetectionReason` codes:

```text
SAME_POOL
ORDER_VALID
ATTACKER_CONSISTENT
VICTIM_DISTINCT
DIRECTION_MATCHED
QUOTE_TOKEN_MATCHED
POSITIVE_GROSS_PROFIT
PRICE_IMPACT_CONFIRMED
PRICE_IMPACT_NOT_CONFIRMED
```

The first seven codes correspond to the mandatory core invariants; the final two represent optional price-impact evidence when `enable_price_impact` is active.

## 5.6 Rule Versioning

```python
class RuleVersion(str, Enum):
    V1 = "v1"
```

Every `DetectionResult` records `rule_version` so outputs remain auditable across future rule iterations.

## 5.7 Evaluation Metrics

Evaluation compares full 5-tuple attack identities rather than isolated transactions:

```python
attack_id = (
    pool_address,
    attacker,
    front_tx_hash,
    victim_tx_hash,
    back_tx_hash,
)
```

Metrics:

- **TP (True Positives)**: Predicted triplets present in `ground_truth`.
- **FP (False Positives)**: Predicted triplets absent from `ground_truth`.
- **FN (False Negatives)**: `ground_truth` triplets missed by the detector.

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 * Precision * Recall / (Precision + Recall)
```

Zero denominators safely evaluate to `0.0` while preserving raw `TP`, `FP`, and `FN` counts. `ground_truth` is strictly isolated to `evaluation/` and never enters `DetectionEngine`.
