SmartSpend.AI – AI-Powered Personal Expense Tracker
  
SmartSpend.AI is an intelligent, modern expense-tracking web application built with Django and Tailwind CSS.
It helps users track expenses, manage budgets, analyze spending trends, and leverages AI/ML to automatically predict expense categories — making money management faster and smarter.

✨ Features
🔹 Core Expense Management
  
➕ Add new expenses   

✏️ Edit and update existing entries

❌ Delete expenses

📅 Filter expenses by date range

🔹 AI-Powered Automation

🤖 Automatic category prediction using a trained ML model (Naive Bayes + scikit-learn)

🧠 Predicts category based on title & description

🔹 Analytics & Insights

📊 Clean dashboard with interactive charts

📅 Monthly spending summary

🗂 Category-wise breakdown

📈 Trend visualization using Chart.js

🔹 Exporting & Reports

📄 Export expenses as PDF (ReportLab)

🧾 Export as CSV

🔍 Well-formatted reports for easy review

🔹 UI & User Experience

💻 Fully responsive UI (Tailwind CSS)

🧼 Clean layout focused on simplicity

⚡ Smooth navigation with optimized components

🛠 Tech Stack
Layer	Technology
Backend	Django (Python)
Frontend	HTML, Tailwind CSS, Chart.js
Database	SQLite (Development)
AI/ML	scikit-learn (Naive Bayes), joblib
Exports	ReportLab (PDF), CSV Writer
🧠 AI Category Prediction – How It Works

SmartSpend.AI uses machine learning to intelligently classify expenses into categories such as Food, Travel, Shopping, Bills, Entertainment, etc.

🔍 Workflow:

Past expenses are preprocessed and used to train a Naive Bayes text-classification model

The model is saved using joblib

When the user enters a new expense, the system predicts the best category automatically

The user can keep or change the prediction

This makes adding expenses incredibly fast and eliminates repetitive manual work.

📸 Screenshots
🏠 Home Page

Recent expenses + filtering options


📊 Analytics Dashboard

Category-wise & monthly breakdown with charts


🚀 Installation & Setup
# Clone the repository
git clone https://github.com/yourusername/SmartSpend.AI.git
cd SmartSpend.AI

# Create virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver

🤝 Contributing

Contributions are welcome!
Feel free to open issues, submit PRs, or suggest new features.

📄 License

This project is licensed under the MIT License.
