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

