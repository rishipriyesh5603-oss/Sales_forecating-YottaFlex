# 📊 YottaFlex AI – Sales Booking Forecast

An end-to-end sales forecasting application designed to help businesses analyze CRM data, predict expected bookings, and evaluate different sales scenarios.

## 🚀 Key Features
- Synthetic CRM data generation with 12 data tables.
- Snapshot-safe sales forecasting.
- Downside, Base and Upside scenario analysis.
- Opportunity-level probability calculations.
- Automated data validation.
- Interactive Streamlit dashboard.
- FastAPI REST API integration.
- Forecast results export to CSV.

## 🛠️ Tech Stack
- Python, Pandas, NumPy
- FastAPI, Streamlit
- Plotly
- Pytest

## 📂 Project Structure
- `data/` – Synthetic CRM datasets
- `docs/` – Methodology and documentation
- `frontend/` – Streamlit dashboard
- `src/` – Core forecasting, analytics, API and validation
- `tests/` – Automated tests

## ▶️ Run Locally

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Generate datasets:**
```bash
python run.py
```

**Start FastAPI:**
```bash
uvicorn src.api:app --reload --port 8000
```

**Start Streamlit:**
```bash
streamlit run frontend/app.py
```

API Documentation: `http://localhost:8000/docs`

Dashboard: `http://localhost:8501`

## 🧪 Testing
```bash
pytest -q
```

## ⚠️ Methodology & Limitations

Uses a transparent, rule-based forecasting approach with synthetic CRM data. It is not a trained production machine learning model. Real historical CRM outcomes are required for production calibration.

## 👨‍💻 Author
**Rishi Priyesh**

GitHub: [Sales Forecasting – YottaFlex](https://github.com/rishipriyesh5603-oss/Sales_forecasting-YottaFlex)
