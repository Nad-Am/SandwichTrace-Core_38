from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from contracts.block import Block
from contracts.detection_input import DetectionInput
from contracts.pool_snapshot import PoolSnapshot
from contracts.swap_event import SwapEvent
from contracts.transaction import Transaction


def assemble_detection_input(raw_input: Mapping[str, Any]) -> DetectionInput:
    """Build a validated input and resolve each swap actor from its transaction."""

    block = Block.model_validate(raw_input["block"])
    transactions = [
        Transaction.model_validate(item) for item in raw_input["transactions"]
    ]
    transactions_by_hash = {
        transaction.tx_hash: transaction for transaction in transactions
    }

    swap_events: list[SwapEvent] = []
    for raw_event in raw_input.get("swap_events", []):
        event_data = dict(raw_event)
        tx_hash = event_data.get("tx_hash")
        transaction = transactions_by_hash.get(tx_hash)
        if transaction is None:
            raise ValueError(f"swap references unknown transaction: {tx_hash}")

        actor = event_data.get("actor") or transaction.from_address
        if str(actor).lower() != transaction.from_address.lower():
            raise ValueError(
                f"swap actor does not match transaction sender: {tx_hash}"
            )
        event_data["actor"] = actor
        try:
            swap_events.append(SwapEvent.model_validate(event_data))
        except ValidationError as exc:
            raise ValueError(f"invalid swap event for transaction {tx_hash}") from exc

    pool_snapshots = [
        PoolSnapshot.model_validate(item)
        for item in raw_input.get("pool_snapshots", [])
    ]
    return DetectionInput(
        block=block,
        transactions=transactions,
        swap_events=swap_events,
        pool_snapshots=pool_snapshots,
    )

