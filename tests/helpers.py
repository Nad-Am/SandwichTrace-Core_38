from contracts.block import Block
from contracts.detection_input import DetectionInput
from contracts.swap_event import SwapEvent
from contracts.transaction import Transaction

QUOTE = "0x00000000000000000000000000000000000000a1"
BASE = "0x00000000000000000000000000000000000000b2"
POOL = "0x00000000000000000000000000000000000000c3"
POOL_2 = "0x00000000000000000000000000000000000000d4"
ROUTER = "0x00000000000000000000000000000000000000e5"
ATTACKER = "0x1111111111111111111111111111111111111111"
VICTIM = "0x2222222222222222222222222222222222222222"
OTHER = "0x3333333333333333333333333333333333333333"


def make_swap(
    tx_hash: str,
    tx_index: int,
    actor: str,
    *,
    token_in: str = QUOTE,
    token_out: str = BASE,
    amount_in: int = 100,
    amount_out: int = 1000,
    pool: str = POOL,
    block_number: int = 1,
    log_index: int = 0,
) -> SwapEvent:
    return SwapEvent(
        pool_address=pool,
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in,
        amount_out=amount_out,
        actor=actor,
        tx_hash=tx_hash,
        block_number=block_number,
        tx_index=tx_index,
        log_index=log_index,
    )


def make_input(*swaps: SwapEvent, block_number: int = 1) -> DetectionInput:
    transactions = [
        Transaction(
            tx_hash=event.tx_hash,
            from_address=event.actor,
            to_address=ROUTER,
            tx_index=event.tx_index,
            status=1,
        )
        for event in swaps
    ]
    return DetectionInput(
        block=Block(
            block_number=block_number,
            block_hash=f"0xblock-{block_number}",
        ),
        transactions=transactions,
        swap_events=list(swaps),
    )


def make_sandwich_swaps() -> tuple[SwapEvent, SwapEvent, SwapEvent]:
    front = make_swap("0xfront", 1, ATTACKER, amount_in=100, amount_out=1000)
    victim = make_swap("0xvictim", 2, VICTIM, amount_in=200, amount_out=1800)
    back = make_swap(
        "0xback",
        3,
        ATTACKER,
        token_in=BASE,
        token_out=QUOTE,
        amount_in=1000,
        amount_out=125,
    )
    return front, victim, back

