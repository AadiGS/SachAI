"""
OCR Text Extraction Module for Fake News Detection
Extracts text from images using Tesseract OCR with preprocessing
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    
    # Configure Tesseract path for Windows
    if sys.platform == 'win32':
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Tesseract-OCR\tesseract.exe',
        ]
        for path in possible_paths:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                break
except ImportError:
    print("⚠️ OCR dependencies not installed: pip install pytesseract Pillow")


class OCRProcessor:
    """Fast OCR processor optimized for news article images"""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    def __init__(self, tesseract_lang: str = 'eng'):
        self.tesseract_lang = tesseract_lang
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Optimize image for better OCR accuracy"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Sharpen
            image = image.filter(ImageFilter.SHARPEN)
            
            # Resize if too small (min 1000px)
            if min(image.size) < 1000:
                scale = 1000 / min(image.size)
                new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
        except Exception:
            return image
    
    def _extract_text_sync(self, image_path: Path) -> Tuple[bool, str, Optional[str]]:
        """Synchronous text extraction (called by async wrapper)"""
        try:
            image = Image.open(image_path)
            image = self.preprocess_image(image)
            
            # Extract text with optimized config
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(
                image,
                lang=self.tesseract_lang,
                config=custom_config
            )
            
            text = text.strip()
            return True, text, None
            
        except pytesseract.TesseractNotFoundError:
            return False, "", "Tesseract OCR not installed"
        except Exception as e:
            return False, "", f"OCR failed: {str(e)}"
    
    async def extract_text_from_image(self, image_path: Path) -> Dict[str, any]:
        """
        Async wrapper for OCR extraction
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with success, text, error
        """
        loop = asyncio.get_event_loop()
        success, text, error = await loop.run_in_executor(
            self.executor,
            self._extract_text_sync,
            image_path
        )
        
        return {
            "success": success,
            "text": ' '.join(text.split()) if success else "",  # Clean whitespace
            "error": error
        }
    
    async def extract_text_from_bytes(self, image_bytes: bytes, filename: str = "image.jpg") -> Dict[str, any]:
        """
        Extract text from image bytes (for API uploads)
        
        Args:
            image_bytes: Image file bytes
            filename: Original filename
            
        Returns:
            Dict with success, text, error
        """
        try:
            # Save temporarily
            temp_path = Path(f"/tmp/{filename}") if sys.platform != 'win32' else Path(f"temp_{filename}")
            temp_path.write_bytes(image_bytes)
            
            result = await self.extract_text_from_image(temp_path)
            
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
            
            return result
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Failed to process image: {str(e)}"
            }


# Singleton instance for reuse
ocr_processor = OCRProcessor()


async def process_image_to_text(image_path_or_bytes) -> str:
    """
    Simple function to extract text from image
    
    Args:
        image_path_or_bytes: Path object or bytes
        
    Returns:
        Extracted text string (empty if failed)
    """
    if isinstance(image_path_or_bytes, bytes):
        result = await ocr_processor.extract_text_from_bytes(image_path_or_bytes)
    else:
        result = await ocr_processor.extract_text_from_image(Path(image_path_or_bytes))
    
    return result.get("text", "") if result.get("success") else ""

