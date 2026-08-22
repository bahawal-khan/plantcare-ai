# PlantCare AI — Dataset (Phase 02)

## Source
- Dataset: **PlantVillage**
- Repository: https://github.com/spMohanty/PlantVillage-Dataset
- Pinned commit (immutable): `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`
- Subfolder used: `raw/color` (RGB leaf photographs). The repository also
  contains `raw/grayscale` and `raw/segmented`, which are derived versions
  of the same underlying photographs and are intentionally not downloaded.
- License: no LICENSE file / no license declared by the upstream
  repository at the pinned commit (verified via the GitHub API). The
  dataset originates from the PlantVillage project (Hughes & Salathe,
  2015 / Mohanty, Hughes & Salathe, 2016) and is widely used for research
  and benchmarking. Verify redistribution terms before any use beyond
  research/education.

## Acquisition method
A git partial clone (`--filter=blob:none`) with cone-mode sparse-checkout
restricted to `raw/color`, so only the blobs actually needed are
downloaded — no full commit history, no grayscale/segmented images.
Reproduce with:

```bash
python ml/scripts/acquire_dataset.py
```

which runs (documented for manual fallback if network access is
unavailable):

```bash
git init data/raw/plantvillage
git -C data/raw/plantvillage remote add origin https://github.com/spMohanty/PlantVillage-Dataset.git
git -C data/raw/plantvillage sparse-checkout init --cone
git -C data/raw/plantvillage sparse-checkout set raw/color
git -C data/raw/plantvillage fetch --depth 1 --filter=blob:none origin 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a
git -C data/raw/plantvillage checkout FETCH_HEAD -- .
```

The dataset is **not** committed to Git — `data/raw/` and
`data/processed/` are git-ignored (see `.gitignore`).

## Storage layout
```text
data/
├── raw/
│   └── plantvillage/
│       └── raw/color/<class_name>/<image>.jpg   # acquired images (git-ignored)
├── processed/
│   ├── splits/                                   # train.json / val.json / test.json manifests
│   └── metadata/                                 # dataset_report.json, split_summary.json
├── disease_info.json
└── class_mapping.json
```

Split manifests store relative image paths + class labels only — the
underlying images are never copied, per the phase's "do not duplicate the
dataset" rule.

## Inspection
Run after acquisition:

```bash
python ml/scripts/inspect_dataset.py
python ml/scripts/build_splits.py
```

`inspect_dataset.py` measures the actual image/class counts, corrupt
files, and duplicate content observed on disk (no counts are assumed from
documentation) and writes `data/processed/metadata/dataset_report.json`.
See that file (once generated) and the phase completion report for the
exact observed numbers.

## Split strategy
- Stratified per class, fixed seed (`42`), ratios 70/15/15
  (train/val/test).
- Images with identical content (duplicate photographs) are grouped by
  SHA-256 hash and assigned to a single split as a unit, so the same
  physical image never crosses a split boundary.
- Splits are computed before any augmentation; augmentation
  (`ml/src/preprocessing/augmentation.py`) is applied only to the training
  split at load time and is never used for validation/test.

## Known limitation
PlantVillage images were captured under controlled/lab conditions
(uniform backgrounds, consistent lighting, single detached leaves). A
model trained on this benchmark should be expected to perform worse on
real-world field photographs (cluttered backgrounds, variable lighting,
multiple/overlapping leaves, phone-camera artifacts) than on this
dataset's own held-out test set. This limitation must be stated in the
final product documentation and, where relevant, surfaced in the UI.
