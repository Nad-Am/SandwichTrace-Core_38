from pydantic import BaseModel, ConfigDict, Field

from contracts.enums import DetectionReason


class SandwichMatch(BaseModel):
    """One structurally and economically validated sandwich candidate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pool_address: str
    attacker: str
    victim: str
    front_tx_hash: str
    victim_tx_hash: str
    back_tx_hash: str
    base_token: str
    quote_token: str
    gross_profit_signal: int = Field(ge=0)
    price_impact_confirmed: bool | None = None
    reasons: list[DetectionReason]

    def identity(self) -> tuple[str, str, str, str, str]:
        return (
            self.pool_address.lower(),
            self.attacker.lower(),
            self.front_tx_hash.lower(),
            self.victim_tx_hash.lower(),
            self.back_tx_hash.lower(),
        )

