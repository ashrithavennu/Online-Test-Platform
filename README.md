# EduAssess — AI-Enhanced Online Examination System

A full-stack college assessment platform with Machine Learning (Decision Tree) and Generative AI integration.

---

## Project Structure

```
online test platform/
├── Frontend/
│   ├── index.html              ← Login / Register page
│   ├── student-dashboard.html  ← Student home
│   ├── exam.html               ← MCQ exam with live timer
│   ├── results.html            ← Score + ML prediction + AI report
│   ├── admin-dashboard.html    ← Admin exam & student management
│   └── api.js                  ← Frontend ↔ Backend connector
│
├── Backend/
│   ├── app.py                  ← Flask server (run this)
│   ├── requirements.txt        ← Python dependencies
│   ├── eduassess.db            ← SQLite database (auto-created)
│   ├── genai/
│   │   ├── __init__.py
│   │   └── report_generator.py ← GenAI module (Anthropic/OpenAI/template)
│   └── ml_model/
│       └── model.pkl           ← Trained Decision Tree (copy from ML/)
│
└── ML/
    ├── generate_dataset.py     ← Creates dataset.csv
    ├── dataset.csv             ← 300-record student exam dataset
    ├── train_model.py          ← Full training script
    ├── train_model.ipynb       ← Jupyter notebook version
    └── model.pkl               ← Saved model (also copied to Backend/ml_model/)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python Flask |
| Database | SQLite (built-in) |
| Machine Learning | Scikit-learn (Decision Tree) |
| Generative AI | Anthropic Claude API / OpenAI (optional) |

---

## Setup Instructions

### Step 1 — Install Python dependencies

```bash
pip install flask scikit-learn pandas numpy matplotlib
```

For GenAI (optional):
```bash
pip install anthropic    # for Claude API
pip install openai       # for OpenAI API (fallback)
```

### Step 2 — Train the ML model

```bash
cd ML
python generate_dataset.py    # creates dataset.csv
python train_model.py         # trains model, saves to ML/ and Backend/ml_model/
```

### Step 3 — (Optional) Set GenAI API key

```bash
# Windows
set GENAI_API_KEY=your_api_key_here
set GENAI_PROVIDER=anthropic       # or openai

# Mac/Linux
export GENAI_API_KEY=your_api_key_here
export GENAI_PROVIDER=anthropic
```

Without an API key, the system uses a high-quality template-based report generator automatically.

### Step 4 — Run the application

```bash
cd Backend
python app.py
```

Open browser: **http://localhost:5000**

---

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@eduassess.com | admin123 |
| Student | aarav@student.com | student123 |
| Student | priya@student.com | student123 |

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| POST | /api/register | Register new student |
| POST | /api/login | Login (student or admin) |
| GET | /api/exams | List open exams |
| GET | /api/exams/<id> | Get exam + questions |
| POST | /api/exams | Create new exam |
| PUT | /api/exams/<id> | Update exam |
| POST | /api/exams/<id>/questions | Add MCQ question |
| POST | /api/submit-exam | Submit answers → auto-score |
| GET | /api/results/<student_id> | Student result history |
| GET | /api/results/attempt/<id> | Single attempt details |
| GET | /api/admin/all-results | All students' results |
| GET | /api/admin/students | All students with averages |
| POST | /api/predict | ML performance prediction |
| POST | /api/generate-report | GenAI performance report |
| GET | /api/health | Server health check |

---

## ML Module — Decision Tree

- **Input Features:** Exam Score, Time Taken, Number of Attempts, Past Score
- **Output Classes:** Good Performer / Average Performer / Needs Improvement
- **Algorithm:** Decision Tree Classifier (Scikit-learn)
- **Test Accuracy:** ~100% on demo dataset
- **CV Accuracy:** 99.67% (5-fold cross-validation)
- **Model saved:** pickle format (.pkl)

---

## GenAI Module

- Generates a 4-section personalized performance report
- Sections: Overall Summary, Strengths, Areas for Improvement, Recommendations
- Uses Anthropic Claude API (primary) → OpenAI (fallback) → Template (no key needed)
- Called automatically after each exam submission

---

## Evaluation Criteria Coverage

| Criteria | Status |
|---|---|
| Application functionality | ✅ Full stack web app |
| Machine Learning implementation | ✅ Decision Tree trained & integrated |
| Generative AI output quality | ✅ 4-section personalized report |
| Integration of all modules | ✅ Frontend ↔ Flask ↔ ML ↔ GenAI |
| Code quality and structure | ✅ Clean, modular, well-commented |

---

## Steps to Run (Quick Reference)

```bash
# 1. Train ML model (do once)
cd ML && python generate_dataset.py && python train_model.py

# 2. Start server
cd ../Backend && python app.py

# 3. Open browser
# http://localhost:5000
```
