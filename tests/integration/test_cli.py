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


def test_cli_reports_missing_fixture(capsys) -> None:
    exit_code = main(
        ["replay", "--fixture", str(ROOT / "does-not-exist.json")]
    )

    assert exit_code == 2
    assert "error:" in capsys.readouterr().err

