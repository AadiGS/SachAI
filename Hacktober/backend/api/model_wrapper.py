"""
Model Wrapper for Fake News Detection
Loads and caches the trained model (news_simple_model.pkl)
Provides fast async prediction interface
"""

import pickle
import asyncio
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

# Path to trained model
MODEL_PATH = Path(__file__).parent.parent / "model" / "news_simple_model.pkl"

# Global model cache
_model_cache = None
_executor = ThreadPoolExecutor(max_workers=2)


def load_model() -> Dict:
    """Load the trained model from pickle file (called once at startup)."""
    global _model_cache
    
    if _model_cache is not None:
        return _model_cache
    
    try:
        with open(MODEL_PATH, 'rb') as f:
            model_package = pickle.load(f)
        
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
        print(f"   Model type: {model_package.get('model_type', 'Unknown')}")
        print(f"   Test accuracy: {model_package.get('test_accuracy', 'N/A')}")
        
        _model_cache = model_package
        return model_package
        
    except FileNotFoundError:
        print(f"❌ Model file not found: {MODEL_PATH}")
        raise
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise


def _predict_sync(text: str) -> Dict:
    """Synchronous prediction (runs in thread pool)."""
    model_package = load_model()
    
    vectorizer = model_package['vectorizer']
    model = model_package['model']
    
    # Transform text to TF-IDF features
    tfidf = vectorizer.transform([text])
    
    # Get prediction and probabilities
    prediction = model.predict(tfidf)[0]
    proba = model.predict_proba(tfidf)[0]
    
    # Format result
    fake_conf = float(proba[0] * 100)
    real_conf = float(proba[1] * 100)
    
    return {
        "prediction": "Real News" if prediction == 1 else "Fake News",
        "label": int(prediction),  # 0 = fake, 1 = real
        "confidence": {
            "fake": round(fake_conf, 2),
            "real": round(real_conf, 2)
        },
        "source": "ML Model (Logistic Regression + TF-IDF)",
        "model_accuracy": float(model_package.get('test_accuracy', 0.96))
    }


async def predict(text: str) -> Dict:
    """
    Async prediction interface - runs in thread pool to avoid blocking.
    
    Args:
        text: News text to verify
        
    Returns:
        Dict with:
            - prediction: "Real News" or "Fake News"
            - label: 0 (fake) or 1 (real)
            - confidence: dict with fake and real percentages
            - source: Model identifier
            - model_accuracy: Model's test accuracy
    """
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, _predict_sync, text)
        return result
        
    except Exception as e:
        print(f"⚠️ Model prediction error: {e}")
        # Return neutral result on error
        return {
            "prediction": "Uncertain",
            "label": -1,
            "confidence": {"fake": 50.0, "real": 50.0},
            "source": "ML Model (Error)",
            "error": str(e)
        }


# Preload model on import (optional - for faster first prediction)
try:
    load_model()
except Exception as e:
    print(f"⚠️ Could not preload model: {e}")
    print("   Model will be loaded on first prediction")

