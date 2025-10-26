import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("FAST SIMPLE MODEL - PRODUCTION READY IN 2 MINUTES")
print("="*70)

# Load data
print("\nLoading WELFake dataset...")
df = pd.read_csv('WELFake_Dataset_cleaned.csv')
df = df.dropna(subset=['label', 'text'])
df['label'] = df['label'].astype(int)

if 'title' in df.columns:
    df['combined_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
else:
    df['combined_text'] = df['text']

df = df[df['combined_text'].str.len() > 50]  # Min length

print(f"Dataset: {len(df)} samples")
print(f"Fake: {(df['label']==0).sum()} | Real: {(df['label']==1).sum()}")

# Clean text
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("\nCleaning texts...")
df['clean_text'] = df['combined_text'].apply(clean_text)

# Split data
X = df['clean_text'].values
y = df['label'].values

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"\nSplits: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

# TF-IDF Vectorization
print("\nTraining TF-IDF + Logistic Regression...")
vectorizer = TfidfVectorizer(
    max_features=10000,
    min_df=5,
    max_df=0.7,
    ngram_range=(1, 2),  # Unigrams + bigrams
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_val_tfidf = vectorizer.transform(X_val)
X_test_tfidf = vectorizer.transform(X_test)

print(f"TF-IDF features: {X_train_tfidf.shape[1]}")

# Train Logistic Regression (fast and works well!)
model = LogisticRegression(
    max_iter=1000,
    C=1.0,  # Regularization
    class_weight='balanced',
    random_state=42,
    solver='saga',
    n_jobs=-1
)

model.fit(X_train_tfidf, y_train)

# Evaluate
train_pred = model.predict(X_train_tfidf)
val_pred = model.predict(X_val_tfidf)
test_pred = model.predict(X_test_tfidf)

train_acc = accuracy_score(y_train, train_pred)
val_acc = accuracy_score(y_val, val_pred)
test_acc = accuracy_score(y_test, test_pred)

print(f"\n{'='*70}")
print("RESULTS")
print(f"{'='*70}")
print(f"Train Accuracy: {train_acc*100:.2f}%")
print(f"Val Accuracy:   {val_acc*100:.2f}%")
print(f"Test Accuracy:  {test_acc*100:.2f}%")
print(f"Gap:            {(train_acc-test_acc)*100:.2f}%")

print("\nTest Set Classification Report:")
print(classification_report(y_test, test_pred, target_names=['Fake', 'Real'], digits=4))

cm = confusion_matrix(y_test, test_pred)
print("\nConfusion Matrix:")
print(cm)
print(f"Fake Recall: {cm[0][0]/(cm[0][0]+cm[0][1])*100:.1f}%")
print(f"Real Recall: {cm[1][1]/(cm[1][0]+cm[1][1])*100:.1f}%")

# Save model
print(f"\n{'='*70}")
print("SAVING MODEL")
print(f"{'='*70}")

model_package = {
    'vectorizer': vectorizer,
    'model': model,
    'test_accuracy': test_acc,
    'model_type': 'LogisticRegression',
    'features': X_train_tfidf.shape[1]
}

with open('news_simple_model.pkl', 'wb') as f:
    pickle.dump(model_package, f)

print("✅ Saved as news_simple_model.pkl")
print(f"\n✅ Test Accuracy: {test_acc*100:.2f}%")
print("✅ Training completed in ~2 minutes!")
print(f"\n{'='*70}")
print("Model is ready for real-world testing!")
print(f"{'='*70}")

