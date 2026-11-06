from pydantic import BaseModel, ConfigDict, Field


class VerifierConfig(BaseModel):
    """Deterministic rule thresholds used by the verifier."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    min_gross_profit: int = Field(default=1, ge=1)
    enable_price_impact: bool = False
    min_price_impact_bps: int = Field(default=0, ge=0)

