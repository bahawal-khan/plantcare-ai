"""Stage 1 transfer-learning training entry point.

Trains the classification head on top of the frozen, ImageNet-pretrained
EfficientNetB0 backbone using ``data/processed/splits/{train,val}.json``.
The test split is never loaded, per ML_SPEC.md's leakage rules.

Usage:
    python ml/scripts/train_stage1.py
    python ml/scripts/train_stage1.py --epochs 1 --train-limit 40 --val-limit 20  # smoke run

Writes (under ml/artifacts/stage1/):
    best_model.keras   the best checkpoint by validation accuracy
    history.json        per-epoch training/validation metrics
    config.json          reproducibility record (seed, sizes, learning rate, ...)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from ml.src.training.stage1 import Stage1TrainingConfig, run_stage1_training

ROOT = Path(__file__).resolve().parents[2]
BASE_CONFIG_PATH = ROOT / "ml" / "configs" / "config.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage 1 transfer-learning training")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=None, help="Overrides ml/configs/config.json")
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--early-stopping-patience", type=int, default=5)
    parser.add_argument(
        "--train-limit", type=int, default=None, help="Cap on train samples, for smoke runs"
    )
    parser.add_argument(
        "--val-limit", type=int, default=None, help="Cap on val samples, for smoke runs"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = json.loads(BASE_CONFIG_PATH.read_text(encoding="utf-8"))

    # Run from the repo root so every path below can stay relative: keeps
    # the saved config.json a portable reproducibility record instead of
    # embedding this machine's absolute filesystem layout (CLAUDE.md rule 7).
    os.chdir(ROOT)

    config = Stage1TrainingConfig(
        train_manifest=Path("data/processed/splits/train.json"),
        val_manifest=Path("data/processed/splits/val.json"),
        dataset_root=Path(base["dataset"]["local_raw_dir"]),
        class_mapping_path=Path(base["class_mapping_path"]),
        artifacts_dir=Path("ml/artifacts/stage1"),
        seed=base["seed"],
        image_size=tuple(base["image_size"]),
        batch_size=args.batch_size or base["batch_size"],
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        dropout_rate=base["model"]["dropout_rate"],
        dense_units=base["model"]["dense_units"],
        early_stopping_patience=args.early_stopping_patience,
        train_limit=args.train_limit,
        val_limit=args.val_limit,
    )

    result = run_stage1_training(config)
    print(f"Trained on {result.num_train_samples} train / {result.num_val_samples} val samples")
    print(f"Best checkpoint: {result.checkpoint_path}")
    print(f"History:         {result.history_path}")
    print(f"Config:          {result.config_path}")


if __name__ == "__main__":
    main()
