import json
from pathlib import Path

from cli import main

ROOT = Path(__file__).resolve().parents[2]


def test_cli_replay_prints_detection_result(capsys) -> None:
    exit_code = main(
        [
            "replay",
            "--fixture",
            str(
                ROOT
                / "dataset"
                / "fixtures"
                / "attacks"
                / "attack_standard.json"
            ),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["is_sandwich"] is True
    assert payload["total_matches"] == 1


def test_cli_evaluate_prints_aggregate_metrics(capsys) -> None:
    exit_code = main(
        [
            "evaluate",
            "--dataset",
            str(ROOT / "dataset" / "fixtures"),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["metrics"]["precision"] == 1.0
    assert len(payload["fixtures"]) == 9


def test_cli_evaluate_accepts_dataset_root(capsys) -> None:
    exit_code = main(
        [
            "evaluate",
            "--dataset",
            str(ROOT / "dataset"),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["metrics"]["precision"] == 1.0
    assert len(payload["fixtures"]) == 9


def test_cli_evaluate_accepts_repository_root(capsys) -> None:
    exit_code = main(["evaluate", "--dataset", str(ROOT)])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["metrics"]["precision"] == 1.0
    assert len(payload["fixtures"]) == 9


def test_cli_rejects_empty_dataset(tmp_path: Path, capsys) -> None:
    exit_code = main(["evaluate", "--dataset", str(tmp_path)])

    assert exit_code == 2
    assert "no fixtures found for evaluation" in capsys.readouterr().err


def test_cli_rejects_malformed_manifest(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"fixture": []}),
        encoding="utf-8",
    )

    exit_code = main(["evaluate", "--manifest", str(manifest_path)])

    assert exit_code == 2
    error = capsys.readouterr().err
    assert "invalid manifest" in error
    assert str(manifest_path.resolve()) in error


def test_cli_rejects_malformed_fixture(tmp_path: Path, capsys) -> None:
    fixture_path = tmp_path / "broken.json"
    fixture_path.write_text(
        json.dumps({"ground_truth": {"expected_matches": []}}),
        encoding="utf-8",
    )

    exit_code = main(["replay", "--fixture", str(fixture_path)])

    assert exit_code == 2
    error = capsys.readouterr().err
    assert "invalid fixture" in error
    assert str(fixture_path) in error


def test_cli_reports_missing_fixture(capsys) -> None:
    exit_code = main(
        ["replay", "--fixture", str(ROOT / "does-not-exist.json")]
    )

    assert exit_code == 2
    assert "error:" in capsys.readouterr().err

