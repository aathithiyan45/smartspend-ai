# SmartSpend.AI – AI-Powered Personal Expense Tracker

SmartSpend.AI is an intelligent, modern expense-tracking web application built with Django and Tailwind CSS.

It allows users to track expenses, manage budgets, analyze spending trends, and uses machine learning to automatically predict expense categories — making financial management faster and more efficient.

---

## Features

### Core Expense Management
- Add new expenses  
- Edit and update existing entries  
- Delete expenses  
- Filter expenses by date range  

### AI-Powered Automation
- Automatic category prediction using a trained Naive Bayes model  
- Predicts category based on title and description  
- Built using scikit-learn  

### Analytics & Insights
- Clean dashboard with interactive charts  
- Monthly spending summary  
- Category-wise breakdown  
- Trend visualization using Chart.js  

### Exporting & Reports
- Export expenses as PDF using ReportLab  
- Export data as CSV  
- Structured reports for financial review  

### User Interface
- Fully responsive design using Tailwind CSS  
- Clean layout focused on usability  
- Optimized and smooth navigation  

---

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Django (Python) |
| Frontend   | HTML, Tailwind CSS, Chart.js |
| Database   | SQLite (Development) |
| AI/ML      | scikit-learn (Naive Bayes), joblib |
| Exporting  | ReportLab (PDF), CSV |

---

## AI Category Prediction – How It Works

SmartSpend.AI uses a machine learning model to classify expenses into categories such as Food, Travel, Shopping, Bills, and Entertainment.

### Workflow

1. Past expenses are preprocessed and used to train a Naive Bayes text classification model.  
2. The trained model is saved using joblib.  
3. When a user enters a new expense, the system predicts the most appropriate category.  
4. The user can accept or manually modify the predicted category.  

This reduces repetitive manual categorization and improves data entry speed.

---

## Installation & Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/SmartSpend.AI.git
cd SmartSpend.AI

Create a virtual environment:

python -m venv env

Activate the virtual environment:

Mac/Linux:

source env/bin/activate

Windows:

env\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run database migrations:

python manage.py migrate

Start the development server:

python manage.py runserver
Contributing

Contributions are welcome.
Feel free to open issues, submit pull requests, or suggest improvements.

License

This project is licensed under the MIT License.


---
