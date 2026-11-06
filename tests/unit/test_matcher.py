from core.detector.candidate import CandidateSelector
from core.detector.matcher import SandwichMatcher
from tests.helpers import (
    ATTACKER,
    BASE,
    OTHER,
    POOL,
    POOL_2,
    QUOTE,
    VICTIM,
    make_input,
    make_sandwich_swaps,
    make_swap,
)


def test_matcher_finds_standard_triplet() -> None:
    detection_input = make_input(*make_sandwich_swaps())
    candidates = CandidateSelector().select(detection_input)
    triplets = SandwichMatcher().match(candidates)

    assert len(triplets) == 1
    assert triplets[0].front.tx_hash == "0xfront"
    assert triplets[0].victim.tx_hash == "0xvictim"
    assert triplets[0].back.tx_hash == "0xback"


def test_matcher_skips_unrelated_transactions_and_pools() -> None:
    front, victim, back = make_sandwich_swaps()
    noisy_front = front.model_copy(update={"tx_index": 1})
    noisy_victim = victim.model_copy(update={"tx_index": 3})
    other_pool = make_swap(
        "0xother-pool",
        4,
        OTHER,
        pool=POOL_2,
        amount_in=50,
        amount_out=400,
    )
    noisy_back = back.model_copy(update={"tx_index": 5})
    detection_input = make_input(
        noisy_front,
        noisy_victim,
        other_pool,
        noisy_back,
    )

    triplets = SandwichMatcher().match(
        CandidateSelector().select(detection_input)
    )

    assert len(triplets) == 1
    assert triplets[0].front.tx_hash == "0xfront"
    assert triplets[0].back.tx_hash == "0xback"


def test_matcher_rejects_same_actor_as_victim() -> None:
    detection_input = make_input(
        make_swap("0xfront", 1, ATTACKER),
        make_swap("0xvictim", 2, ATTACKER),
        make_swap(
            "0xback",
            3,
            ATTACKER,
            token_in=BASE,
            token_out=QUOTE,
            amount_out=130,
        ),
    )

    triplets = SandwichMatcher().match(
        CandidateSelector().select(detection_input)
    )

    assert triplets == []


def test_matcher_does_not_require_adjacent_events() -> None:
    detection_input = make_input(
        make_swap("0xfront", 1, ATTACKER),
        make_swap("0xvictim", 9, VICTIM),
        make_swap(
            "0xback",
            10,
            ATTACKER,
            token_in=BASE,
            token_out=QUOTE,
            amount_out=130,
        ),
    )

    triplets = SandwichMatcher().match(
        CandidateSelector().select(detection_input)
    )

    assert len(triplets) == 1


def test_candidate_selector_ignores_failed_transactions() -> None:
    detection_input = make_input(*make_sandwich_swaps())
    failed_transactions = [
        transaction.model_copy(update={"status": 0})
        if transaction.tx_hash == "0xfront"
        else transaction
        for transaction in detection_input.transactions
    ]
    detection_input = detection_input.model_copy(
        update={"transactions": failed_transactions}
    )

    candidates = CandidateSelector().select(detection_input)

    assert all(
        event.tx_hash != "0xfront"
        for events in candidates.values()
        for event in events
    )

