# 3. SCOPE_AND_BOUNDARIES.md —— 范围与边界控制

## 3.1 当前 MVP 范围

| 维度 | 当前支持 |
| --- | --- |
| 区块链 | Ethereum |
| DEX 模型 | Uniswap V2 风格 |
| 检测范围 | 单个流动性池 |
| 交易范围 | 同一区块 |
| 攻击模式 | 典型 Front-run / Victim / Back-run |
| 交易路由 | 单跳 |
| 攻击者归因 | 同一个交易发起者 EOA |
| 输入方式 | 本地 JSON Fixture |
| 收益指标 | Quote Token 毛收益信号 |
| 运行方式 | Python CLI |

## 3.2 暂不支持的能力

当前不实现：

- 多 Pool 跨池攻击。
- 多跳交易路由。
- 多地址协同攻击。
- 跨区块攻击关联。
- Mempool 实时监控。
- 实时 RPC 数据采集。
- Trace 自动获取与完整证据溯源。
- 净利润计算。
- Reorg 检测和结果回滚。
- FastAPI 服务。
- Vue 前端。
- 交易拦截和资金追回。

这些能力属于后续平台化扩展方向，不属于当前 MVP 的范围。

## 3.3 关键边界约束

### 数据边界

Core 只能处理已经标准化的 Python 数据对象。

原始 JSON 解析、Pydantic 校验和交易事件关联由 Dataset 负责。

### 算法边界

当前算法识别的是符合预定义条件的典型三联体，不等同于识别所有可能存在的三明治攻击。

### 身份归因边界

攻击者通过 Front-run 和 Back-run 两笔交易的 Transaction.from_address 一致性进行归因。

不将 SwapEvent.sender 直接视为攻击者。

当前方法不覆盖代理合约、多 EOA 协同和复杂账户抽象场景。

### 收益边界

当前计算的是 Quote Token 毛收益信号，不是攻击者最终净利润，也不是受害者损失。

不扣除 Gas、手续费、其他资金成本。

### 价格影响边界

PoolSnapshot 可以作为可选输入契约保留。

但核心检测不依赖 PoolSnapshot，也不把价格影响作为攻击成立的必要条件。

缺少价格快照表示未验证，不表示验证失败。

## 3.4 当前与未来能力的隔离

未来扩展真实链上数据时，应通过数据采集与适配层，将 RPC、Receipt、Trace 等数据转换成现有 Contracts 定义的标准输入。

不应将 RPC 请求、链上数据解析或数据库访问直接塞进 Core。
