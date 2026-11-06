import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from contracts.detection_input import DetectionInput
from dataset.assemble import assemble_detection_input

_IGNORED_DISCOVERY_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


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
    payload = _read_json_object(path, "fixture")
    missing = [
        key for key in ("input", "ground_truth") if key not in payload
    ]
    if missing:
        raise ValueError(
            f"invalid fixture {path}: missing required keys: "
            f"{', '.join(missing)}"
        )

    try:
        fixture = Fixture(
            fixture_id=str(payload.get("fixture_id") or path.stem),
            description=str(payload.get("description", "")),
            input=assemble_detection_input(payload["input"]),
            ground_truth=FixtureGroundTruth.model_validate(
                payload["ground_truth"]
            ),
        )
        _validate_ground_truth_references(fixture)
    except (KeyError, ValidationError, ValueError) as exc:
        raise ValueError(f"invalid fixture {path}: {exc}") from exc
    return fixture


def load_manifest(manifest_path: str | Path) -> list[Path]:
    path = Path(manifest_path).resolve()
    payload = _read_json_object(path, "manifest")
    if "fixtures" not in payload:
        raise ValueError(
            f"invalid manifest {path}: missing required key 'fixtures'"
        )

    entries = payload["fixtures"]
    if not isinstance(entries, list):
        raise ValueError(
            f"invalid manifest {path}: 'fixtures' must be a list"
        )
    if not entries:
        raise ValueError(
            f"invalid manifest {path}: 'fixtures' must not be empty"
        )
    if any(not isinstance(entry, str) or not entry for entry in entries):
        raise ValueError(
            f"invalid manifest {path}: every fixture entry must be a "
            "non-empty string"
        )

    paths = [(path.parent / entry).resolve() for entry in entries]
    missing = [str(item) for item in paths if not item.is_file()]
    if missing:
        raise FileNotFoundError(f"manifest references missing fixtures: {missing}")
    return paths


def discover_fixtures(dataset_root: str | Path) -> list[Path]:
    root = Path(dataset_root).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"dataset directory does not exist: {root}")

    root_manifest = root / "manifest.json"
    if root_manifest.is_file():
        return load_manifest(root_manifest)

    fixtures: list[Path] = []
    for path in sorted(root.rglob("*.json")):
        relative_parts = path.relative_to(root).parts[:-1]
        if any(part in _IGNORED_DISCOVERY_DIRS for part in relative_parts):
            continue
        if not path.is_file() or path.name == "manifest.json":
            continue
        payload = _read_json_object(path, "JSON file")
        if _looks_like_fixture(payload):
            fixtures.append(path)
    return fixtures


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid {label} JSON {path}: line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise ValueError(
            f"invalid {label} {path}: expected a JSON object"
        )
    return dict(payload)


def _looks_like_fixture(payload: Mapping[str, Any]) -> bool:
    fixture_keys = {"fixture_id", "input", "ground_truth"}
    return bool(fixture_keys.intersection(payload))


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

