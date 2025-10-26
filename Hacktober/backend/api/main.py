"""
FastAPI Main Application
Fake News Detection System - Complete Integration
Handles all input types, runs parallel verification, returns verdict
"""

import os
import time
import asyncio
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from dotenv import load_dotenv

# Load environment variables FIRST before importing modules
load_dotenv()

# Import our services
from input_processor import process_input
from gemini_service import summarize_news, aggregate_verdict
from verification_pipeline import run_parallel_verification
from model_wrapper import load_model
from modules import generate_voice, create_whatsapp_share_from_result

# Initialize FastAPI
app = FastAPI(
    title="Fake News Detection API",
    description="AI-powered fake news detection with multiple verification sources",
    version="1.0.0"
)

# CORS Configuration - Allow all localhost ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8081",  # Added for current frontend port
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",  # Added for current frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Preload model at startup
@app.on_event("startup")
async def startup_event():
    """Load ML model at startup for faster predictions."""
    print("🚀 Starting Fake News Detection API...")
    print("=" * 60)
    try:
        load_model()
        print("✅ ML Model loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not preload model: {e}")
    print("=" * 60)
    print("🎯 API ready at http://localhost:8000")
    print("📚 Docs at http://localhost:8000/docs")
    print("=" * 60)


# Request Models
class TextDetectionRequest(BaseModel):
    """Request model for text-based detection."""
    text: str
    type: str = "text"  # "text", "url"


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "status": "online",
        "message": "Fake News Detection API",
        "version": "1.0.0",
        "endpoints": {
            "detect_text": "POST /api/detect/text",
            "detect_image": "POST /api/detect/image",
            "detect_voice": "POST /api/detect/voice",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": True,
        "timestamp": time.time()
    }


@app.post("/api/detect/text")
async def detect_text(request: TextDetectionRequest):
    """
    Detect fake news from text or URL input.
    
    Processing flow:
    1. Input to text (direct or scrape)
    2. Gemini summarization
    3. Parallel verification (model + 6 APIs)
    4. Gemini verdict aggregation
    5. Return result with confidence and references
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📥 NEW REQUEST: {request.type.upper()}")
        print(f"{'='*60}")
        
        # STEP 1: Convert input to text (1-3s)
        print("\n[STEP 1/5] Processing input...")
        input_data = {
            "type": request.type,
            "data": request.text
        }
        text, input_metadata = await process_input(input_data)
        print(f"✅ Text extracted ({len(text)} chars) in {input_metadata.get('processing_time', 0)}s")
        
        # STEP 2: Gemini summarization (2-3s)
        print("\n[STEP 2/5] Summarizing with Gemini...")
        summary_result = await summarize_news(text, timeout=3)
        gemini_summary = summary_result.get('summary', text[:500])
        print(f"✅ Summary created ({len(gemini_summary)} chars)")
        
        # STEP 3: Parallel verification (5-8s)
        print("\n[STEP 3/5] Running parallel verification...")
        verification_results = await run_parallel_verification(text, gemini_summary)
        model_result = verification_results.get('model', {})
        print(f"✅ Verification complete in {verification_results.get('execution_time', 0)}s")
        print(f"   Successful services: {verification_results.get('services_successful', 0)}/6")
        
        # STEP 4: Gemini verdict aggregation (2-3s)
        print("\n[STEP 4/5] Aggregating verdict with Gemini...")
        final_verdict = await aggregate_verdict(
            original_text=text,
            gemini_summary=gemini_summary,
            model_result=model_result,
            verification_results=verification_results,
            timeout=3
        )
        print(f"✅ Final verdict: {final_verdict.get('verdict', 'Unknown')}")
        
        # STEP 5: Prepare response (< 1s)
        print("\n[STEP 5/5] Preparing response...")
        
        # Generate WhatsApp share message with Gemini summary
        whatsapp_share = create_whatsapp_share_from_result({
            "text": gemini_summary,  # Use Gemini summary (3-5 lines) for sharing
            "prediction": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', '')
        })
        
        total_time = time.time() - start_time
        
        response = {
            "success": True,
            "verdict": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', ''),
            "key_factors": final_verdict.get('key_factors', []),
            "references": final_verdict.get('references', []),
            "query": gemini_summary,
            "isFake": final_verdict.get('verdict', '') == "Fake",
            "highlightedQuery": _highlight_suspicious_text(gemini_summary),
            "whatsapp_share": whatsapp_share,
            "metadata": {
                "input_type": request.type,
                "processing_time": round(total_time, 2),
                "services_checked": verification_results.get('services_checked', 6),
                "services_successful": verification_results.get('services_successful', 0),
                "model_prediction": model_result.get('prediction', 'N/A'),
                "model_confidence": model_result.get('confidence', {}),
                "requires_tts": input_metadata.get('requires_tts', False)
            }
        }
        
        print(f"\n✅ REQUEST COMPLETE in {total_time:.2f}s")
        print(f"   Target: 15-25s | Actual: {total_time:.2f}s")
        print(f"{'='*60}\n")
        
        return response
        
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """
    Detect fake news from image input (OCR).
    
    Accepts image file, extracts text via OCR, then processes normally.
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📥 NEW REQUEST: IMAGE")
        print(f"   Filename: {file.filename}")
        print(f"{'='*60}")
        
        # Read image bytes
        image_data = await file.read()
        
        # STEP 1: OCR to text
        print("\n[STEP 1/5] Extracting text from image...")
        input_data = {
            "type": "image",
            "data": image_data
        }
        text, input_metadata = await process_input(input_data)
        print(f"✅ Text extracted ({len(text)} chars) in {input_metadata.get('processing_time', 0)}s")
        
        # Continue with normal flow
        print("\n[STEP 2/5] Summarizing with Gemini...")
        summary_result = await summarize_news(text, timeout=3)
        gemini_summary = summary_result.get('summary', text[:500])
        
        print("\n[STEP 3/5] Running parallel verification...")
        verification_results = await run_parallel_verification(text, gemini_summary)
        model_result = verification_results.get('model', {})
        
        print("\n[STEP 4/5] Aggregating verdict with Gemini...")
        final_verdict = await aggregate_verdict(text, gemini_summary, model_result, verification_results, timeout=3)
        
        print("\n[STEP 5/5] Preparing response...")
        # Generate WhatsApp share message with Gemini summary (for image input)
        whatsapp_share = create_whatsapp_share_from_result({
            "text": gemini_summary,  # Use Gemini summary (3-5 lines) for sharing
            "prediction": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', '')
        })
        
        total_time = time.time() - start_time
        
        response = {
            "success": True,
            "verdict": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', ''),
            "key_factors": final_verdict.get('key_factors', []),
            "references": final_verdict.get('references', []),
            "query": gemini_summary,
            "isFake": final_verdict.get('verdict', '') == "Fake",
            "highlightedQuery": _highlight_suspicious_text(gemini_summary),
            "whatsapp_share": whatsapp_share,
            "metadata": {
                "input_type": "image",
                "processing_time": round(total_time, 2),
                "services_checked": verification_results.get('services_checked', 6),
                "services_successful": verification_results.get('services_successful', 0)
            }
        }
        
        print(f"\n✅ REQUEST COMPLETE in {total_time:.2f}s")
        print(f"{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect/voice")
