import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURATION (EDIT THESE LINES) ---
# 1. Ensure this file is in the same folder as your CSV dataset.
DATASET_FILE = 'AI_Human.csv' 
TEXT_COLUMN = 'text'      # Column name in your CSV with the content
LABEL_COLUMN = 'generated'    # Column name in your CSV with the label (0 or 1)

# Ensure the dataset file exists and contains the required columns
if not os.path.exists(DATASET_FILE):
    raise FileNotFoundError(f"Dataset file '{DATASET_FILE}' not found.")
else:
    with open(DATASET_FILE, 'r') as f:
        header = f.readline().strip().split(',')
        if TEXT_COLUMN not in header or LABEL_COLUMN not in header:
            raise KeyError(f"Dataset must contain columns '{TEXT_COLUMN}' and '{LABEL_COLUMN}'.")
TEST_SIZE = 0.2           # 20% of data used for testing/evaluation

# --- 1. Load the Large Training Data ---
try:
    df = pd.read_csv(DATASET_FILE)
    df = df[[TEXT_COLUMN, LABEL_COLUMN]].dropna()
    
    # Ensure the label column is numeric (0 and 1)
    df[LABEL_COLUMN] = pd.to_numeric(df[LABEL_COLUMN], errors='coerce').astype(int)
    
    print(f"Successfully loaded {len(df)} samples from {DATASET_FILE}")
    
except FileNotFoundError:
    print(f"ERROR: Dataset file '{DATASET_FILE}' not found. Please check the file name.")
    exit()
except KeyError as e:
    print(f"ERROR: Column {e} not found in the dataset. Check TEXT_COLUMN/LABEL_COLUMN in the CONFIG.")
    exit()


# --- 2. Feature Engineering & Training ---
print("\nStarting Model Training...")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    df[TEXT_COLUMN], df[LABEL_COLUMN], test_size=TEST_SIZE, random_state=42
)

# Initialize TF-IDF Vectorizer
# ngram_range=(1, 2) looks for single words and pairs of words
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000, ngram_range=(1, 2))
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Initialize and train the classifier
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# --- 3. Evaluation ---
y_pred = model.predict(X_test_vectorized)
print("\n--- Model Evaluation (on test data) ---")
print(f"Total Samples Used for Training: {len(X_train)}")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=['Human', 'AI']))

# --- 4. Save Model and Vectorizer ---
with open('ai_detector_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("\nSUCCESS: ai_detector_model.pkl and tfidf_vectorizer.pkl created.")