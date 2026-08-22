/**
 * Verified training-dataset statistics. Copied (not fabricated -- CLAUDE.md
 * rule 5) from the checked-in ML evaluation artifacts, which are the
 * authoritative source:
 *   - data/processed/metadata/split_summary.json (split_counts, total_images, num_classes)
 *   - ml/artifacts/evaluation/metrics.json (num_samples on the held-out test split)
 * These are static facts about a fixed training run, not a live API value --
 * update them only if the model is retrained and those artifacts change.
 */
export const datasetStats = {
  totalImages: 54305,
  trainImages: 38012,
  valImages: 8146,
  testImages: 8147,
  numClasses: 38,
} as const;
