import pandas as pd
import os
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

from sklearn.svm import LinearSVC


df = pd.read_csv("data/resume_dataset.csv")
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)          # remove numbers
    text = re.sub(r'[^a-zA-Z ]', ' ', text)  # remove symbols
    text = re.sub(r'\s+', ' ', text)         # remove extra spaces
    return text

df['cleaned'] = df['resume_str'].apply(clean_text)

df = df[df['cleaned'].str.strip()!=""]

X = df['cleaned']
y = df['category']

vectorizer = TfidfVectorizer(stop_words='english',max_features=5000,ngram_range=(1,2))
x_vec = vectorizer.fit_transform(X)
X_train,X_test,y_train,y_test = train_test_split(x_vec,y,test_size=0.2,random_state=42)

model = LinearSVC()
model.fit(X_train,y_train)

y_pred = model.predict(X_test)
print("Accuracy:",accuracy_score(y_test,y_pred))

os.makedirs("model", exist_ok=True)

pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("✅ Model trained and saved!")