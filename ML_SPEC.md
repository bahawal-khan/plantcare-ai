# PlantCare AI — ML Specification

## Model
EfficientNetB0 with ImageNet pretrained weights.

## Classification
Single-label multiclass classification.

Use:
- categorical cross-entropy for one-hot labels, or
- sparse categorical cross-entropy for integer labels.

## Input
Recommended starting point: 224x224 RGB. Keep configurable.

## Augmentation
Apply only to training:
- horizontal flip where biologically reasonable
- small rotations
- moderate zoom
- small translations
- mild contrast/brightness changes

Avoid unrealistic transformations.

## Stage 1 — Transfer Learning
- load ImageNet weights
- freeze backbone
- attach global average pooling + dropout + dense classifier
- train head
- save best checkpoint

## Stage 2 — Fine-Tuning
- load best Stage 1 checkpoint
- unfreeze a controlled upper portion
- keep lower feature layers frozen
- lower learning rate substantially
- monitor validation metrics
- save best checkpoint

## Metrics
- accuracy
- macro/weighted precision
- macro/weighted recall
- macro/weighted F1
- per-class report
- confusion matrix

## Leakage Rules
- split before augmentation
- no test images in training
- no test-based hyperparameter tuning
- no fitting preprocessing statistics on the test set

## Artifacts
Save:
- model
- class mapping
- config
- training history
- metrics
- confusion matrix
- sample predictions
- Grad-CAM examples

## Reproducibility
Record:
- seed
- dataset/split configuration
- image size
- batch size
- epochs
- learning rates
- trainable layers
- framework/model version where practical
