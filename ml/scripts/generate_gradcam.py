"""Phase 07 Grad-CAM example generation entry point.

Loads the final Stage 2 checkpoint (``ml/artifacts/stage2/best_model.keras``
by default) and generates real Grad-CAM heatmaps/overlays/3D-visualization
payloads for a small, class-diverse sample of test-set images, per
ML_SPEC.md "Artifacts: ... Grad-CAM examples". Read-only with respect to the
model: only used for inference (``model.predict``-equivalent calls plus a
gradient pass against the frozen weights), never trains or modifies it.

Usage:
    python ml/scripts/generate_gradcam.py
    python ml/scripts/generate_gradcam.py --num-examples 4  # smoke run

Writes (under ml/artifacts/gradcam/):
    <n>_<class>_heatmap.png   colorized Grad-CAM heatmap, aligned to the image
    <n>_<class>_overlay.png   heatmap blended onto the original image
    <n>_<class>_3d.json       interactive 3D visualization payload (heightmap + texture)
    manifest.json             target layer, responsible-use note, and per-example summary
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image

from ml.src.data.class_mapping import load_class_mapping
from ml.src.evaluation.evaluate import DEFAULT_MODEL_PATH
from ml.src.explainability.gradcam import (
    RESPONSIBLE_USE_NOTE,
    TARGET_LAYER_NAME,
    build_3d_visualization_payload,
    build_gradcam_response_payload,
    generate_gradcam_explanation,
    save_gradcam_images,
)
from ml.src.models.efficientnet import load_model

ROOT = Path(__file__).resolve().parents[2]
BASE_CONFIG_PATH = ROOT / "ml" / "configs" / "config.json"
DEFAULT_PREDICTIONS_PATH = Path("ml/artifacts/evaluation/predictions.json")
DEFAULT_OUTPUT_DIR = Path("ml/artifacts/gradcam")
DEFAULT_NUM_EXAMPLES = 12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 07 Grad-CAM example generation")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--predictions-path", type=Path, default=DEFAULT_PREDICTIONS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--num-examples", type=int, default=DEFAULT_NUM_EXAMPLES)
    return parser.parse_args()


def _select_examples(predictions: list[dict], num_examples: int) -> list[dict]:
    """One correct prediction per distinct predicted class, up to num_examples,
    for a class-diverse sample rather than num_examples images from one class.
    """
    seen_classes: set[str] = set()
    selected: list[dict] = []
    for record in predictions:
        if not record.get("correct"):
            continue
        class_name = record["predicted_class"]
        if class_name in seen_classes:
            continue
        seen_classes.add(class_name)
        selected.append(record)
        if len(selected) >= num_examples:
            break
    return selected


def main() -> None:
    args = parse_args()
    base = json.loads(BASE_CONFIG_PATH.read_text(encoding="utf-8"))

    # Run from the repo root so every path below can stay relative (CLAUDE.md rule 7).
    os.chdir(ROOT)

    class_mapping = load_class_mapping(Path(base["class_mapping_path"]))
    class_names_by_index = [name for name, _ in sorted(class_mapping.items(), key=lambda kv: kv[1])]
    dataset_root = Path(base["dataset"]["local_raw_dir"])
    image_size = tuple(base["image_size"])

    predictions = json.loads(args.predictions_path.read_text(encoding="utf-8"))
    examples = _select_examples(predictions, args.num_examples)
    if not examples:
        raise SystemExit(f"No correct predictions found in {args.predictions_path}")

    model = load_model(args.model_path)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_examples = []
    for i, record in enumerate(examples):
        image_path = dataset_root / record["path"]
        with Image.open(image_path) as img:
            explanation = generate_gradcam_explanation(model, img, image_size=image_size)

        stem = f"{i:02d}_{record['predicted_class']}"
        image_paths = save_gradcam_images(explanation, output_dir, stem=stem)

        payload_3d = build_3d_visualization_payload(explanation)
        payload_path = output_dir / f"{stem}_3d.json"
        payload_path.write_text(json.dumps(payload_3d, indent=2) + "\n", encoding="utf-8")

        response_payload = build_gradcam_response_payload(explanation, class_names=class_names_by_index)
        manifest_examples.append(
            {
                "source_image": str(image_path),
                "true_class": record["true_class"],
                "predicted_class": response_payload["predicted_class"],
                "confidence": response_payload["confidence"],
                "heatmap_image": str(image_paths["heatmap"]),
                "overlay_image": str(image_paths["overlay"]),
                "visualization_3d_payload": str(payload_path),
            }
        )
        print(f"[{i + 1}/{len(examples)}] {record['predicted_class']}: {image_paths['overlay']}")

    manifest = {
        "model_path": str(args.model_path),
        "target_layer": TARGET_LAYER_NAME,
        "image_size": list(image_size),
        "num_examples": len(manifest_examples),
        "responsible_use_note": RESPONSIBLE_USE_NOTE,
        "examples": manifest_examples,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
