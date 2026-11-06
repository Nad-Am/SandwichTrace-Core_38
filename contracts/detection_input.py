from pydantic import BaseModel, ConfigDict, Field, model_validator

from contracts.block import Block
from contracts.pool_snapshot import PoolSnapshot
from contracts.swap_event import SwapEvent
from contracts.transaction import Transaction


class DetectionInput(BaseModel):
    """Validated input accepted by the detection engine."""

    model_config = ConfigDict(extra="forbid")

    block: Block
    transactions: list[Transaction]
    swap_events: list[SwapEvent]
    pool_snapshots: list[PoolSnapshot] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_relations(self) -> "DetectionInput":
        by_hash: dict[str, Transaction] = {}
        tx_indices: set[int] = set()
        for transaction in self.transactions:
            if transaction.tx_hash in by_hash:
                raise ValueError(f"duplicate transaction hash: {transaction.tx_hash}")
            if transaction.tx_index in tx_indices:
                raise ValueError(f"duplicate transaction index: {transaction.tx_index}")
            by_hash[transaction.tx_hash] = transaction
            tx_indices.add(transaction.tx_index)

        swap_transactions: set[str] = set()
        log_positions: set[tuple[str, int, int]] = set()
        for event in self.swap_events:
            if event.block_number != self.block.block_number:
                raise ValueError(
                    f"swap {event.tx_hash} block_number does not match input block"
                )
            transaction = by_hash.get(event.tx_hash)
            if transaction is None:
                raise ValueError(f"swap references unknown transaction: {event.tx_hash}")
            if event.tx_hash in swap_transactions:
                raise ValueError(
                    "MVP supports at most one swap event per transaction: "
                    f"{event.tx_hash}"
                )
            if transaction.tx_index != event.tx_index:
                raise ValueError(
                    f"swap tx_index does not match transaction: {event.tx_hash}"
                )
            if transaction.from_address.lower() != event.actor.lower():
                raise ValueError(
                    f"swap actor does not match transaction sender: {event.tx_hash}"
                )
            position = (event.tx_hash, event.tx_index, event.log_index)
            if position in log_positions:
                raise ValueError(f"duplicate swap log position: {position}")
            swap_transactions.add(event.tx_hash)
            log_positions.add(position)

        for snapshot in self.pool_snapshots:
            if snapshot.block_number != self.block.block_number:
                raise ValueError(
                    f"pool snapshot block_number does not match input block: "
                    f"{snapshot.pool_address}"
                )
            if snapshot.block_hash and snapshot.block_hash != self.block.block_hash:
                raise ValueError(
                    f"pool snapshot block_hash does not match input block: "
                    f"{snapshot.pool_address}"
                )
        return self

