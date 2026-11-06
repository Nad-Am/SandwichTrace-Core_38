# 4. DATA_CONTRACTS.md —— 数据契约

## 4.1 Fixture 结构

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

其中：

- input：提供给检测引擎的标准化输入。
- ground_truth：仅供评测模块使用的人工标注数据。

## 4.2 Transaction

```python
class Transaction(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str | None
    tx_index: int
    status: int
```

字段约束：

- tx_hash：交易哈希。
- from_address：交易发起者。
- to_address：交易目标地址。
- tx_index：区块内交易顺序。
- status：交易执行状态。

当前只处理 status = 1 的成功交易。

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

字段约束：

- pool_address：流动性池地址。
- token_in / token_out：标准化后的输入、输出资产。
- amount_in / amount_out：原始最小单位整数。
- actor：关联 Transaction.from_address 后得到的交易发起者。
- sender：Swap 事件原始 sender。
- recipient：Swap 事件原始 recipient。
- tx_hash：所属交易哈希。
- block_number：所属区块。
- tx_index：区块内交易索引。
- log_index：交易回执中的日志索引。

注意：真实 Uniswap V2 Swap 事件包含 amount0In、amount1In、amount0Out、amount1Out。需要结合 token0/token1 关系解析出标准化的 token_in、token_out、amount_in、amount_out。

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

该契约作为可选扩展保留。

当前不要求实现储备状态重建，也不能将区块级快照解释为同一区块内每笔交易执行前后的精确状态。

## 4.5 DetectionInput

```python
class DetectionInput(BaseModel):
    block: Block
    transactions: list[Transaction]
    swap_events: list[SwapEvent]
    pool_snapshots: list[PoolSnapshot] = Field(default_factory=list)
```

DetectionInput 是 DetectionEngine 的统一输入。

Ground Truth 不属于 DetectionInput。

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

每个 SandwichMatch 表示一个独立的攻击候选命中。

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

约束：

- 一次检测任务允许存在多个攻击命中。
- matches 保存全部三联体。
- total_matches 应由 matches 数量派生。
- is_sandwich 应由 matches 是否为空派生。
- reasons 归属于具体 SandwichMatch，而不是整个 DetectionResult。
- base_token 和 quote_token 说明交易方向及毛收益的计量资产。
- price_impact_confirmed 使用三态语义：true 表示验证通过，false 表示存在数据但验证失败，null 表示没有执行价格影响验证。

## 4.8 VerifierConfig

```python
@dataclass(frozen=True)
class VerifierConfig:
    min_gross_profit: int = 1
    enable_price_impact: bool = False
    min_price_impact_bps: int = 0
```

当前只需要简单配置，不引入复杂规则配置系统。

min_gross_profit 表示毛收益信号阈值，不代表净利润门槛。

价格影响阈值使用整数 basis points（bps），避免在金额和价格规则中混用浮点数。

## 4.9 PoolSnapshot 位置语义

MVP 仅定义以下快照位置：

```text
SnapshotPosition.BLOCK_START
```

快照表示区块执行前、目标 Pool 的储备状态。由于当前价格影响验证尚未参与核心判定，该快照不会阻塞检测流程。未来增加区块中途快照时，应扩展 `tx_hash` 或 `log_index` 字段。
