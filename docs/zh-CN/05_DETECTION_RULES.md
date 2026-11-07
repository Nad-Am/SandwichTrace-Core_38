# 5. DETECTION_RULES.md —— 检测规则

> [English](../en/05_DETECTION_RULES.md) | **????**

## 5.1 典型攻击模式

```
A：攻击者使用 Quote Token 买入 Base Token

B：受害者使用 Quote Token 买入 Base Token

C：攻击者卖出 Base Token，换回 Quote Token
```

## 5.2 核心判定条件

一组交易 A、B、C 需要满足：

1. A、B、C 属于同一个流动性池。
2. A、B、C 位于同一个区块。
3. A、B、C 满足 A < B < C 的执行顺序。
4. A 与 C 的交易发起者相同。
5. B 的交易发起者与 A 不同。
6. A 与 B 的交易方向相同。
7. C 的交易方向与 A、B 相反。
8. A 的输入资产与 C 的输出资产相同。
9. C 的 Quote Token 输出数量大于 A 的 Quote Token 输入数量。

## 5.3 毛收益信号

```
gross_profit_signal = amount_out_C - amount_in_A
```

计算前必须确认：

- A 的输入资产与 C 的输出资产为同一种 Quote Token。
- 金额均采用同一资产的原始最小单位。
- 不使用浮点数进行金额比较。

该指标仅代表攻击者首尾交易之间的 Quote Token 毛收益信号。

它不等于扣除 Gas 和其他成本后的净利润，也不等于受害者实际损失。

## 5.4 交易匹配与去重

匹配过程需要：

- 按 Pool 分组。
- 按区块内交易顺序排序。
- 预筛选买入和卖出方向。
- 搜索可能的 A/B/C 组合。
- 对匹配结果去重。

不能通过简单限制 A、B、C 之间最多相隔 K 笔交易来优化性能，因为无关交易可能合法地夹在三笔攻击交易之间。

当前 MVP 优先采用按 Pool 分组后的候选匹配策略，避免直接使用全量三重循环。

不同语义需要区分：

- 资源限制：限制单次运行允许搜索的候选数量，用于防止异常输入耗尽资源。
- 检测窗口：限制 A、B、C 之间允许间隔的交易数量，属于检测语义。

MVP 不设置固定交易间隔限制，因为无关交易可以合法地出现在三笔攻击交易之间。如未来增加资源保护，应明确告警或报错，不能静默丢弃仍可能有效的候选。

## 5.5 命中原因

当前规则使用以下稳定原因代码：

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

核心检测结果只要求前七项。价格影响原因属于可选增强证据。

## 5.6 规则版本

当前使用：

```python
class RuleVersion(str, Enum):
    V1 = "v1"
```

检测结果应记录 rule_version，以保证后续规则迭代时检测结果可追溯。

## 5.7 评测口径

使用完整三联体进行匹配，而不是只判断单笔交易是否命中。

攻击标识：

```python
attack_id = (
    pool_address,
    attacker,
    front_tx_hash,
    victim_tx_hash,
    back_tx_hash,
)
```

指标：

- TP：预测三联体与 Ground Truth 完全一致。
- FP：预测出不存在于 Ground Truth 的三联体。
- FN：Ground Truth 中存在但未预测出的三联体。

```
Precision = TP / (TP + FP)

Recall = TP / (TP + FN)

F1 = 2 * Precision * Recall / (Precision + Recall)
```

空分母时返回 0.0，同时保留 TP、FP、FN 原始计数。

Ground Truth 仅用于 Evaluation，不得参与 DetectionEngine 的检测决策。
