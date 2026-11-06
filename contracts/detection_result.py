from pydantic import BaseModel, ConfigDict, computed_field

from contracts.enums import RuleVersion
from contracts.sandwich_match import SandwichMatch


class DetectionResult(BaseModel):
    """Complete detection result for one block-level input."""

    model_config = ConfigDict(extra="forbid")

    rule_version: RuleVersion
    block_number: int
    block_hash: str
    matches: list[SandwichMatch]

    @computed_field
    @property
    def total_matches(self) -> int:
        return len(self.matches)

    @computed_field
    @property
    def is_sandwich(self) -> bool:
        return bool(self.matches)

