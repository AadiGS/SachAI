"""
Input Processor
Handles all input types: text, URL, image, voice
Converts everything to text for verification pipeline
"""

import asyncio
from typing import Dict, Tuple
from modules import (
    process_image_to_text,
    scrape_url_to_text,
    transcribe_voice
)


async def process_input(input_data: Dict) -> Tuple[str, Dict]:
    """
    Process input and convert to text.
    
    Args:
        input_data: Dict with:
            - type: "text" | "url" | "image" | "voice"
            - data: The actual input (text string, URL, image bytes, audio bytes)
            
    Returns:
        Tuple of (text_content, metadata)
    """
    input_type = input_data.get("type", "text")
    data = input_data.get("data", "")
    
    print(f"📥 Processing input type: {input_type}")
    
    if input_type == "text":
        return await _process_text(data)
    elif input_type == "url":
        return await _process_url(data)
    elif input_type == "image":
        return await _process_image(data)
    elif input_type == "voice":
        return await _process_voice(data)
    else:
        raise ValueError(f"Unknown input type: {input_type}")


async def _process_text(text: str) -> Tuple[str, Dict]:
    """Process direct text input."""
    if not text or not text.strip():
        raise ValueError("Empty text provided")
    
    return text.strip(), {
        "input_type": "text",
        "processing_time": 0,
        "success": True
    }


async def _process_url(url: str) -> Tuple[str, Dict]:
    """Process URL input - scrape and extract text."""
    import time
    start_time = time.time()
    
    if not url or not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL provided")
    
    print(f"🌐 Scraping URL: {url}")
    
    try:
        # Use the URL scraper module
        result = await scrape_url_to_text(url, timeout=8)
        
        if result.get('success') and result.get('text'):
            text = result['text']
            processing_time = time.time() - start_time
            
            return text, {
                "input_type": "url",
                "source_url": url,
                "processing_time": round(processing_time, 2),
                "success": True,
                "title": result.get('title', ''),
                "word_count": len(text.split())
            }
        else:
            error = result.get('error', 'Unknown error')
            raise Exception(f"URL scraping failed: {error}")
            
    except Exception as e:
        print(f"❌ URL processing error: {e}")
        raise ValueError(f"Could not extract text from URL: {str(e)}")


async def _process_image(image_data) -> Tuple[str, Dict]:
    """Process image input - OCR to extract text."""
    import time
    start_time = time.time()
    
    if not image_data:
        raise ValueError("No image data provided")
    
    print(f"🖼️ Processing image with OCR...")
    
    try:
        # Use the OCR module
        text = await process_image_to_text(image_data)
        
        if not text or len(text.strip()) < 10:
            raise Exception("Could not extract sufficient text from image")
        
        processing_time = time.time() - start_time
        
        return text, {
            "input_type": "image",
            "processing_time": round(processing_time, 2),
            "success": True,
            "extracted_length": len(text),
            "word_count": len(text.split())
        }
        
    except Exception as e:
        print(f"❌ Image processing error: {e}")
        raise ValueError(f"Could not extract text from image: {str(e)}")


async def _process_voice(audio_data) -> Tuple[str, Dict]:
    """Process voice input - Speech-to-Text."""
    import time
    start_time = time.time()
    
    if not audio_data:
        raise ValueError("No audio data provided")
    
    print(f"🎤 Processing voice with STT...")
    
    try:
        # Use the voice module for transcription
        result = await transcribe_voice(audio_data)
        
        if result.get('success') and result.get('text'):
            text = result['text']
            processing_time = time.time() - start_time
            
            return text, {
                "input_type": "voice",
                "processing_time": round(processing_time, 2),
                "success": True,
                "language": result.get('language', 'en'),
                "word_count": len(text.split()),
                "requires_tts": True  # Flag to trigger TTS for response
            }
        else:
            error = result.get('error', 'Unknown error')
            raise Exception(f"Voice transcription failed: {error}")
            
    except Exception as e:
        print(f"❌ Voice processing error: {e}")
        raise ValueError(f"Could not transcribe audio: {str(e)}")


# Test function
async def test_input_processor():
    """Test input processor with different types."""
    
    # Test text
    print("Testing text input...")
    text_input = {
        "type": "text",
        "data": "Breaking news: Scientists discover new planet"
    }
    text, metadata = await process_input(text_input)
    print(f"✅ Text: {text[:50]}...")
    print(f"   Metadata: {metadata}")
    
    # Test URL (mock)
    print("\nTesting URL input...")
    url_input = {
        "type": "url",
        "data": "https://example.com/article"
    }
    try:
        text, metadata = await process_input(url_input)
        print(f"✅ Extracted: {text[:50]}...")
        print(f"   Metadata: {metadata}")
    except Exception as e:
        print(f"⚠️ URL test skipped: {e}")


if __name__ == "__main__":
    asyncio.run(test_input_processor())

