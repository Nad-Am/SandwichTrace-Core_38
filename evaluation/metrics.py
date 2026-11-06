from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict

AttackIdentity = tuple[str, str, str, str, str]


class MetricsResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


def metrics_from_counts(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
) -> MetricsResult:
    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives
    precision = (
        true_positives / precision_denominator
        if precision_denominator
        else 0.0
    )
    recall = (
        true_positives / recall_denominator if recall_denominator else 0.0
    )
    f1_denominator = precision + recall
    f1 = 2 * precision * recall / f1_denominator if f1_denominator else 0.0
    return MetricsResult(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def compare_attack_sets(
    predicted: Iterable[AttackIdentity],
    expected: Iterable[AttackIdentity],
) -> MetricsResult:
    predicted_set = set(predicted)
    expected_set = set(expected)
    true_positives = len(predicted_set & expected_set)
    false_positives = len(predicted_set - expected_set)
    false_negatives = len(expected_set - predicted_set)
    return metrics_from_counts(true_positives, false_positives, false_negatives)

