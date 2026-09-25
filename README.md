# 🌾 OptiCrop AI - Intelligent Crop Recommendation & Precision Agriculture Engine

<div align="center">

**An AI-Powered Precision Agriculture Platform for Smart Crop Recommendation, Soil Suitability Analysis & Agronomic Intelligence**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)
![Beanie ODM](https://img.shields.io/badge/Beanie-Async_ODM-black)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange)
![Recharts](https://img.shields.io/badge/Recharts-Data_Viz-22b5bf)
![Pytest](https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest&logoColor=white)

</div>

---

# 📖 Overview

OptiCrop AI is a production-ready **AI-powered precision agriculture platform** that enables farmers, agronomists, and agricultural researchers to make data-driven crop selections, evaluate land and soil suitability under dynamic weather conditions, inspect machine learning model behavior, and manage custom agricultural datasets through a modern, responsive web application.

The platform bridges real-world agricultural agronomics and advanced machine learning to predict optimal crops based on 7 critical parameters: **Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, and Rainfall**.

---

# ✨ Key Features

- 👤 Secure User Registration & Login with Profile Management
- 🔐 JWT-Based Authentication with Refresh Token Rotation
- 🌾 Intelligent Crop Recommendation Engine with Multi-Class Probability Scoring
- ⚖️ Dynamic Crop Suitability Checker with Dataset-Calibrated Optimal Ranges
- 📊 Interactive Analytics Dashboard with Correlation Heatmaps & Feature Distributions
- 🧠 Transparent Model Insights with Gini Feature Importances & Evaluation Metrics
- 📁 Custom Dataset Upload & CSV Viewer with Dynamic Metric Recalculation
- 🔄 Automatic Model Retraining & Real-Time Sync on Dataset Change
- 🛡️ Outlier Detection, Validation & Robust Agronomic Boundaries
- 📈 Chronological Prediction Audit Logs & Recommendation Frequency Tracking
- 🌙 Dark / Light Modern Agricultural Theme
- 📱 Fully Responsive UI Built with Shadcn UI & Tailwind CSS
- ☁️ Asynchronous MongoDB Atlas Integration via Beanie ODM & GridFS
- 🔒 Enterprise API Security with Bcrypt Hashing & CORS Protection

---

# 🏗️ System Architecture

```
Frontend (React 18 + TypeScript + Vite + Tailwind CSS + TanStack Router)

        │
        ▼ HTTP / REST (Bearer JWT Auth)

FastAPI Asynchronous Backend (Python 3.11)

        │
        ├──► Authentication & Role Verification (OAuth2 / JWT / Bcrypt)
        │
        ├──► ML Inference & Preprocessing Pipeline (Scikit-Learn / Pandas / NumPy)
        │       │
        │       ├── Random Forest Classifier
        │       ├── Agronomic Boundary Validator
        │       └── Dynamic Optimal Range Analyzer
        │
        └──► Database & Storage Access Layer
                │
                ├── Beanie Async ODM (MongoDB Atlas Collections)
                │       ├── Users & Audit Logs
                │       ├── Prediction Runs & Histories
                │       ├── Datasets & Summaries
                │       └── Deployments & Model Metrics
                │
                └── MongoDB GridFS Bucket (Serialized Models & CSV Artifacts)
```

---

# 🛠 Technology Stack

## Frontend

- React 18+
- TypeScript
- Vite
- TanStack Router & File-based Routing
- Tailwind CSS
- Shadcn UI & Radix UI Primitives
- Recharts (Interactive Visualizations)
- Lucide React Icons
- Sonner (Toast Notifications)

## Backend

- Python 3.11+
- FastAPI (High-performance Async Web Framework)
- Pydantic v2 (Data Validation & Settings Management)
- Uvicorn (ASGI Server)

## Database & Storage

- MongoDB Atlas (Cloud NoSQL Database)
- Beanie ODM (Async Object Document Mapper with Motor)
- GridFS (Distributed File Storage for Datasets & Model Checkpoints)

## Machine Learning & Data Science

- Scikit-Learn (Random Forest, Decision Tree, Logistic Regression, Evaluation)
- Pandas & NumPy (Data Processing & Statistical Analysis)
- Joblib (Model Serialization)

## Authentication & Security

- JWT (JSON Web Tokens - Access & Refresh)
- Passlib & Bcrypt (Password Hashing)
- CORS Middleware & Input Sanitization

## Testing & Quality

- Pytest (Comprehensive Unit & Integration Testing)
- Pytest-Asyncio
- ESLint & Prettier

---

# 📂 Project Structure

```
opticrop-ai/
│
├── frontend/
│   ├── public/                 # Static assets and favicon
│   ├── src/
│   │   ├── components/
│   │   │   ├── opticrop/       # Platform shells, navigation, charts, forms
│   │   │   └── ui/             # Shadcn UI primitives (cards, dialogs, tables)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # API client, agronomic ranges, auth context
│   │   ├── routes/             # TanStack file routes (recommendation, suitability, etc.)
│   │   ├── router.tsx          # Application router setup
│   │   └── styles.css          # Tailwind CSS styles
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/      # FastAPI endpoints (auth, prediction, dataset, analytics)
│   │   ├── core/               # Configuration, security, database connectors
│   │   ├── models/             # Beanie ODM documents (User, Dataset, Prediction, Model)
│   │   ├── repositories/       # MongoDB data access layer
│   │   ├── schemas/            # Pydantic request & response models
│   │   ├── services/           # ML pipelines, training, preprocessing, analytics
│   │   └── storage/            # GridFS distributed file management
│   ├── scripts/                # Database migrations & utilities
│   ├── tests/                  # Pytest integration & unit test suite
│   ├── requirements.txt        # Python backend dependencies
│   ├── pytest.ini
│   └── .env.example            # Environment variables template
│
├── .gitignore                  # Git ignore rules (secrets, venv, node_modules)
└── README.md                   # Project documentation
```

---

# 🚀 Main Modules

## Authentication & Security

- User Registration with Form Validation
- User Login with JWT Access & Refresh Tokens
- Password Encryption with Bcrypt (12 Rounds)
- Protected API Routes & Automatic Token Expiration
- Login Audit Logging

---

## Smart Dashboard

- High-Level Agronomic & Prediction Statistics
- Active Machine Learning Model Status & Accuracy
- Quick Recommendation Launcher
- Recent Prediction History Feed
- Dynamic Dataset Summaries

---

## AI Crop Recommendation Engine

- 7-Parameter Environmental Input:
  - **Nitrogen ($N$)**, **Phosphorus ($P$)**, **Potassium ($K$)** (kg/ha)
  - **Temperature** (°C)
  - **Relative Humidity** (%)
  - **Soil pH Level** (0 - 14)
  - **Rainfall** (mm)
- Multi-Class Confidence Scoring & Ranking
- Agronomic Validation & Out-of-Bounds Detection
- Instant Prediction Presets (Rice, Wheat, Cotton, Maize, etc.)
- Audit Logging to MongoDB Atlas

---

## Dynamic Suitability Checker

- Select any target crop from dynamically populated options
- Live calculation of **Optimal Match Percentage**
- Parameter-by-Parameter Breakdown against uploaded dataset ranges:
  - Optimal minimum, average, and maximum levels
  - Immediate deficit / excess alerts (e.g., Nitrogen deficit, pH too acidic)
- Dynamic "Fill Ideal Values" helper calibrated directly to the active dataset
- Model vs. Target Crop alignment comparison

---

## Dynamic Analytics Dashboard

- Real-Time Statistics calculated from the active dataset:
  - Class Distribution across all crop categories
  - Correlation Heatmaps between soil nutrients and climate factors
  - Nutrient and Climate Distribution histograms
  - Pairwise Feature Scatter analysis
- Updates immediately when a new dataset is uploaded or switched

---

## Model Insights & Explainability

- **Feature Importance Breakdown**: Mean Decrease in Impurity (Gini importance)
- **Model Comparison Table**: Random Forest vs. Alternative Classifiers
- **Classification Metrics**: Precision, Recall, F1-Score (Macro & Weighted)
- **Confusion Matrix Visualization**: Multi-class prediction performance
- **ROC & Precision-Recall Curves**
- Model Hyperparameters & Training Run Telemetry

---

## Dataset Manager & CSV Viewer

- Upload custom agricultural CSV datasets
- Automatic Schema Validation (Verifies $N, P, K$, temperature, humidity, pH, rainfall, label)
- Full-Screen In-Browser CSV Data Grid with Pagination & Search
- Active Dataset Switching & Deletion
- Instant Re-synchronization of all dropdowns, graphs, and statistics

---

## User Settings & Profile

- Manage Profile Information (Name, Email, Role)
- Agronomic Preferences & Default Parameter Presets
- API Session Management & Logout

---

# 🔒 Security Features

- **JWT Authentication**: Secure Bearer tokens with short-lived access and revocable refresh tokens
- **Bcrypt Password Hashing**: Salted cryptographic password storage
- **Input Validation**: Strict Pydantic v2 schemas and agronomic boundary checks
- **CORS Protection**: Whitelisted origin policies
- **Environment Isolation**: Live secrets strictly ignored from version control (`.env`)
- **NoSQL Injection Defense**: Sanitized Beanie ODM queries

---

# 🤖 AI & Machine Learning Pipeline

```
Raw Agricultural Data (CSV)
            │
            ▼
Data Cleaning & Missing Value Handling (Pandas / NumPy)
            │
            ▼
Feature Normalization & Preprocessing (StandardScaler)
            │
            ▼
Stratified Train-Test Split (80 / 20)
            │
            ▼
Random Forest Classifier Ensemble (Scikit-Learn)
            │
            ├── Hyperparameter Tuning (n_estimators, max_depth, min_samples_split)
            ├── Stratified K-Fold Cross Validation
            └── Feature Importance Extraction
            │
            ▼
Model Evaluation (Accuracy, Precision, Recall, F1 Macro)
            │
            ▼
Serialization (Joblib) & Storage (MongoDB GridFS)
            │
            ▼
Real-Time Async Inference & Probability Estimation
```

---

# 🗄 Database & ODM

The platform uses **MongoDB Atlas** with the **Beanie Asynchronous ODM**:

### Core Document Models:
- `User`: User credentials, roles, profile details
- `Dataset`: Uploaded agricultural datasets, metadata, record counts
- `DatasetStatistics`: Dynamic mean, min, max, std-dev metrics per crop
- `TrainedModel`: Serialized model references, hyperparameters, performance metrics
- `PredictionRun`: Individual inference logs, inputs, predicted crops, confidence
- `Deployment`: Production model deployments, health status, versioning
- `MonitoringAlert`: System drift alerts, anomalous input detection
- `LoginAudit`: Authentication security audit trails

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/Mohan-Sala/opticrop-ai.git
cd opticrop-ai
```

---

## 2. Backend Setup

### Navigate to backend directory:
```bash
cd backend
```

### Create and activate virtual environment:
```bash
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 3. Frontend Setup

### Open a new terminal and navigate to frontend:
```bash
cd frontend
```

### Install dependencies:
```bash
npm install
```

---

# 🔑 Environment Variables

Create a `.env` file inside the `backend/` directory:

```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=opticrop_db
MONGODB_TEST_DATABASE=opticrop_ai_test

# GridFS Storage Buckets
STORAGE_BUCKET_DATASETS=datasets
STORAGE_BUCKET_MODELS=models
STORAGE_BUCKET_PLOTS=plots
STORAGE_BUCKET_EXPORTS=exports

# Security & JWT Credentials
JWT_SECRET_KEY=your-32-byte-hex-secret-key-here
JWT_REFRESH_SECRET_KEY=your-32-byte-hex-refresh-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
```

---

# 🗃 Database Initialization & Model Bootstrapping

The backend automatically initializes database indexes and trains a baseline model on first startup using the bundled seed dataset:

```bash
cd backend
python -m app.services.prediction.bootstrap
```

---

# ▶ Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

---

# ▶ Run Frontend

```bash
cd frontend
npm run dev
```

- Application URL: `http://localhost:3000` (or `http://localhost:5173`)

---

# 🧪 Running Tests

OptiCrop AI includes a complete Pytest test suite:

```bash
cd backend
python -m pytest tests/ -v
```

---

# 📷 Screenshots

| Page | Description |
|------|-------------|
| **Landing Page** | Overview of OptiCrop AI with key agronomic capabilities and interactive call-to-actions |
| **Dashboard** | Unified overview displaying model health, recent inference audits, and quick statistics |
| **Crop Recommendation** | 7-factor soil and weather input form with multi-crop prediction confidence distributions |
| **Suitability Checker** | Dynamic crop matching with dataset-calibrated optimal range benchmarks and deficiency alerts |
| **Analytics Dashboard** | Live class distribution charts, correlation heatmaps, and soil nutrient boxplots |
| **Model Insights** | Feature importance ranking, model comparisons, confusion matrices, and ROC curves |
| **Dataset Manager & CSV Viewer** | Full tabular viewer for uploaded CSV records with schema validation and real-time model syncing |
| **User Settings** | User profile preferences, agronomic presets, and security credentials management |

---

# 🎯 Future Enhancements

- 🛰️ Satellite & IoT Sensor Integration (NDVI vegetation index & automated soil probe sync)
- 🌦️ Real-Time Weather API Integration (OpenWeatherMap / NASA POWER automated climate feed)
- 💧 Intelligent Irrigation & Fertilizer Advisory Engine
- 📱 Native Mobile Application (React Native / Flutter for on-field farmers)
- 🌐 Multi-Language Support (Regional farming languages & vernacular UI)
- 🐛 Plant Disease & Pest Image Detection via Vision AI (Convolutional Neural Networks)
- 📑 Automated PDF Agronomic Soil Health Report Export

---

# 📚 Documentation

Detailed documentation and guides:

- [Interactive API Documentation (Swagger UI)](http://localhost:8000/docs)
- [Alternative API Specification (ReDoc)](http://localhost:8000/redoc)
- [Machine Learning Architecture & Feature Weights](backend/app/services/training/)
- [Database Schema & Beanie ODM Models](backend/app/models/)

---

# 👨‍💻 Author

**Mohan Sala**

Computer Science Engineering Student

AI & Full Stack Developer

- Email: [salamohan2005@gmail.com](mailto:salamohan2005@gmail.com)
- GitHub: [@Mohan-Sala](https://github.com/Mohan-Sala)

---

# 🙏 Acknowledgements

Special thanks to the following technologies, libraries, and open-source communities:

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)
- [Scikit-Learn](https://scikit-learn.org/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [Beanie ODM](https://beanie-odm.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn UI](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)
- [Lucide Icons](https://lucide.dev/)

---

# 📄 License

This project is developed for academic, educational, and research purposes.

Licensed under the [MIT License](LICENSE).

---

<div align="center">

### ⭐ If you found this project useful, please consider giving it a Star ⭐

</div>
