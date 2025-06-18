import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

df = pd.read_csv('data/expenses.csv')
df['title'] = df['title'].str.lower()

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['title'])

model = MultinomialNB()
model.fit(X, df['category'])

os.makedirs('ml', exist_ok=True)
joblib.dump(model, 'ml/category_model.pkl')
joblib.dump(vectorizer, 'ml/vectorizer.pkl')
print("✅ Model trained and saved.")
