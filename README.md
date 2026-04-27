# FairLens 2.0 ⚖️

**FairLens** is a production-grade Bias Audit & Decision Intelligence system designed to identify, explain, and simulate the mitigation of algorithmic bias in machine learning datasets.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-19-61dafb.svg)
![FastAPI](https://img.shields.io/badge/fastapi-v0.100+-009688.svg)

## 🚀 Key Features

- **Statistical Fairness Metrics:** Calculates Disparate Impact (DI) with confidence intervals and statistical significance tests.
- **SHAP-based Root Cause Analysis:** Identifies which features the model relies on most to drive outcome disparities.
- **Proxy Bias Detection:** Automatically detects features that correlate strongly with protected attributes.
- **What-If Simulation:** Interactively drop features to see how it affects the Disparate Impact ratio in real-time.
- **Stability Analysis:** Uses bootstrap resampling to ensure audit results are robust and not due to small sample noise.
- **Data Integrity Guard:** Automatically handles duplicate labels, hidden whitespace, and structural inconsistencies.

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, Tailwind CSS v4, Lucide Icons, Recharts, Framer Motion.
- **Backend:** FastAPI, Pandas, Scikit-Learn, SHAP, Scipy, Pandera.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The API will be running at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Dashboard will be available at `http://localhost:5173`.

---

## 📊 Usage Guide

1. **Upload Data:** Use the dashboard to upload a CSV file (e.g., `demo_data.csv`).
2. **Configure Audit:** 
   - Select the **Protected Attribute** (e.g., `gender`).
   - Select the **Target Column** (e.g., `loan_approved`).
   - Specify the **Privileged Value** (e.g., `Male`) and **Favorable Outcome** (e.g., `1`).
3. **Analyze:** Click "Analyze Dataset" to see the Disparate Impact, Stability Score, and Root Cause Analysis.
4. **Simulate:** Use the "What-If" panel to drop high-risk proxy features and see if fairness improves.

## 🛡️ Data Integrity
FairLens includes a built-in safety layer that:
- Strips whitespace from headers.
- Removes duplicate column labels.
- Resets indices for consistent data alignment.
- Handles missing values via median/mode imputation.

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements.
