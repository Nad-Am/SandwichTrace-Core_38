from pathlib import Path

from contracts.config import VerifierConfig
from contracts.detection_input import DetectionInput
from contracts.detection_result import DetectionResult
from core.detector.engine import DetectionEngine
from dataset.loader import load_fixture


class DetectionService:
    """Application boundary for CLI, evaluation and future API adapters."""

    def __init__(self, config: VerifierConfig | None = None) -> None:
        self.engine = DetectionEngine(config)

    def detect_fixture(self, fixture_path: str | Path) -> DetectionResult:
        fixture = load_fixture(fixture_path)
        return self.detect(fixture.input)

    def detect(self, detection_input: DetectionInput) -> DetectionResult:
        return self.engine.detect(detection_input)

