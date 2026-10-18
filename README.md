# 🌱 PlantCare AI

[![Live Demo](https://img.shields.io/badge/🌱_Live_Demo-plantcare.khanova.tech-4CAF50?style=for-the-badge)](https://plantcare.khanova.tech)
[![API Status](https://img.shields.io/badge/⚡_API-api.khanova.tech-2196F3?style=for-the-badge)](https://api.khanova.tech/health)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js-000000?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![ML](https://img.shields.io/badge/Model-CNN_%2B_EfficientNet-FF6F00?style=for-the-badge&logo=tensorflow)](https://www.tensorflow.org/)

An AI-powered web app that detects plant diseases from a single leaf photo. Upload an image and get the predicted disease, a confidence score, and a Grad-CAM heatmap showing exactly which part of the leaf the model focused on — including an interactive 3D visualization.
---

## 📸 Screenshots

**Homepage**

<img width="1355" height="642" alt="image" src="https://github.com/user-attachments/assets/682770ae-d54f-4eda-83ab-24c0a1d8fa4e" />


**Diagnosis result with Grad-CAM overlay**

<img width="1350" height="626" alt="image" src="https://github.com/user-attachments/assets/caf73928-bbb0-4d25-8954-89a3a45bc187" />


**Interactive 3D Grad-CAM visualization**

<img width="1243" height="515" alt="image" src="https://github.com/user-attachments/assets/e934d7fc-67ae-4200-9b93-1b414f892d8e" />


---

## 🧠 Model

- **Architecture:** Convolutional Neural Network (CNN) built on **EfficientNetB0** (ImageNet pretrained), fine-tuned via transfer learning.
- **Dataset:** ~54,000 leaf images across multiple plant species and disease classes.
  - Training: 38,000+ images
  - Testing: 8,000+ images
- **Training:** ~21 hours on CPU (no GPU used).
- **Explainability:** Grad-CAM heatmaps highlight the exact leaf regions driving each prediction, rendered as a 2D overlay and an interactive 3D surface.

---

## 🛠️ Tech Stack

**Backend** — FastAPI · TensorFlow/Keras · Python
**Frontend** — Next.js · React · TypeScript · Tailwind CSS
**Deployment** — Hostinger VPS · Nginx · Let's Encrypt SSL · PM2 · systemd

---

## 🚀 Deployment

Deployed on a **Hostinger VPS** running Ubuntu 24.04 — Nginx as reverse proxy, SSL via Let's Encrypt (auto-renewing), FastAPI backend managed by systemd for auto-restart on crash/reboot, and Next.js frontend managed by PM2. Firewall (UFW) and Fail2ban are configured for basic server hardening.

---

## ⚙️ How It Works

1. User uploads a leaf image
2. FastAPI backend preprocesses the image and runs inference through the EfficientNetB0 model
3. Model returns the predicted disease + confidence score
4. Grad-CAM generates a heatmap showing which pixels influenced the decision
5. Frontend displays the diagnosis with a visual explanation

---

## ⚠️ Responsible Use

This is a portfolio/research project. Predictions and Grad-CAM explanations are decision-support aids, not a substitute for professional agricultural or plant-pathology diagnosis.

---

## 👤 Author

Built by **Bahawal Khan**
