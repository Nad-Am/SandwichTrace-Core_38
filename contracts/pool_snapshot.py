from pydantic import BaseModel, ConfigDict, Field, model_validator

from contracts.enums import SnapshotPosition


class PoolSnapshot(BaseModel):
    """Optional block-start reserves for future price impact verification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pool_address: str = Field(min_length=1)
    token0: str = Field(min_length=1)
    token1: str = Field(min_length=1)
    reserve0: int = Field(ge=0)
    reserve1: int = Field(ge=0)
    block_number: int = Field(ge=0)
    block_hash: str | None = None
    position: SnapshotPosition = SnapshotPosition.BLOCK_START

    @model_validator(mode="after")
    def validate_tokens(self) -> "PoolSnapshot":
        if self.token0.lower() == self.token1.lower():
            raise ValueError("token0 and token1 must differ")
        return self

