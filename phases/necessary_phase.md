Before starting Phase 06, review PHASE_04_TRANSFER_LEARNING.md and PHASE_05_FINE_TUNING.md.

So far, only smoke training has been performed.

Now perform the actual full-scale training using the complete PlantVillage dataset already acquired in data/raw/plantvillage/.

Use the complete training and validation splits created in Phase 02.

1. Run full Stage 1 transfer learning.
2. Save the best Stage 1 checkpoint.
3. Run full Stage 2 fine-tuning starting from the best Stage 1 checkpoint.
4. Use the complete training/validation data.
5. Do NOT use test.json or any test images during training or model selection.
6. Do NOT start Phase 06 evaluation yet.
7. Save final best checkpoints, histories, and configs.

Follow PHASE_04_TRANSFER_LEARNING.md and PHASE_05_FINE_TUNING.md exactly.

Acceptance criteria:

- Full training dataset is actually used, not smoke-test limits.
- Full validation dataset is used separately.
- Test set remains completely untouched.
- Stage 1 uses the required frozen-backbone transfer-learning setup.
- Best Stage 1 checkpoint is saved.
- Stage 2 starts from the best full Stage 1 checkpoint.
- Only the specified upper EfficientNetB0 layers are unfrozen.
- Learning rate for Stage 2 is lower than Stage 1.
- Best Stage 2 checkpoint is saved.
- Training history and configuration are saved for both stages.
- Training completes successfully without data leakage.
- Relevant tests pass.
- Report every criterion as PASS / FAIL / NOT VERIFIABLE.

Also report:
- actual train image count
- actual validation image count
- epochs completed
- best validation metrics
- training time
- final Stage 1 checkpoint path
- final Stage 2 checkpoint path
- confirmation that test data was never used

STOP after full training.