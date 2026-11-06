import pytest
from pydantic import ValidationError

from contracts.block import Block
from contracts.detection_input import DetectionInput
from contracts.detection_result import DetectionResult
from contracts.enums import RuleVersion
from contracts.swap_event import SwapEvent
from contracts.transaction import Transaction
from dataset.assemble import assemble_detection_input
from tests.helpers import ATTACKER, BASE, POOL, QUOTE, ROUTER


def test_detection_result_derives_summary_fields() -> None:
    result = DetectionResult(
        rule_version=RuleVersion.V1,
        block_number=1,
        block_hash="0xblock",
        matches=[],
    )

    assert result.total_matches == 0
    assert result.is_sandwich is False
    assert result.model_dump(mode="json")["total_matches"] == 0


def test_actor_must_match_transaction_sender() -> None:
    swap = SwapEvent(
        pool_address=POOL,
        token_in=QUOTE,
        token_out=BASE,
        amount_in=100,
        amount_out=1000,
        actor="0x9999999999999999999999999999999999999999",
        tx_hash="0xfront",
        block_number=1,
        tx_index=1,
        log_index=0,
    )

    with pytest.raises(ValidationError, match="actor does not match"):
        DetectionInput(
            block=Block(block_number=1, block_hash="0xblock"),
            transactions=[
                Transaction(
                    tx_hash="0xfront",
                    from_address=ATTACKER,
                    to_address=ROUTER,
                    tx_index=1,
                    status=1,
                )
            ],
            swap_events=[swap],
        )


def test_input_rejects_multiple_swaps_in_one_transaction() -> None:
    transaction = Transaction(
        tx_hash="0xfront",
        from_address=ATTACKER,
        to_address=ROUTER,
        tx_index=1,
        status=1,
    )
    swaps = [
        SwapEvent(
            pool_address=POOL,
            token_in=QUOTE,
            token_out=BASE,
            amount_in=100,
            amount_out=1000,
            actor=ATTACKER,
            tx_hash="0xfront",
            block_number=1,
            tx_index=1,
            log_index=log_index,
        )
        for log_index in (0, 1)
    ]

    with pytest.raises(ValidationError, match="at most one swap event"):
        DetectionInput(
            block=Block(block_number=1, block_hash="0xblock"),
            transactions=[transaction],
            swap_events=swaps,
        )


def test_assembler_resolves_actor_from_transaction() -> None:
    assembled = assemble_detection_input(
        {
            "block": {"block_number": 1, "block_hash": "0xblock"},
            "transactions": [
                {
                    "tx_hash": "0xfront",
                    "from_address": ATTACKER,
                    "to_address": ROUTER,
                    "tx_index": 1,
                    "status": 1,
                }
            ],
            "swap_events": [
                {
                    "pool_address": POOL,
                    "token_in": QUOTE,
                    "token_out": BASE,
                    "amount_in": 100,
                    "amount_out": 1000,
                    "tx_hash": "0xfront",
                    "block_number": 1,
                    "tx_index": 1,
                    "log_index": 0,
                }
            ],
        }
    )

    assert assembled.swap_events[0].actor == ATTACKER


def test_assembler_rejects_explicit_actor_mismatch() -> None:
    with pytest.raises(ValueError, match="actor does not match"):
        assemble_detection_input(
            {
                "block": {"block_number": 1, "block_hash": "0xblock"},
                "transactions": [
                    {
                        "tx_hash": "0xfront",
                        "from_address": ATTACKER,
                        "to_address": ROUTER,
                        "tx_index": 1,
                        "status": 1,
                    }
                ],
                "swap_events": [
                    {
                        "pool_address": POOL,
                        "token_in": QUOTE,
                        "token_out": BASE,
                        "amount_in": 100,
                        "amount_out": 1000,
                        "actor": "0x9999999999999999999999999999999999999999",
                        "tx_hash": "0xfront",
                        "block_number": 1,
                        "tx_index": 1,
                        "log_index": 0,
                    }
                ],
            }
        )

