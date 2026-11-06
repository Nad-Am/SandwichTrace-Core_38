from pydantic import BaseModel, ConfigDict, Field, model_validator


class SwapEvent(BaseModel):
    """Normalized single-hop AMM swap event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pool_address: str = Field(min_length=1)
    token_in: str = Field(min_length=1)
    token_out: str = Field(min_length=1)
    amount_in: int = Field(ge=1)
    amount_out: int = Field(ge=1)

    actor: str = Field(min_length=1)
    sender: str | None = None
    recipient: str | None = None

    tx_hash: str = Field(min_length=1)
    block_number: int = Field(ge=0)
    tx_index: int = Field(ge=0)
    log_index: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_tokens(self) -> "SwapEvent":
        if self.token_in.lower() == self.token_out.lower():
            raise ValueError("token_in and token_out must differ")
        return self

    @property
    def order_key(self) -> tuple[int, int, int]:
        return (self.block_number, self.tx_index, self.log_index)

