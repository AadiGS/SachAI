"""
Voice Processing Service for Fake News Detection
Provides Speech-to-Text (STT) and Text-to-Speech (TTS) using ElevenLabs API
"""

import os
import base64
import io
import asyncio
import logging
from typing import Dict, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️ ElevenLabs not installed: pip install elevenlabs")

try:
    from langdetect import detect as lang_detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect not installed (optional): pip install langdetect")


logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Voice processing for speech-to-text and text-to-speech"""
    
    def __init__(self, api_key: str = None, voice_id: str = None):
        """
        Initialize Voice Processor
        
        Args:
            api_key: ElevenLabs API key (or from env)
            voice_id: ElevenLabs voice ID for TTS (or from env)
        """
        if not ELEVENLABS_AVAILABLE:
            self.available = False
            return
        
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = voice_id or os.getenv('ELEVENLABS_TTS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Default voice
        
        if not self.api_key:
            print("⚠️ ElevenLabs API key not found")
            self.available = False
            return
        
        try:
            self.client = ElevenLabs(api_key=self.api_key)
            self.executor = ThreadPoolExecutor(max_workers=2)
            self.available = True
        except Exception as e:
            print(f"⚠️ ElevenLabs initialization failed: {e}")
            self.available = False
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        if not LANGDETECT_AVAILABLE:
            return "en"
        
        try:
            return lang_detect(text)
        except Exception:
            return "en"
    
    def _stt_sync(self, audio_bytes: bytes) -> Tuple[str, str]:
        """Synchronous speech-to-text (called by async wrapper)"""
        try:
            audio_stream = io.BytesIO(audio_bytes)
            
            # Use ElevenLabs STT (Scribe model)
            response = self.client.speech_to_text.convert(
                file=audio_stream,
                model_id="scribe_v1"  # Updated: Use scribe_v1 (valid model)
            )
            
            transcript = response.text.strip()
            
            if not transcript:
                return "", "en"
            
            # Detect language
            language = self._detect_language(transcript)
            
            return transcript, language
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            return "", "en"
    
    def _tts_sync(self, text: str, language: str = "en") -> bytes:
        """Synchronous text-to-speech (called by async wrapper)"""
        try:
            # Generate audio
            audio_bytes = b""
            
            # Try generate method first
            try:
                audio_stream = self.client.generate(
                    text=text,
                    voice=self.voice_id,
                    model="eleven_turbo_v2",  # Updated: Use eleven_turbo_v2 for TTS
                    stream=False
                )
                
                # Handle different return types
                if isinstance(audio_stream, bytes):
                    audio_bytes = audio_stream
                else:
                    # Generator
                    for chunk in audio_stream:
                        if chunk:
                            audio_bytes += chunk
            
            except AttributeError:
                # Alternative method
                response = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_turbo_v2"  # Updated: Use eleven_turbo_v2 for TTS
                )
                
                for chunk in response:
                    if chunk:
                        audio_bytes += chunk
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    async def speech_to_text(self, audio_bytes: bytes, timeout: int = 10) -> Dict[str, Any]:
        """
        Convert speech to text (async)
        
        Args:
            audio_bytes: Audio file bytes
            timeout: Max time in seconds
            
        Returns:
            Dict with text, language, success
        """
        if not self.available:
            return {
                "success": False,
                "text": "",
                "language": "en",
                "error": "Voice service not available"
            }
        
        try:
            loop = asyncio.get_event_loop()
            text, language = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._stt_sync, audio_bytes),
                timeout=timeout
            )
            
            if not text:
                return {
                    "success": False,
                    "text": "",
                    "language": "en",
                    "error": "No speech detected"
                }
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "error": None
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "text": "",
                "language": "en",
                "error": "STT timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "language": "en",
                "error": str(e)
            }
    
    async def text_to_speech(self, text: str, language: str = "en", 
                            timeout: int = 10) -> Dict[str, Any]:
        """
        Convert text to speech (async)
        
        Args:
            text: Text to convert
            language: Language code (optional, for future use)
            timeout: Max time in seconds
            
        Returns:
            Dict with audio_base64, success, error
        """
        if not self.available:
            return {
                "success": False,
                "audio_base64": None,
                "error": "Voice service not available"
            }
        
        try:
            loop = asyncio.get_event_loop()
            audio_bytes = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._tts_sync, text, language),
                timeout=timeout
            )
            
            if not audio_bytes:
                return {
                    "success": False,
                    "audio_base64": None,
                    "error": "TTS returned no audio"
                }
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "audio_size": len(audio_bytes),
                "error": None
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "audio_base64": None,
                "error": "TTS timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "audio_base64": None,
                "error": str(e)
            }
    
    async def process_voice_input(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Complete voice processing: STT only
        (TTS will be called separately after verification)
        
        Args:
            audio_bytes: Audio file bytes
            
        Returns:
            Dict with transcribed text and language
        """
        stt_result = await self.speech_to_text(audio_bytes)
        return stt_result


# Singleton instance
voice_processor = VoiceProcessor()


async def transcribe_voice(audio_bytes: bytes) -> Dict[str, Any]:
    """
    Simple function to transcribe voice to text
    
    Args:
        audio_bytes: Audio file bytes
        
    Returns:
        Dict with text, language, success
    """
    return await voice_processor.speech_to_text(audio_bytes)


async def generate_voice(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Simple function to generate voice from text
    
    Args:
        text: Text to speak
        language: Language code
        
    Returns:
        Dict with audio_base64, success
    """
    return await voice_processor.text_to_speech(text, language)


async def process_voice_complete(audio_bytes: bytes, verification_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete voice workflow: STT → Verify → TTS
    
    Args:
        audio_bytes: Input audio
        verification_result: Result from fake news detection
        
    Returns:
        Dict with transcription, verification, and response audio
    """
    # Step 1: Transcribe
    stt_result = await transcribe_voice(audio_bytes)
    
    if not stt_result['success']:
        return {
            "success": False,
            "error": stt_result['error']
        }
    
    # Step 2: Format verification result for TTS
    prediction = verification_result.get("prediction", "Unknown")
    description = verification_result.get("description", "No description")
    
    # Create spoken response
    if "fake" in prediction.lower():
        response_text = f"This news is fake. {description}"
    else:
        response_text = f"This news is verified as real. {description}"
    
    # Step 3: Generate TTS
    tts_result = await generate_voice(response_text, stt_result['language'])
    
    # Step 4: Return complete result
    return {
        "success": True,
        "transcribed_text": stt_result['text'],
        "detected_language": stt_result['language'],
        "verification": verification_result,
        "response_text": response_text,
        "response_audio": tts_result.get('audio_base64')
    }

