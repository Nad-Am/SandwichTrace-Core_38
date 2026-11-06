from pydantic import BaseModel, ConfigDict, Field


class Block(BaseModel):
    """Minimal block metadata needed by the offline detector."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    block_number: int = Field(ge=0)
    block_hash: str = Field(min_length=1)
    parent_hash: str | None = None

