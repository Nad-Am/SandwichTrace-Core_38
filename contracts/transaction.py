from pydantic import BaseModel, ConfigDict, Field


class Transaction(BaseModel):
    """A successful or failed transaction included in the processed block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tx_hash: str = Field(min_length=1)
    from_address: str = Field(min_length=1)
    to_address: str | None = None
    tx_index: int = Field(ge=0)
    status: int = Field(ge=0, le=1)

