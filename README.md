# OmniSalus — AI Clinical Command Center & Multi-Disease Diagnostic Platform

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-LightGBM%20%7C%20XGBoost%20%7C%20Scikit--Learn-FF6F00?style=for-the-badge)
![Groq AI](https://img.shields.io/badge/AI-Groq%20Llama%203.3%2070B-F55036?style=for-the-badge)
![Database](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Security](https://img.shields.io/badge/Auth-Session%20Gated%20Admin-06B6D4?style=for-the-badge)

**OmniSalus** is an advanced clinical intelligence platform that pairs **9 trained machine learning diagnostic models** across **7 major human health conditions** with an **interactive Groq-powered clinical reasoning chatbot**, **cryptographically signed PDF reports**, and an **executive SQLite telemetry administration command center**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Diagnostic Models & Disease Modules](#-diagnostic-models--disease-modules)
- [Groq AI Clinical Assistant](#-groq-ai-clinical-assistant)
- [Executive Admin Panel & SQLite Telemetry](#-executive-admin-panel--sqlite-telemetry)
  - [Admin Authentication & Credentials](#admin-authentication--credentials)
  - [Admin Telemetry Features](#admin-telemetry-features)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Project Directory Layout](#-project-directory-layout)
- [Installation & Quickstart Guide](#-installation--quickstart-guide)
- [API Endpoints Reference](#-api-endpoints-reference)
- [Clinical Disclaimer](#-clinical-disclaimer)

---

## 🌟 Key Features

1. **7 Disease Assessment Calculators**:
   - High-precision risk predictions for Heart Disease, Diabetes, Stroke, Liver Disease, Kidney Disease, Breast Cancer, and Obesity.
2. **Multi-Algorithm Consensus**:
   - Heart disease calculator enables real-time comparison across **LightGBM (83.66%)**, **XGBoost (83.64%)**, and **Logistic Regression (83.23%)** simultaneously.
3. **Groq AI Clinical Assistant**:
   - Ultra-fast medical conversation agent powered by Groq's high-speed inference engine (`llama-3.3-70b-versatile` with automatic tiered fallback).
   - **Context-Aware Diagnosis Analysis**: Automatically reads exact patient biomarker inputs and model risk percentages without canned or repetitive replies.
   - **Frontend API Key Manager**: Modal in navbar and chat drawer allows users to plug in their personal Groq API keys with live connection verification.
4. **Unified SQLite Clinical Database**:
   - Automatically stores every patient assessment, risk category, exact timestamps, and calculated timespans into a central `omnisalus.db` SQLite database.
5. **Secure Executive Admin Panel**:
   - Protected dashboard with KPI summary cards, filter tabs, live search, biomarker deep-dive modals, and instant CSV exports.
   - Gated behind session-based authentication with hardcoded credentials and `@admin_required` route protection.
6. **Cryptographically Signed PDF Reports**:
   - Generates tamper-proof medical assessment summaries using `itsdangerous` and `ReportLab`.
7. **Cyber-Clinical Dark Glassmorphism UI**:
   - Modern design tokens with HSL gradients, responsive mobile navigation, and zero-dependency local SVG vector masks (`icons.css`).

---

## 🩺 Diagnostic Models & Disease Modules

| Disease Module | URL Route | ML Architecture | Metrics / Notes |
|---|---|---|---|
| **Heart Disease** | `/heart` | LightGBM, XGBoost, Logistic Regression | 18 CDC clinical & lifestyle metrics; single or multi-model comparison mode |
| **Diabetes Risk** | `/diabetes` | XGBoost Classifier | Glycemic threshold scoring with pre-diabetic risk tiering |
| **Stroke Vulnerability** | `/stroke` | XGBoost Classifier | Vascular risk calculation based on cardiovascular indicators |
| **Liver Disease** | `/liver` | Ensemble Classifier | Bilirubin, liver enzymes, and albumin ratio analysis |
| **Kidney Disease** | `/kidney` | Random Forest Classifier | Renal function biomarkers and hypertension telemetry |
| **Breast Cancer** | `/breast-cancer` | Scikit-Learn Classifier | Fine-needle aspirate (FNA) cell nuclei characteristics |
| **Obesity Level** | `/obesity` | Multi-Class Decision Classifier | 7-tier classification from Insufficient Weight to Obesity Type III |

All 9 models can be validated using the built-in validator script:
```bash
python check_all_models.py
```

---

## 🤖 Groq AI Clinical Assistant

The AI companion ("Omni") provides interactive clinical explanations for all diagnostic results:

- **Model Engine**: Powered by Groq's low-latency API. Default primary model is `llama-3.3-70b-versatile` with automatic dynamic fallback to active account tier models (`llama3-70b-8192`, `llama-3.1-70b-versatile`, `llama3-8b-8192`, `mixtral-8x7b-32768`).
- **Interactive Key Manager**: Click the **"Groq API Key"** button in the navbar or chat drawer header to input your key. The app performs a live test connection and stores it in your browser session for seamless access.
- **Dynamic Context Injection**: When an assessment is run, Omni receives the specific biomarkers (e.g., blood pressure, glucose, enzymes) and the model's output probability to provide personalized, structured dietary and lifestyle guidance.

---

## 🛡️ Executive Admin Panel & SQLite Telemetry

### Admin Authentication & Credentials

The centralized clinical telemetry dashboard is located at **`/admin`**. Unauthenticated visitors are automatically redirected to the dedicated login gateway at **`/admin/login`**.

| Field | Default Value | Environment Variable Override |
|---|---|---|
| **Admin ID / Username** | `admin` | `OMNI_ADMIN_USER` |
| **Admin Password** | `admin123` | `OMNI_ADMIN_PASSWORD` |

- **Login Gateway**: Features a quick-credentials hint box, password show/hide toggle (`👁`/`🙈`), and animated error handling.
- **Session Protection**: All `/admin` and `/api/admin/*` routes are protected using `@admin_required`.
- **Navbar Highlight**: High-visibility glowing cyber-capsule with an active `SQLITE` chip.
- **Logout Action**: Prominent button in the dashboard header (`/admin/logout`) clears session state and relocks the panel.

### Admin Telemetry Features

- **KPI Cards**: Live counts for *Total Assessments*, *Today's Submissions*, *High Risk Alerts*, and *Top Active Disease Module*.
- **Multi-Filter Toolbar**: Filter by specific disease module (Heart, Diabetes, Liver, etc.) or risk level (Low, Moderate, High, Critical).
- **Search System**: Search patient records by ID, diagnosis keyword, or specific biomarker values.
- **Inspect Biomarker Telemetry**: Modal view displaying formatted JSON input parameters, model predictions, client IP, and submission timespans.
- **One-Click CSV Export**: Download complete dataset history (`/api/admin/export`).
- **Granular Record Deletion**: Delete individual test entries safely.

---

## 🏗️ Architecture & Tech Stack

```
OmniSalus/
├── Frontend Layer       HTML5 + Vanilla CSS (Glassmorphism) + Vanilla JavaScript
├── Iconography          Local SVG Vector Masks (icons.css — Zero CDN dependency)
├── Backend Server       Python 3.12 + Flask 3.1 + Jinja2 Templates
├── Database Engine      SQLite3 (omnisalus.db) via db_manager.py
├── Machine Learning     Scikit-learn, XGBoost, LightGBM, Pandas, NumPy, Joblib
├── LLM Integration      Groq Cloud SDK (Llama 3.3 70B Versatile)
└── Document Security    URLSafeTimedSerializer (itsdangerous) + ReportLab PDF
```

---

## 📁 Project Directory Layout

```
OmniSalus/
├── app.py                      # Core Flask application, page routes, and API endpoints
├── db_manager.py               # SQLite schema setup, record queries, and stats manager
├── model_engine.py             # Inference pipeline for all 9 machine learning models
├── groq_chatbot.py             # Groq clinical conversational assistant & fallback engine
├── pdf_report.py               # Signed PDF diagnostic report generator
├── check_all_models.py         # Verification test script for all 9 model loaders
├── omnisalus.db                # SQLite database storing clinical telemetry records
├── requirements.txt            # Python package dependencies
│
├── static/
│   ├── css/
│   │   ├── style.css           # Core base layout styles
│   │   ├── experience.css      # Glassmorphism theme, admin panel & login styles
│   │   └── icons.css           # Local vector SVG icon masks
│   ├── js/
│   │   ├── main.js             # Form handling, prediction requests, UI controllers
│   │   ├── admin.js            # Admin panel telemetry table, filters & modal logic
│   │   └── chatbot.js          # Chatbot drawer, Groq API key manager modal
│   └── images/
│       └── omni-robot.png      # 3D clinical AI companion artwork
│
└── templates/
    ├── base.html               # Master layout with highlighted Admin nav link
    ├── index.html              # Command Center dashboard homepage
    ├── heart.html              # Heart disease risk calculator (3-model comparison)
    ├── diabetes.html           # Diabetes risk calculator
    ├── stroke.html             # Stroke vulnerability calculator
    ├── liver.html              # Liver health diagnostics
    ├── kidney.html             # Kidney & renal disease calculator
    ├── breast_cancer.html      # Breast cancer malignancy classifier
    ├── obesity.html            # Obesity level classifier
    ├── admin.html              # Centralized SQLite clinical admin panel
    └── admin_login.html        # Secure admin login portal
```

---

## 🚀 Installation & Quickstart Guide

### 1. Prerequisites
- **Python 3.12+** installed on your operating system.
- Git (optional, for repository management).

### 2. Environment Setup

Clone or open the project folder in your terminal:
```bash
cd OmniSalus
```

Create and activate a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the verified project requirements:
```bash
pip install -r requirements.txt
```

### 4. Verify Model Integrity

Verify that all 9 machine learning models load correctly:
```bash
python check_all_models.py
```
*Expected output:* `Loaded 9/9 models. All loaders passed.`

### 5. Start the Application

Launch the Flask development server:
```bash
python app.py
```

The server will initialize SQLite and start at:
👉 **`http://127.0.0.1:5000`**

---

## 📡 API Endpoints Reference

### Public Clinical Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict/<model_type>` | Runs ML inference for `heart`, `diabetes`, `stroke`, `liver`, `kidney`, `breast-cancer`, or `obesity`. Saves telemetry to SQLite. |
| `POST` | `/api/chat` | Sends user query and diagnostic context to Groq AI chatbot. |
| `POST` | `/api/test-key` | Validates a user-supplied Groq API key with live model test. |
| `POST` | `/api/report` | Downloads signed PDF diagnostic report. |
| `GET` | `/api/health-check` | Returns operational status and count of active models. |

### Protected Admin Endpoints (`@admin_required`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/records` | Fetches filtered & paginated patient assessment records. |
| `GET` | `/api/admin/records/<id>` | Retrieves full biomarker JSON telemetry for a record. |
| `DELETE`| `/api/admin/records/<id>` | Permanently deletes a patient record. |
| `GET` | `/api/admin/stats` | Returns aggregate counts, today's totals, and risk breakdown. |
| `GET` | `/api/admin/export` | Downloads the full assessment database as a `.csv` file. |

---

## ⚠️ Clinical Disclaimer

OmniSalus is developed for **educational, hackathon demonstration, and clinical research prototyping purposes only**. The machine learning models and conversational AI outputs should not be used as a substitute for professional medical advice, clinical diagnosis, or immediate emergency care. Always consult a qualified healthcare provider for any medical conditions.
