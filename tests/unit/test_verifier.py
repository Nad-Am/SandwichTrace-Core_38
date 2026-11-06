from contracts.config import VerifierConfig
from contracts.enums import DetectionReason
from core.detector.matcher import SandwichMatcher, SwapTriplet
from core.detector.verifier import SandwichVerifier
from tests.helpers import BASE, QUOTE, make_input, make_sandwich_swaps


def triplet() -> SwapTriplet:
    front, victim, back = make_sandwich_swaps()
    return SwapTriplet(front, victim, back)


def test_verifier_returns_explainable_match() -> None:
    match = SandwichVerifier().verify(triplet())

    assert match is not None
    assert match.gross_profit_signal == 25
    assert match.base_token == BASE
    assert match.quote_token == QUOTE
    assert match.price_impact_confirmed is None
    assert match.reasons == [
        DetectionReason.SAME_POOL,
        DetectionReason.ORDER_VALID,
        DetectionReason.ATTACKER_CONSISTENT,
        DetectionReason.VICTIM_DISTINCT,
        DetectionReason.DIRECTION_MATCHED,
        DetectionReason.QUOTE_TOKEN_MATCHED,
        DetectionReason.POSITIVE_GROSS_PROFIT,
    ]


def test_verifier_rejects_profit_below_configured_threshold() -> None:
    match = SandwichVerifier(
        VerifierConfig(min_gross_profit=26)
    ).verify(triplet())

    assert match is None


def test_verifier_rejects_negative_gross_profit() -> None:
    front, victim, back = make_sandwich_swaps()
    losing_back = back.model_copy(update={"amount_out": 99})

    match = SandwichVerifier().verify(
        SwapTriplet(front, victim, losing_back)
    )

    assert match is None

