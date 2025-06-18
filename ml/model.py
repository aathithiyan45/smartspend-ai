import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'ml', 'category_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'ml', 'vectorizer.pkl')

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def predict_category(title):
    title = title.lower()
    X = vectorizer.transform([title])
    return model.predict(X)[0]
