# 💸 SmartSpend.AI – AI-Powered Expense Tracker

SmartSpend.AI is a powerful and intelligent expense tracker web app built with Django and Tailwind CSS. It simplifies budgeting, tracks expenses, predicts categories using AI/ML, and visualizes your spending trends with beautiful charts.

---

## 🚀 Features

✅ Add, edit, and delete expenses  
✅ AI-based automatic category prediction  
✅ Clean dashboard with charts and trend analysis  
✅ Category-wise and monthly analytics  
✅ Filter expenses by date range  
✅ Export expenses to CSV or PDF  
✅ Responsive and intuitive UI (Tailwind CSS)

---

## 🛠 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, Tailwind CSS, Chart.js
- **Database:** SQLite (Dev)
- **ML Model:** Trained with scikit-learn (joblib)
- **Exporting:** ReportLab (PDF), CSV Writer

---

## 📸 Screenshots

### 🏠 Home Page
Displays all recent expenses with filtering support  
![Home Page](screenshots/home.png)

### 📊 Stats Dashboard
Shows monthly and category-wise spending with graphs  
![Stats Page](screenshots/stats.png)

---

## 🧠 AI Category Prediction

SmartSpend.AI predicts the category of an expense based on the **title/description** using a trained `Naive Bayes` model saved with `joblib`.  
Training happens offline using past expenses and is integrated during form submission.

---


