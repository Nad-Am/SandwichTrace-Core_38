from bisect import bisect_right
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from contracts.swap_event import SwapEvent


@dataclass(frozen=True)
class SwapTriplet:
    front: SwapEvent
    victim: SwapEvent
    back: SwapEvent

    @property
    def identity(self) -> tuple[str, str, str, str, str]:
        return (
            self.front.pool_address.lower(),
            self.front.actor.lower(),
            self.front.tx_hash.lower(),
            self.victim.tx_hash.lower(),
            self.back.tx_hash.lower(),
        )


class SandwichMatcher:
    """Find A-B-C candidates without assuming the events are adjacent."""

    def match(self, events_by_pool: Mapping[str, Sequence[SwapEvent]]) -> list[SwapTriplet]:
        matches: dict[tuple[str, str, str, str, str], SwapTriplet] = {}

        for pool_events in events_by_pool.values():
            events = sorted(
                pool_events,
                key=lambda event: (event.tx_index, event.log_index),
            )
            if len(events) < 3:
                continue

            back_index: dict[
                tuple[str, str, str], list[int]
            ] = defaultdict(list)
            for index, event in enumerate(events):
                key = (
                    event.actor.lower(),
                    event.token_in.lower(),
                    event.token_out.lower(),
                )
                back_index[key].append(index)

            positions = [index for index in range(len(events))]
            for front_index, front in enumerate(events):
                expected_back_key = (
                    front.actor.lower(),
                    front.token_out.lower(),
                    front.token_in.lower(),
                )
                candidate_backs = back_index.get(expected_back_key, [])
                back_start = bisect_right(candidate_backs, front_index)

                for back_index_value in candidate_backs[back_start:]:
                    back = events[back_index_value]
                    victim_start = bisect_right(positions, front_index)
                    victim_end = bisect_right(positions, back_index_value - 1)
                    for victim_index in positions[victim_start:victim_end]:
                        victim = events[victim_index]
                        if victim.actor.lower() == front.actor.lower():
                            continue
                        if (
                            victim.token_in.lower() != front.token_in.lower()
                            or victim.token_out.lower() != front.token_out.lower()
                        ):
                            continue

                        triplet = SwapTriplet(
                            front=front,
                            victim=victim,
                            back=back,
                        )
                        matches.setdefault(triplet.identity, triplet)

        return sorted(
            matches.values(),
            key=lambda triplet: (
                triplet.front.tx_index,
                triplet.victim.tx_index,
                triplet.back.tx_index,
            ),
        )

