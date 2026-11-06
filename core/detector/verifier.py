from contracts.config import VerifierConfig
from contracts.enums import DetectionReason
from contracts.sandwich_match import SandwichMatch
from core.detector.matcher import SwapTriplet


class SandwichVerifier:
    """Validate a structural triplet against the deterministic MVP rules."""

    def __init__(self, config: VerifierConfig | None = None) -> None:
        self.config = config or VerifierConfig()

    def verify(self, triplet: SwapTriplet) -> SandwichMatch | None:
        front = triplet.front
        victim = triplet.victim
        back = triplet.back
        reasons: list[DetectionReason] = []

        if front.pool_address.lower() != victim.pool_address.lower():
            return None
        if victim.pool_address.lower() != back.pool_address.lower():
            return None
        reasons.append(DetectionReason.SAME_POOL)

        front_order = (front.tx_index, front.log_index)
        victim_order = (victim.tx_index, victim.log_index)
        back_order = (back.tx_index, back.log_index)
        if not front_order < victim_order < back_order:
            return None
        reasons.append(DetectionReason.ORDER_VALID)

        if front.actor.lower() != back.actor.lower():
            return None
        reasons.append(DetectionReason.ATTACKER_CONSISTENT)

        if victim.actor.lower() == front.actor.lower():
            return None
        reasons.append(DetectionReason.VICTIM_DISTINCT)

        if (
            victim.token_in.lower() != front.token_in.lower()
            or victim.token_out.lower() != front.token_out.lower()
            or back.token_in.lower() != front.token_out.lower()
            or back.token_out.lower() != front.token_in.lower()
        ):
            return None
        reasons.append(DetectionReason.DIRECTION_MATCHED)

        if back.token_out.lower() != front.token_in.lower():
            return None
        reasons.append(DetectionReason.QUOTE_TOKEN_MATCHED)

        gross_profit = back.amount_out - front.amount_in
        if gross_profit < self.config.min_gross_profit:
            return None
        reasons.append(DetectionReason.POSITIVE_GROSS_PROFIT)

        return SandwichMatch(
            pool_address=front.pool_address,
            attacker=front.actor,
            victim=victim.actor,
            front_tx_hash=front.tx_hash,
            victim_tx_hash=victim.tx_hash,
            back_tx_hash=back.tx_hash,
            base_token=front.token_out,
            quote_token=front.token_in,
            gross_profit_signal=gross_profit,
            price_impact_confirmed=None,
            reasons=reasons,
        )

    def verify_price_impact(self, match: SandwichMatch) -> bool | None:
        """Reserved extension point; price impact is outside the MVP scope."""

        if not self.config.enable_price_impact:
            return None
        return None

