import json
import pickle
import re
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("SIMPLE FAKE NEWS DETECTOR - PREDICTION")
print("="*70)

# Load model
print("\nLoading model...")
try:
    with open('news_simple_model.pkl', 'rb') as f:
        model_package = pickle.load(f)
    print("✅ Model loaded!")
except:
    print("❌ Error: news_simple_model.pkl not found!")
    print("Run: python train_simple_fast.py")
    exit(1)

vectorizer = model_package['vectorizer']
model = model_package['model']

print(f"Model type: {model_package['model_type']}")
print(f"Features: {model_package['features']:,}")
print(f"Test accuracy: {model_package['test_accuracy']*100:.2f}%")

# Clean text function
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Load input
print("\n" + "="*70)
print("LOADING INPUT")
print("="*70)

try:
    with open('input.json', 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    print(f"✅ Loaded {len(input_data)} samples")
except:
    print("❌ input.json not found!")
    exit(1)

# Extract texts
texts = []
for item in input_data:
    if isinstance(item, dict) and 'text' in item:
        texts.append(item['text'])
    elif isinstance(item, str):
        texts.append(item)

# Clean and predict
print("\nProcessing...")
cleaned_texts = [clean_text(text) for text in texts]
tfidf_features = vectorizer.transform(cleaned_texts)
predictions = model.predict(tfidf_features)
probabilities = model.predict_proba(tfidf_features)

# Prepare output
output_data = []
for text, pred, prob in zip(texts, predictions, probabilities):
    output_data.append({
        "text": text,
        "flag": int(pred),
        "prediction": "Real News" if pred == 1 else "Fake News",
        "confidence": {
            "fake": round(prob[0] * 100, 2),
            "real": round(prob[1] * 100, 2)
        }
    })

# Save
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print("RESULTS")
print("="*70)
print(f"✅ Saved to output.json")
print(f"\nPredictions: Fake={predictions.tolist().count(0)}, Real={predictions.tolist().count(1)}")

print("\nSample predictions:")
for i, item in enumerate(output_data[:3]):
    print(f"\n{i+1}. {item['text'][:80]}...")
    print(f"   → {item['prediction']} ({item['confidence']['real']}% confidence)")

print("\n" + "="*70)

