# 🌱 OptiCrop - AI-Powered Smart Agricultural Production Optimization Engine

<div align="center">

**An AI-Powered Crop Recommendation & Agricultural Decision Support Platform for Smart Farming**

![HTML](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikitlearn&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-darkgreen)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange)
![Groq AI](https://img.shields.io/badge/Groq-AI-blueviolet)

</div>

---

# 📖 Overview

OptiCrop is an **AI-powered agricultural recommendation platform** designed to help farmers, agricultural researchers, agribusiness companies, and policymakers make intelligent, data-driven farming decisions.

The platform combines **Machine Learning, Artificial Intelligence, cloud technologies, and modern web development** to recommend the most suitable crops based on soil nutrients and environmental conditions.

By analyzing **Nitrogen (N), Phosphorous (P), Potassium (K), Temperature, Humidity, pH, and Rainfall**, OptiCrop predicts the best crop while providing model insights, analytics, and AI-generated farming recommendations.

---

# ✨ Key Features

- 🌱 AI-Powered Crop Recommendation
- 📂 Dataset Upload & Management
- 🤖 Automatic Problem Type Detection (Classification / Regression)
- 🧹 Automated Data Preprocessing
- 📊 Multi-Model Machine Learning Training
- 🏆 Best Model Selection
- 📈 Model Performance Comparison
- 📉 Interactive Data Visualization
- 🤖 AI-Powered Agricultural Insights (Groq LLaMA 3.3-70B)
- 📋 Prediction History
- 📊 Dashboard Analytics
- 📁 Multi-Project Workspace
- 🔔 Notification Center
- 👤 User Profile Management
- 🌙 Dark / Light Theme
- 📱 Fully Responsive UI
- ☁️ Cloud Database Integration
- 🔒 Secure API Architecture

---

# 🏗️ System Architecture

```
Frontend (HTML, CSS, JavaScript)

        │

        ▼

FastAPI REST API

        │

        ▼

JWT Authentication Middleware

        │

        ▼

SQLAlchemy ORM

        │

        ▼

Supabase PostgreSQL Database

        │

        ├──────────────► Machine Learning Engine
        │                  (Scikit-learn)

        ├──────────────► Groq AI

        ├──────────────► Supabase Storage

        └──────────────► Analytics Engine
```

---

# 🛠 Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript (ES6+)
- TypeScript
- Bootstrap 5
- Vite

## Backend

- Python
- FastAPI
- Uvicorn

## Machine Learning

- Scikit-learn
- Pandas
- NumPy
- SciPy
- Matplotlib
- Seaborn
- Joblib

## Database

- PostgreSQL
- Supabase

## ORM

- SQLAlchemy
- Alembic

## Authentication

- JWT
- Passlib
- bcrypt

## AI

- Groq API
- LLaMA 3.3-70B Versatile

## Cloud Storage

- Supabase Storage

## Deployment

- Vercel / Netlify (Frontend)
- FastAPI Server
- Supabase Cloud Database

---

# 📂 Project Structure

```
OptiCrop/

│
├── frontend/
│   ├── src/
│   ├── assets/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── services/
│   ├── styles/
│   └── utils/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── dependencies/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── storage/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── logs/
│   ├── requirements.txt
│   └── alembic.ini
│
├── datasets/
├── trained_models/
├── documentation/
│
├── README.md
│
└── .gitignore
```

---

# 🚀 Main Modules

## Authentication

- User Registration
- User Login
- JWT Authentication
- Protected Routes
- Logout

---

## Dashboard

- Agricultural Statistics
- Recent Predictions
- Active Projects
- Dataset Summary
- Training Overview
- AI Insights
- Quick Actions

---

## Project Management

- Create Project
- Edit Project
- Delete Project
- Multi-Project Workspace

---

## Dataset Management

- Upload CSV Dataset
- Dataset Validation
- Data Preview
- Missing Value Detection
- Feature Analysis
- Dataset History

---

## Data Preprocessing

- Missing Value Handling
- Duplicate Removal
- Label Encoding
- Feature Scaling
- Feature Selection
- Train-Test Split

---

## Machine Learning

### Classification

- Random Forest Classifier
- Decision Tree Classifier
- Logistic Regression
- K-Nearest Neighbors

### Regression

- Linear Regression
- Random Forest Regressor
- Decision Tree Regressor
- KNN Regressor

---

## Model Comparison

Compare models using

### Classification

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

### Regression

- R² Score
- RMSE
- MAE
- MSE

Automatically selects the **Best Performing Model**.

---

## Crop Recommendation

Predict crops using

- Nitrogen (N)
- Phosphorous (P)
- Potassium (K)
- Temperature
- Humidity
- pH
- Rainfall

Displays

- Recommended Crop
- Prediction Confidence
- Model Used
- Model Version
- AI Recommendation

---

## AI Agricultural Insights

Generate intelligent farming recommendations using

- Soil Analysis
- Crop Suitability
- Environmental Assessment
- Fertilizer Guidance
- Yield Optimization
- Sustainable Farming Suggestions

Powered by **Groq LLaMA 3.3-70B**.

---

## Analytics

- Dataset Analytics
- Model Analytics
- Training Analytics
- Prediction Analytics
- Crop Distribution
- Feature Correlation
- Accuracy Comparison

---

## Prediction History

Store

- Input Parameters
- Recommended Crop
- Confidence Score
- Model Version
- Prediction Timestamp

---

## Notifications

- Dataset Uploaded
- Training Started
- Training Completed
- Prediction Generated
- System Notifications

---

## Profile

Manage

- Personal Information
- Organization
- Location
- Profile Picture
- Security Settings
- Preferences

---

# 🔒 Security Features

- JWT Authentication
- Password Hashing (bcrypt)
- Protected REST APIs
- Input Validation
- Environment Variables
- Secure File Upload Validation
- Database Access Control
- Role-Based Authorization
- Secure API Communication

---

# 🤖 AI Integration

OptiCrop uses **Groq LLaMA 3.3-70B Versatile** to generate

- Crop Recommendations
- Soil Health Insights
- Farming Guidance
- Environmental Analysis
- Yield Optimization Suggestions
- Sustainable Agriculture Practices

---

# 🗄 Database

The application uses **Supabase PostgreSQL** with **SQLAlchemy ORM**.

Main Tables

- Users
- User Settings
- Projects
- Datasets
- Training Sessions
- Trained Models
- Model Metrics
- Prediction History
- Notifications

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/opticrop.git

cd opticrop
```

---

## Install Frontend

```bash
cd frontend

npm install
```

---

## Install Backend

```bash
cd backend

pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file inside the backend folder.

```env
APP_NAME=OptiCrop

APP_ENV=development

SECRET_KEY=

JWT_SECRET=

DATABASE_URL=

SUPABASE_URL=

SUPABASE_ANON_KEY=

SUPABASE_SERVICE_ROLE_KEY=

GROQ_API_KEY=

STORAGE_BUCKET_DATASETS=

STORAGE_BUCKET_MODELS=

STORAGE_BUCKET_PLOTS=

STORAGE_BUCKET_EXPORTS=
```

---

# 🗄 Database Migration

Generate Migration

```bash
alembic revision --autogenerate -m "Initial Migration"
```

Run Migration

```bash
alembic upgrade head
```

---

# ▶ Run Backend

```bash
uvicorn app.main:app --reload
```

---

# ▶ Run Frontend

```bash
npm run dev
```

---

# 📷 Screenshots

| Page | Screenshot |
|------|------------|
| Landing Page | docs/images/landing.png |
| Login | docs/images/login.png |
| Register | docs/images/register.png |
| Dashboard | docs/images/dashboard.png |
| Projects | docs/images/projects.png |
| Dataset Upload | docs/images/dataset-upload.png |
| Data Analysis | docs/images/data-analysis.png |
| Model Training | docs/images/model-training.png |
| Model Comparison | docs/images/model-comparison.png |
| Crop Recommendation | docs/images/crop-prediction.png |
| AI Insights | docs/images/ai-insights.png |
| Profile | docs/images/profile.png |

---

# 🎯 Future Enhancements

- Weather API Integration
- Satellite Image Analysis
- IoT Sensor Integration
- Drone Data Processing
- Fertilizer Recommendation
- Crop Disease Detection
- Yield Prediction
- Market Price Prediction
- AI Chat Assistant
- Mobile Application
- Multi-language Support
- Government Scheme Recommendations
- Precision Agriculture Dashboard

---

# 📚 Documentation

Project documentation is available in the `documentation/` folder.

- API Documentation
- Database Documentation
- Machine Learning Documentation
- Model Training Guide
- Deployment Guide
- System Architecture
- Security Documentation
- Testing Documentation
- Developer Guide
- User Manual
- Project Report

---

# 👨‍💻 Author

**Mohan Sala**

Computer Science Engineering Student

AI & Full Stack Developer

---

# 🙏 Acknowledgements

Special thanks to the following technologies and communities:

- FastAPI
- Python
- Scikit-learn
- Pandas
- NumPy
- SQLAlchemy
- Alembic
- Supabase
- Groq
- PostgreSQL
- Bootstrap
- GitHub

---

# 📄 License

This project is developed for academic and educational purposes.

MIT License

---

<div align="center">

### ⭐ If you found this project useful, please consider giving it a Star ⭐

</div>
