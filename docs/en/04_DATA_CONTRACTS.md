# 4. DATA_CONTRACTS.md — Data Contracts

> **English** | [简体中文](../zh-CN/04_DATA_CONTRACTS.md)

## 4.1 Fixture Structure

```json
{
  "input": {
    "block": {},
    "transactions": [],
    "swap_events": [],
    "pool_snapshots": []
  },
  "ground_truth": {
    "expected_matches": []
  }
}
```

- `input`: Normalized block, transaction, and swap payload supplied to the detection engine.
- `ground_truth`: Labeled expected matches consumed exclusively by the evaluation runner.

## 4.2 Transaction

```python
class Transaction(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str | None
    tx_index: int
    status: int
```

Field constraints:

- `tx_hash`: Transaction hash.
- `from_address`: Initiating EOA address.
- `to_address`: Target contract or recipient address.
- `tx_index`: Intra-block execution index (`>= 0`).
- `status`: Execution status (`1` for succeeded, `0` for reverted).

Only succeeded transactions (`status == 1`) are eligible for candidate selection.

## 4.3 SwapEvent

```python
class SwapEvent(BaseModel):
    pool_address: str

    token_in: str
    token_out: str

    amount_in: int
    amount_out: int

    actor: str
    sender: str
    recipient: str

    tx_hash: str
    block_number: int
    tx_index: int
    log_index: int
```

Field constraints:

- `pool_address`: Target AMM liquidity pool address.
- `token_in` / `token_out`: Normalized input and output token addresses.
- `amount_in` / `amount_out`: Positive integer amounts in minimal token units (`wei`).
- `actor`: Initiating EOA resolved from `Transaction.from_address`.
- `sender`: Raw `sender` field emitted by the Uniswap V2 `Swap` event.
- `recipient`: Raw `to` / recipient field emitted by the `Swap` event.
- `tx_hash`: Enclosing transaction hash.
- `block_number`: Enclosing block number.
- `tx_index`: Enclosing transaction index within the block.
- `log_index`: Event log index within the receipt.

*Note: Raw Uniswap V2 `Swap` logs emit `amount0In`, `amount1In`, `amount0Out`, and `amount1Out`, which are normalized against pool `token0`/`token1` into directional `token_in`, `token_out`, `amount_in`, and `amount_out`.*

## 4.4 PoolSnapshot

```python
class PoolSnapshot(BaseModel):
    pool_address: str
    token0: str
    token1: str
    reserve0: int
    reserve1: int
    block_number: int
```

Retained as an optional contract extension. The MVP does not require intra-block reserve state reconstruction, and block-level snapshots must not be conflated with exact pre-swap reserves for arbitrary intra-block transactions.

## 4.5 DetectionInput

```python
class DetectionInput(BaseModel):
    block: Block
    transactions: list[Transaction]
    swap_events: list[SwapEvent]
    pool_snapshots: list[PoolSnapshot] = Field(default_factory=list)
```

`DetectionInput` is the sole input contract accepted by `DetectionEngine`. `ground_truth` is strictly excluded from `DetectionInput`.

## 4.6 SandwichMatch

```python
class SandwichMatch(BaseModel):
    pool_address: str
    attacker: str
    victim: str

    front_tx_hash: str
    victim_tx_hash: str
    back_tx_hash: str

    base_token: str
    quote_token: str
    gross_profit_signal: int
    price_impact_confirmed: bool | None = None
    reasons: list[DetectionReason]
```

Each `SandwichMatch` represents a single verified sandwich triplet within the block.

## 4.7 DetectionResult

```python
class DetectionResult(BaseModel):
    rule_version: str
    block_number: int
    block_hash: str

    matches: list[SandwichMatch]

    total_matches: int
    is_sandwich: bool
```

Invariants:

- A single block detection run may yield zero, one, or multiple `SandwichMatch` items.
- `total_matches` is derived directly from `len(matches)`.
- `is_sandwich` is derived from `total_matches > 0`.
- `reasons` are attached to each individual `SandwichMatch` rather than aggregated at the block level.
- `base_token` and `quote_token` denote the intermediate asset and the profit-accounting asset, respectively.
- `price_impact_confirmed` uses tri-state semantics: `True` (confirmed), `False` (snapshot present but below threshold), or `None` (not evaluated).

## 4.8 VerifierConfig

```python
@dataclass(frozen=True)
class VerifierConfig:
    min_gross_profit: int = 1
    enable_price_impact: bool = False
    min_price_impact_bps: int = 0
```

- `min_gross_profit`: Minimum positive Quote Token gross profit signal in raw integer units.
- `min_price_impact_bps`: Price-impact threshold expressed in integer basis points (`bps`), avoiding floating-point precision drift.

## 4.9 PoolSnapshot Position Semantics

The MVP defines:

```text
SnapshotPosition.BLOCK_START
```

This represents pool reserves at the start of the block prior to transaction execution. Future support for mid-block reserve states should extend snapshot positioning with `tx_hash` or `log_index`.
