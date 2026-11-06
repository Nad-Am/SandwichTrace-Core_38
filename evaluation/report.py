import json

from evaluation.runner import EvaluationReport


def render_report(report: EvaluationReport, indent: int = 2) -> str:
    return json.dumps(
        report.model_dump(mode="json"),
        ensure_ascii=False,
        indent=indent,
    )

