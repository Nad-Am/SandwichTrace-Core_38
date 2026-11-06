import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from application.detection_service import DetectionService
from dataset.loader import load_manifest
from evaluation.report import render_report
from evaluation.runner import EvaluationRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sandwich-trace",
        description="Offline Ethereum sandwich attack detection",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay_parser = subparsers.add_parser(
        "replay",
        help="Run one fixture through the detection pipeline",
    )
    replay_parser.add_argument("--fixture", required=True, type=Path)

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate all fixtures and print aggregate metrics",
    )
    source_group = evaluate_parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--dataset", type=Path)
    source_group.add_argument("--manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "replay":
            result = DetectionService().detect_fixture(args.fixture)
            print(
                json.dumps(
                    result.model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        if args.command == "evaluate":
            runner = EvaluationRunner()
            if args.manifest:
                report = runner.evaluate_fixtures(load_manifest(args.manifest))
            else:
                report = runner.evaluate_dataset(args.dataset)
            print(render_report(report))
            return 0
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

