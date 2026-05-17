# 🎓 SIMATS Faculty Recruitment Vacancy Tracker

A Streamlit web application to manage faculty recruitment vacancies and candidate pipeline across all SIMATS institutions.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📋 Features

| Page | Description |
|------|-------------|
| 📊 Dashboard | KPI cards, vacancy status chart, institution-wise summary |
| 📋 Vacancies | View, filter, update status, delete vacancies |
| 👤 Candidates | View pipeline, filter by stage/dept, update candidate stage |
| ➕ Add Vacancy | Form to create a new vacancy |
| ➕ Add Candidate | Form to register a new candidate against a vacancy |
| 📈 Reports | Institution report, department report, candidate funnel |

---

## 🏛️ Institutions Covered
- SIMATS Engineering
- SCAD
- SCLAS
- SPIER

---

## 💡 Notes
- Data is stored in **session state** (in-memory). For persistence, replace with SQLite or CSV file storage.
- All sample data is pre-loaded for demonstration.
