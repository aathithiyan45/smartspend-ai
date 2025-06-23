import spacy
from datetime import datetime
from calendar import monthrange

nlp = spacy.load("en_core_web_sm")

MONTHS = {
    "january": 1, "february": 2, "march": 3,
    "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9,
    "october": 10, "november": 11, "december": 12,
}

def extract_query_data(query):
    doc = nlp(query.lower())
    category = None
    months_found = []

    for token in doc:
        if token.pos_ == "NOUN" and token.text not in MONTHS:
            category = token.text.capitalize()
            break

    for token in doc:
        if token.text in MONTHS:
            months_found.append(token.text)

    today = datetime.today()
    year = today.year
    start_date = end_date = None

    if len(months_found) >= 2:
        start_month = MONTHS[months_found[0]]
        end_month = MONTHS[months_found[1]]
        start_date = datetime(year, start_month, 1).date()
        last_day = monthrange(year, end_month)[1]
        end_date = datetime(year, end_month, last_day).date()

    return {
        "category": category,
        "start_date": start_date,
        "end_date": end_date
    }
