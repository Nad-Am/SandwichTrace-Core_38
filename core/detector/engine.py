from collections.abc import Iterable

from contracts.config import VerifierConfig
from contracts.detection_input import DetectionInput
from contracts.detection_result import DetectionResult
from contracts.enums import RuleVersion
from contracts.sandwich_match import SandwichMatch
from core.detector.candidate import CandidateSelector
from core.detector.matcher import SandwichMatcher, SwapTriplet
from core.detector.verifier import SandwichVerifier


class DetectionEngine:
    """Coordinate candidate selection, matching and verification."""

    def __init__(self, config: VerifierConfig | None = None) -> None:
        self.config = config or VerifierConfig()
        self.candidate_selector = CandidateSelector()
        self.matcher = SandwichMatcher()
        self.verifier = SandwichVerifier(self.config)

    def detect(self, detection_input: DetectionInput) -> DetectionResult:
        candidates = self.candidate_selector.select(detection_input)
        triplets = self.matcher.match(candidates)
        matches = self._verified_matches(triplets)
        return DetectionResult(
            rule_version=RuleVersion.V1,
            block_number=detection_input.block.block_number,
            block_hash=detection_input.block.block_hash,
            matches=matches,
        )

    def _verified_matches(
        self,
        triplets: Iterable[SwapTriplet],
    ) -> list[SandwichMatch]:
        unique: dict[tuple[str, str, str, str, str], SandwichMatch] = {}
        for triplet in triplets:
            match = self.verifier.verify(triplet)
            if match is None:
                continue
            unique.setdefault(match.identity(), match)

        return list(unique.values())

