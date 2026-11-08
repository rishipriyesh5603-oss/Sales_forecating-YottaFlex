📊 YottaFlex AI – Sales Booking Forecasting
An end-to-end sales forecasting application designed to help businesses analyze CRM data, predict expected bookings, and evaluate different sales scenarios.
🚀 Key Features
Synthetic CRM data generation with 12 data tables.
Snapshot-safe sales forecasting.
Opportunity stage, age and activity-based probability calculations.
Downside, Base and Upside scenario analysis.
Automated data validation.
Interactive Streamlit dashboard.
FastAPI REST API integration.
Forecast results export to CSV.
🛠️ Tech Stack
Python | Pandas | NumPy | FastAPI | Streamlit | Plotly | Pytest
📁 Project Structure
data/ – Synthetic CRM datasets
src/ – Forecasting, analytics and validation logic
frontend/ – Streamlit dashboard
tests/ – Automated test cases
docs/ – Methodology and prompt history
⚙️ Installation
git clone https://github.com/rishipriyesh5603-oss/Sales_forecasting-YottaFlex.git
cd Sales_forecasting-YottaFlex
py -3.12 -m venv venv
pip install -r requirements.txt
▶️ Run Application
FastAPI:
uvicorn src.api:app --reload --port 8000
API Docs: http://localhost:8000/docs
Streamlit:
streamlit run frontend/app.py
Dashboard: http://localhost:8501
🧪 Testing
pytest -q
📌 Methodology & Limitations
The application uses a transparent, rule-based forecasting approach with synthetic CRM data. It applies scenario multipliers and opportunity-level probability adjustments. It is not a trained production machine learning model.
👨‍💻 Author
Rishi Priyesh
GitHub: https://github.com/rishipriyesh5603-oss/Sales_forecasting-YottaFlex
