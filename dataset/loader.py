import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from contracts.detection_input import DetectionInput
from dataset.assemble import assemble_detection_input


class ExpectedMatch(BaseModel):
    """Ground-truth attack identity kept outside DetectionInput."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pool_address: str
    attacker: str
    victim: str
    front_tx_hash: str
    victim_tx_hash: str
    back_tx_hash: str

    def identity(self) -> tuple[str, str, str, str, str]:
        return (
            self.pool_address.lower(),
            self.attacker.lower(),
            self.front_tx_hash.lower(),
            self.victim_tx_hash.lower(),
            self.back_tx_hash.lower(),
        )


class FixtureGroundTruth(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    expected_matches: list[ExpectedMatch] = Field(default_factory=list)


class Fixture(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    fixture_id: str
    description: str = ""
    input: DetectionInput
    ground_truth: FixtureGroundTruth


def load_fixture(fixture_path: str | Path) -> Fixture:
    path = Path(fixture_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    fixture = Fixture(
        fixture_id=str(payload.get("fixture_id") or path.stem),
        description=str(payload.get("description", "")),
        input=assemble_detection_input(payload["input"]),
        ground_truth=FixtureGroundTruth.model_validate(payload["ground_truth"]),
    )
    _validate_ground_truth_references(fixture)
    return fixture


def load_manifest(manifest_path: str | Path) -> list[Path]:
    path = Path(manifest_path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("fixtures", [])
    paths = [(path.parent / entry).resolve() for entry in entries]
    missing = [str(item) for item in paths if not item.is_file()]
    if missing:
        raise FileNotFoundError(f"manifest references missing fixtures: {missing}")
    return paths


def discover_fixtures(dataset_root: str | Path) -> list[Path]:
    root = Path(dataset_root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"dataset directory does not exist: {root}")
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def _validate_ground_truth_references(fixture: Fixture) -> None:
    transactions = {
        transaction.tx_hash.lower(): transaction
        for transaction in fixture.input.transactions
    }
    swaps = {
        (event.tx_hash.lower(), event.pool_address.lower()): event
        for event in fixture.input.swap_events
    }
    for expected in fixture.ground_truth.expected_matches:
        for tx_hash in (
            expected.front_tx_hash,
            expected.victim_tx_hash,
            expected.back_tx_hash,
        ):
            if tx_hash.lower() not in transactions:
                raise ValueError(
                    f"ground truth references unknown transaction: {tx_hash}"
                )

        for tx_hash, actor in (
            (expected.front_tx_hash, expected.attacker),
            (expected.victim_tx_hash, expected.victim),
            (expected.back_tx_hash, expected.attacker),
        ):
            key = (tx_hash.lower(), expected.pool_address.lower())
            event = swaps.get(key)
            if event is None:
                raise ValueError(
                    "ground truth references a swap outside the expected pool: "
                    f"{tx_hash}"
                )
            if event.actor.lower() != actor.lower():
                raise ValueError(
                    f"ground truth actor does not match swap actor: {tx_hash}"
                )

