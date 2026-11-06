import json
from pathlib import Path

import pytest

from dataset.loader import discover_fixtures, load_fixture, load_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_manifest_contains_all_fixtures() -> None:
    manifest_paths = load_manifest(ROOT / "dataset" / "manifest.json")
    discovered_paths = discover_fixtures(ROOT / "dataset" / "fixtures")

    assert len(manifest_paths) == len(discovered_paths) == 9
    assert {path.name for path in manifest_paths} == {
        path.name for path in discovered_paths
    }


def test_dataset_root_uses_manifest_automatically() -> None:
    paths = discover_fixtures(ROOT / "dataset")

    assert len(paths) == 9
    assert all(path.is_file() for path in paths)


def test_discover_fixtures_skips_unrelated_json(tmp_path: Path) -> None:
    (tmp_path / "metadata.json").write_text(
        json.dumps({"name": "not a fixture"}),
        encoding="utf-8",
    )

    assert discover_fixtures(tmp_path) == []


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"fixture": []}, "missing required key 'fixtures'"),
        ({"fixtures": []}, "'fixtures' must not be empty"),
        ({"fixtures": "fixture.json"}, "'fixtures' must be a list"),
    ],
)
def test_manifest_rejects_invalid_payload(
    tmp_path: Path,
    payload: dict,
    message: str,
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message) as exc_info:
        load_manifest(manifest_path)

    assert str(manifest_path.resolve()) in str(exc_info.value)


def test_load_fixture_reports_missing_keys_with_path(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "broken.json"
    fixture_path.write_text(
        json.dumps({"ground_truth": {"expected_matches": []}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required keys") as exc_info:
        load_fixture(fixture_path)

    assert str(fixture_path) in str(exc_info.value)


@pytest.mark.parametrize(
    "fixture_path",
    discover_fixtures(ROOT / "dataset" / "fixtures"),
    ids=lambda path: path.stem,
)
def test_every_fixture_loads_and_ground_truth_is_separate(
    fixture_path: Path,
) -> None:
    fixture = load_fixture(fixture_path)

    assert fixture.fixture_id
    assert not hasattr(fixture.input, "ground_truth")

