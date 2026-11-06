"""Shared Pydantic contracts for the offline detection core."""

from contracts.block import Block
from contracts.config import VerifierConfig
from contracts.detection_input import DetectionInput
from contracts.detection_result import DetectionResult
from contracts.enums import DetectionReason, RuleVersion, SnapshotPosition
from contracts.pool_snapshot import PoolSnapshot
from contracts.sandwich_match import SandwichMatch
from contracts.swap_event import SwapEvent
from contracts.transaction import Transaction

__all__ = [
    "Block",
    "DetectionInput",
    "DetectionReason",
    "DetectionResult",
    "PoolSnapshot",
    "RuleVersion",
    "SandwichMatch",
    "SnapshotPosition",
    "SwapEvent",
    "Transaction",
    "VerifierConfig",
]

