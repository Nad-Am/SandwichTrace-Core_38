from pathlib import Path

from application.detection_service import DetectionService
from core.detector.engine import DetectionEngine
from dataset.loader import load_fixture
from tests.helpers import make_input, make_sandwich_swaps

FIXTURES = Path(__file__).resolve().parents[2] / "dataset" / "fixtures"


def test_engine_detects_standard_sandwich() -> None:
    result = DetectionEngine().detect(make_input(*make_sandwich_swaps()))

    assert result.is_sandwich is True
    assert result.total_matches == 1
    assert result.matches[0].gross_profit_signal == 25


def test_engine_returns_empty_result_for_noise() -> None:
    result = DetectionEngine().detect(
        make_input(*make_sandwich_swaps()[:1])
    )

    assert result.is_sandwich is False
    assert result.matches == []


def test_service_changes_claim_identity() -> None:
    fixture = FIXTURES / "boundary" / "no_gross_profit.json"
    result = DetectionService().detect_fixture(fixture)

    assert result.is_sandwich is False


def test_multi_match_fixture_returns_all_matches() -> None:
    fixture = load_fixture(
        FIXTURES / "attacks" / "attack_multiple_pools.json"
    )
    result = DetectionEngine().detect(fixture.input)

    assert result.total_matches == 2

