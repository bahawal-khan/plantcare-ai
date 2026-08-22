"""Phase 06 final evaluation entry point.

Evaluates the final Stage 2 checkpoint (``ml/artifacts/stage2/best_model.keras``
by default) on the untouched test split (``data/processed/splits/test.json``),
saves metrics/predictions/confusion-matrix artifacts, and writes a
validation-vs-test overfitting analysis comparing against the Stage 1/2
training histories. Evaluation only: never trains or modifies the model.

Usage:
    python ml/scripts/evaluate_stage2.py
    python ml/scripts/evaluate_stage2.py --limit 40  # smoke run

Writes (under ml/artifacts/evaluation/):
    metrics.json                 overall accuracy/macro/weighted precision-recall-F1
    per_class_metrics.json       per-class precision/recall/F1/support
    classification_report.txt    sklearn classification_report text
    confusion_matrix.json        raw confusion matrix (labels + matrix)
    confusion_matrix.png         confusion matrix heatmap
    predictions.json             per-image true/predicted class + confidence
    config.json                  reproducibility record
    overfitting_analysis.md      validation-vs-test comparison and generalization analysis
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from ml.src.evaluation.evaluate import (
    DEFAULT_MODEL_PATH,
    EvaluationConfig,
    OVERFITTING_REPORT_FILENAME,
    analyze_generalization,
    run_evaluation,
    write_overfitting_report,
)

ROOT = Path(__file__).resolve().parents[2]
BASE_CONFIG_PATH = ROOT / "ml" / "configs" / "config.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 06 final test-set evaluation")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--batch-size", type=int, default=None, help="Overrides ml/configs/config.json")
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap on test samples, for smoke runs"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = json.loads(BASE_CONFIG_PATH.read_text(encoding="utf-8"))

    # Run from the repo root so every path below can stay relative (CLAUDE.md rule 7).
    os.chdir(ROOT)

    config = EvaluationConfig(
        test_manifest=Path("data/processed/splits/test.json"),
        dataset_root=Path(base["dataset"]["local_raw_dir"]),
        class_mapping_path=Path(base["class_mapping_path"]),
        model_path=args.model_path,
        artifacts_dir=Path("ml/artifacts/evaluation"),
        image_size=tuple(base["image_size"]),
        batch_size=args.batch_size or base["batch_size"],
        limit=args.limit,
    )

    result = run_evaluation(config)
    print(f"Evaluated {result.num_samples} test images across {result.num_classes} classes")
    print(f"Accuracy:            {result.accuracy:.4f}")
    print(f"Macro precision/recall/F1:    {result.macro_precision:.4f} / {result.macro_recall:.4f} / {result.macro_f1:.4f}")
    print(f"Weighted precision/recall/F1: {result.weighted_precision:.4f} / {result.weighted_recall:.4f} / {result.weighted_f1:.4f}")
    print(f"Metrics:             {result.metrics_path}")
    print(f"Per-class metrics:   {result.per_class_metrics_path}")
    print(f"Classification rpt:  {result.classification_report_path}")
    print(f"Confusion matrix:    {result.confusion_matrix_json_path}")
    print(f"Confusion matrix img:{result.confusion_matrix_image_path}")
    print(f"Predictions:         {result.predictions_path}")
    print(f"Config:              {result.config_path}")

    stage1_history_path = Path("ml/artifacts/stage1/history.json")
    stage2_history_path = Path("ml/artifacts/stage2/history.json")
    if stage1_history_path.is_file() and stage2_history_path.is_file():
        stage1_history = json.loads(stage1_history_path.read_text(encoding="utf-8"))
        stage2_history = json.loads(stage2_history_path.read_text(encoding="utf-8"))
        analysis = analyze_generalization(
            stage1_history=stage1_history,
            stage2_history=stage2_history,
            test_accuracy=result.accuracy,
            test_macro_f1=result.macro_f1,
            test_weighted_f1=result.weighted_f1,
        )
        report_path = write_overfitting_report(
            analysis, Path(config.artifacts_dir) / OVERFITTING_REPORT_FILENAME
        )
        print(f"Overfitting analysis: {report_path}")
    else:
        print(
            "Skipped overfitting analysis: Stage 1/2 history.json not found "
            f"({stage1_history_path}, {stage2_history_path})"
        )


if __name__ == "__main__":
    main()
