from collections import defaultdict
from collections.abc import Mapping, Sequence

from contracts.detection_input import DetectionInput
from contracts.swap_event import SwapEvent


class CandidateSelector:
    """Filter successful swaps and group them by pool."""

    def select(self, detection_input: DetectionInput) -> Mapping[str, Sequence[SwapEvent]]:
        successful = {
            transaction.tx_hash
            for transaction in detection_input.transactions
            if transaction.status == 1
        }
        grouped: dict[str, list[SwapEvent]] = defaultdict(list)
        for event in detection_input.swap_events:
            if event.tx_hash not in successful:
                continue
            grouped[event.pool_address.lower()].append(event)

        for events in grouped.values():
            events.sort(key=lambda event: (event.tx_index, event.log_index))
        return {pool: tuple(events) for pool, events in grouped.items()}

