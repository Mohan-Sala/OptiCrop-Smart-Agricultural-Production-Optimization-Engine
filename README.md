# OptiCrop AI 🌾🤖

OptiCrop AI is a production-grade Agricultural Intelligence Platform combining Machine Learning with Soil and Climate agronomics. It empowers farmers, agronomists, and researchers to make data-driven crop recommendations, evaluate crop suitability under changing weather conditions, and analyze machine learning model behavior in real time.

---

## 🌟 Core Features

- **Crop Recommendation Engine**: Predicts optimal crops based on 7 essential agronomic variables ($N, P, K$, Temperature, Humidity, pH, Rainfall) with tested high-confidence presets.
- **Dynamic Crop Suitability Checker**: Evaluates if field conditions match specific target crops and displays comparative probability distributions across all crops trained in the model.
- **Interactive Datasets & CSV Viewer**: In-dashboard CSV manager allowing farmers to upload custom agricultural datasets, preview records in a full-screen table, download files, and automatically retrain models on upload.
- **Comprehensive Analytics & Research Dashboard**: Live inference audit logs stored in MongoDB Atlas, crop recommendation frequency distributions, and chronological performance tracking.
- **Explainable Model Insights**: Real-time transparency into Random Forest Gini feature importances, cross-validation metrics (Accuracy, F1 Macro, Precision), hyperparameters, and MongoDB GridFS model artifacts.

---

## 🛠️ Architecture & Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Routing & State**: TanStack Router + TanStack Start
- **UI Components**: Tailwind CSS + Shadcn UI + Radix Primitives + Lucide Icons
- **Data Visualization**: Recharts (Horizontal Bar Charts, Chronology Lines)
- **Notifications**: Sonner

### Backend
- **Framework**: FastAPI (Asynchronous Python 3.11)
- **Machine Learning**: Scikit-Learn (RandomForestClassifier, Cross-Validation, Metrics)
- **Persistence**: MongoDB Atlas
  - **Documents**: Beanie ODM / Motor Async driver
  - **Artifacts & Datasets**: MongoDB GridFS Storage
- **Testing**: Pytest (100% passing test suite across 62 integration tests)

---

## 📁 Repository Structure

```text
opticrop-ai/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/v1/routes/    # Endpoints (predictions, datasets, training, analytics)
│   │   ├── database/         # MongoDB Atlas connection & Beanie ODM
│   │   ├── models/           # Beanie document models
│   │   ├── services/         # ML pipeline, bootstrap, storage, analytics
│   │   └── storage/          # MongoDB GridFS integration
│   ├── tests/                # Full Pytest test suite
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/                 # React & Vite Application
│   ├── src/
│   │   ├── routes/           # TanStack file-based routes (dashboard, suitability, etc.)
│   │   ├── components/       # Shadcn UI & OptiCrop visual components
│   │   └── lib/              # Centralized API client & agronomy presets
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite build configuration
├── crop_data.csv             # Sample agricultural dataset (100 records)
├── crop_recommendation.csv   # Seed agronomic dataset
└── .gitignore                # Comprehensive Git ignore rules
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (npm / pnpm / yarn)
- MongoDB Atlas Cluster URI

---

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Set your MongoDB connection URI and database name:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=opticrop_db
   ```

5. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000` (or the port displayed in your terminal).

---

## 🧪 Testing

Run the backend test suite:
```bash
cd backend
python -m pytest tests/
```

---

## 📄 License
This project is licensed under the MIT License.
