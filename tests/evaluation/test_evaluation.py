from pathlib import Path

from evaluation.metrics import compare_attack_sets, metrics_from_counts
from evaluation.runner import EvaluationRunner

ROOT = Path(__file__).resolve().parents[2]


def test_metrics_use_zero_for_empty_denominators() -> None:
    metrics = metrics_from_counts(0, 0, 0)

    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_compare_attack_sets_calculates_tp_fp_fn() -> None:
    expected = {
        ("pool", "attacker", "a", "b", "c"),
        ("pool", "attacker", "a2", "b2", "c2"),
    }
    predicted = {
        ("pool", "attacker", "a", "b", "c"),
        ("pool", "attacker", "wrong", "b", "c"),
    }
    metrics = compare_attack_sets(predicted, expected)

    assert metrics.true_positives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5


def test_evaluation_runner_reaches_full_recall_on_curated_fixtures() -> None:
    report = EvaluationRunner().evaluate_dataset(ROOT / "dataset" / "fixtures")

    assert len(report.fixtures) == 9
    assert report.metrics.true_positives == 4
    assert report.metrics.false_positives == 0
    assert report.metrics.false_negatives == 0
    assert report.metrics.precision == 1.0
    assert report.metrics.recall == 1.0
    assert report.metrics.f1 == 1.0

