from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from application.detection_service import DetectionService
from contracts.detection_result import DetectionResult
from dataset.loader import (
    ExpectedMatch,
    Fixture,
    discover_fixtures,
    load_fixture,
)
from evaluation.metrics import (
    AttackIdentity,
    MetricsResult,
    compare_attack_sets,
    metrics_from_counts,
)


class FixtureEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    fixture_id: str
    description: str
    detection: DetectionResult
    expected_matches: list[ExpectedMatch]
    metrics: MetricsResult


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metrics: MetricsResult
    fixtures: list[FixtureEvaluation]


class EvaluationRunner:
    def __init__(self, service: DetectionService | None = None) -> None:
        self.service = service or DetectionService()

    def evaluate_fixtures(self, fixture_paths: Iterable[str | Path]) -> EvaluationReport:
        results: list[FixtureEvaluation] = []
        total_tp = 0
        total_fp = 0
        total_fn = 0

        for fixture_path in fixture_paths:
            fixture = load_fixture(fixture_path)
            result = self.evaluate_fixture(fixture)
            results.append(result)
            total_tp += result.metrics.true_positives
            total_fp += result.metrics.false_positives
            total_fn += result.metrics.false_negatives

        return EvaluationReport(
            metrics=metrics_from_counts(total_tp, total_fp, total_fn),
            fixtures=results,
        )

    def evaluate_dataset(self, dataset_root: str | Path) -> EvaluationReport:
        return self.evaluate_fixtures(discover_fixtures(dataset_root))

    def evaluate_fixture(self, fixture: Fixture) -> FixtureEvaluation:
        detection = self.service.detect(fixture.input)
        predicted: list[AttackIdentity] = [
            match.identity() for match in detection.matches
        ]
        expected: list[AttackIdentity] = [
            match.identity() for match in fixture.ground_truth.expected_matches
        ]
        return FixtureEvaluation(
            fixture_id=fixture.fixture_id,
            description=fixture.description,
            detection=detection,
            expected_matches=fixture.ground_truth.expected_matches,
            metrics=compare_attack_sets(predicted, expected),
        )

