# Contributing

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Branch Workflow

Use short-lived feature branches and keep `main` runnable:

```text
feat/contracts
feat/candidate-matcher
feat/verifier-engine
test/evaluation-cli
docs/report-assets
```

Each branch should be linked to an Issue and merged through a Pull Request. A Pull Request should include:

- the behavior changed;
- tests added or updated;
- the commands used for verification;
- any remaining MVP boundary.

## Pull Request Checklist

- `python -m pytest` passes.
- `python cli.py replay --fixture dataset/fixtures/attacks/attack_standard.json` works.
- `python cli.py evaluate --dataset dataset/fixtures` works.
- New fixtures include both `input` and `ground_truth`.
- Ground Truth is never passed into `DetectionInput` or the detection core.
- README or design documents are updated when public contracts change.

## Fixture Rules

- Use synthetic data unless a real transaction sample has been verified and documented.
- Keep amounts as raw integers.
- Use `Transaction.from_address` as the swap `actor`.
- Add positive and negative cases for every new rule.