async def detect_voice(file: UploadFile = File(...)):
    """
    Detect fake news from voice input (Speech-to-Text).
    
    Accepts audio file, transcribes to text, processes, and optionally generates TTS response.
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📥 NEW REQUEST: VOICE")
        print(f"   Filename: {file.filename}")
        print(f"{'='*60}")
        
        # Read audio bytes
        audio_data = await file.read()
        
        # STEP 1: STT to text
        print("\n[STEP 1/5] Transcribing audio...")
        input_data = {
            "type": "voice",
            "data": audio_data
        }
        text, input_metadata = await process_input(input_data)
        print(f"✅ Text transcribed ({len(text)} chars) in {input_metadata.get('processing_time', 0)}s")
        
        # Continue with normal flow
        print("\n[STEP 2/5] Summarizing with Gemini...")
        summary_result = await summarize_news(text, timeout=3)
        gemini_summary = summary_result.get('summary', text[:500])
        
        print("\n[STEP 3/5] Running parallel verification...")
        verification_results = await run_parallel_verification(text, gemini_summary)
        model_result = verification_results.get('model', {})
        
        print("\n[STEP 4/5] Aggregating verdict with Gemini...")
        final_verdict = await aggregate_verdict(text, gemini_summary, model_result, verification_results, timeout=3)
        
        print("\n[STEP 5/5] Preparing response (with TTS)...")
        
        # Generate TTS for verdict
        tts_text = f"The news has been analyzed. Verdict: {final_verdict.get('verdict', 'Uncertain')}. {final_verdict.get('description', '')}"
        tts_result = await generate_voice(tts_text)
        
        # Generate WhatsApp share message with Gemini summary (for voice input)
        whatsapp_share = create_whatsapp_share_from_result({
            "text": gemini_summary,  # Use Gemini summary (3-5 lines) for sharing
            "prediction": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', '')
        })
        
        total_time = time.time() - start_time
        
        response = {
            "success": True,
            "verdict": final_verdict.get('verdict', 'Uncertain'),
            "confidence": final_verdict.get('confidence', {"fake": 50, "real": 50}),
            "description": final_verdict.get('description', ''),
            "key_factors": final_verdict.get('key_factors', []),
            "references": final_verdict.get('references', []),
            "query": gemini_summary,
            "isFake": final_verdict.get('verdict', '') == "Fake",
            "highlightedQuery": _highlight_suspicious_text(gemini_summary),
            "whatsapp_share": whatsapp_share,
            "tts_audio": tts_result.get('audio_base64', None) if tts_result.get('success') else None,
            "metadata": {
                "input_type": "voice",
                "processing_time": round(total_time, 2),
                "services_checked": verification_results.get('services_checked', 6),
                "services_successful": verification_results.get('services_successful', 0),
                "tts_generated": tts_result.get('success', False)
            }
        }
        
        print(f"\n✅ REQUEST COMPLETE in {total_time:.2f}s")
        print(f"{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _highlight_suspicious_text(text: str) -> list:
    """
    Highlight suspicious phrases in text.
    Returns list of segments with isSuspicious flag.
    """
    suspicious_keywords = [
        'shocking', 'breaking', 'miracle', 'secret', 'doctors hate',
        'you won\'t believe', 'click here', 'amazing', 'unbelievable',
        'exclusive', 'leaked', 'banned', 'hidden truth'
    ]
    
    # Simple implementation - split by sentences
    segments = []
    words = text.split()
    
    for i, word in enumerate(words):
        is_suspicious = any(keyword in word.lower() for keyword in suspicious_keywords)
        segments.append({
            "text": word + " ",
            "isSuspicious": is_suspicious
        })
    
    return segments


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

