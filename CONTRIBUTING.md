# Contributing / 贡献指南

> [English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>
## English

### Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

### Branch Workflow

Use short-lived feature or fix branches and keep `main` runnable at all times:

```text
feat/contracts
feat/candidate-matcher
feat/verifier-engine
fix/evaluate-fixture-validation
docs/i18n-en
docs/i18n-zh-cn
```

Each branch should address a clearly scoped task or Issue and be merged into `main`. A Pull Request should include:

- Summary of behavior or documentation changes;
- Tests added or updated;
- Verification commands executed locally;
- Any remaining MVP scope boundaries.

### Pull Request Checklist

- [ ] `python -m pytest` passes with zero failures.
- [ ] `core/` remains free of file I/O, JSON parsing, RPC calls, and Ground Truth access.
- [ ] `SwapEvent.actor` is derived from `Transaction.from_address`.
- [ ] `gross_profit_signal` is documented as raw Quote Token gross profit.
- [ ] Documentation remains aligned with the current MVP boundaries.

---

<a name="简体中文"></a>
## 简体中文

### 开发环境配置

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

### 分支协作规范

采用短周期特性/修复分支开发，始终保持 `main` 主干处于可运行与测试通过状态：

```text
feat/contracts
feat/candidate-matcher
feat/verifier-engine
fix/evaluate-fixture-validation
docs/i18n-en
docs/i18n-zh-cn
```

每个分支应聚焦于明确的任务或 Issue，并在验证通过后合并入 `main`。提交 Pull Request 时应包含：

- 变更的行为或文档范围说明；
- 新增或更新的测试用例；
- 本地执行的验证命令及输出摘要；
- 当前 MVP 的范围边界说明。

### Pull Request 检查清单

- [ ] `python -m pytest` 全量测试通过。
- [ ] `core/` 保持纯粹，不包含文件读取、JSON 解析、RPC 调用或 Ground Truth 访问。
- [ ] `SwapEvent.actor` 严格由 `Transaction.from_address` 解析关联。
- [ ] `gross_profit_signal` 明确定义为 Quote Token 原始毛收益信号。
- [ ] 文档表述与当前 MVP 代码能力边界严格一致。
