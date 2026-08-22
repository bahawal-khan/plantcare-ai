# PlantCare AI — Complete Project Specification

## 1. Product
PlantCare AI is a portfolio-focused deep learning web application that analyzes a plant-leaf image and predicts one of the disease/healthy classes supported by the trained model.

## 2. Main User Flow
1. Visitor opens the website.
2. Visitor selects or drops a leaf image.
3. Frontend sends the image to the FastAPI backend.
4. Backend validates the file and runs the trained EfficientNetB0 model.
5. API returns the predicted class, confidence, plant, and optional top-k results.
6. Backend can generate a Grad-CAM explanation.
7. Frontend displays the result and disease information.
8. User can browse the disease library independently.

## 3. Core Technologies
### ML
- Python
- TensorFlow/Keras
- EfficientNetB0
- ImageNet pretrained weights
- Transfer learning
- Fine-tuning
- Grad-CAM
- NumPy
- Pillow
- scikit-learn

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn
- python-multipart for multipart uploads

### Frontend
- Next.js
- TypeScript
- Tailwind CSS or an equivalent utility/component styling approach

### Deployment
- CPU-oriented deployment
- Frontend and FastAPI backend can be deployed separately
- Final free-tier platform must be verified during deployment phase

## 4. Database
Version 1 deliberately has NO database.

Use:
- `data/disease_info.json`
- `data/class_mapping.json`
- model artifacts
- configuration files

Do not add authentication, user accounts, prediction history, or a relational database in V1.

## 5. Dataset
The implementation must support a configurable plant-disease image dataset. PlantVillage is a recommended starting dataset if its usage terms fit the project.

Do not hard-code the project to one provider or fabricate dataset statistics.

## 6. Model
Primary model: EfficientNetB0 pretrained on ImageNet.

Stage 1:
- freeze pretrained backbone
- train custom classification head

Stage 2:
- unfreeze a controlled upper portion
- fine-tune using a substantially smaller learning rate

## 7. ML Requirements
- reproducible seeds
- train/validation/test split
- no split overlap
- training-only augmentation
- consistent preprocessing
- checkpointing
- early stopping
- learning-rate scheduling where appropriate
- saved class mapping
- training history
- evaluation report
- confusion matrix
- per-class precision/recall/F1
- saved best model

## 8. Grad-CAM
Generate an attention heatmap for supported predictions. The UI must describe Grad-CAM as an interpretability aid, not proof of biological causation.

## 9. FastAPI Requirements
Required endpoints:
- `GET /health`
- `GET /model-info`
- `POST /predict`
- `GET /diseases`
- `GET /diseases/{disease_id}`

FastAPI must:
- load the model once during application lifespan/startup
- validate uploads
- limit upload size
- return structured Pydantic responses
- handle missing model/artifact states cleanly
- never accept arbitrary server file paths from clients
- expose CORS only for configured frontend origins

## 10. Frontend Pages
Public pages:
1. Home
2. Diagnose
3. Diagnosis Result/state
4. Disease Library
5. Disease Detail
6. How It Works
7. About

Global:
- premium navbar
- responsive layout
- professional footer
- clickable GitHub, LinkedIn and email links configured centrally

## 11. Disease Information
Disease information is static application content stored in JSON/configuration, not a database.

Each supported disease can contain:
- id
- plant
- name
- description
- symptoms
- causes
- prevention
- general management/treatment guidance
- severity/category where appropriate

Do not invent medical/agricultural claims. Keep guidance general and include responsible-use language.

## 12. Evaluation
Report:
- accuracy
- precision
- recall
- F1
- per-class metrics
- confusion matrix
- optional ROC/PR analysis when appropriate

The test set is untouched until final evaluation.

## 13. Non-Functional Requirements
- modular
- maintainable
- typed where practical
- tested
- documented
- reproducible
- no secrets committed
- no hard-coded absolute paths
- clear error handling
- CPU-friendly inference
- clean GitHub presentation

## 14. Definition of Done
All phase acceptance criteria pass; the complete test suite passes; a supported image can be classified through FastAPI; Grad-CAM works; frontend and backend integrate; disease information is shown; deployment instructions are documented; and limitations are clearly stated.
