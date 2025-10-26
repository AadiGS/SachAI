"""
URL Scraper Service for Fake News Detection
Extracts clean article text from URLs using multiple methods
"""

import os
import re
import asyncio
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Requests not installed: pip install requests")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️ BeautifulSoup not installed: pip install beautifulsoup4")

try:
    from boilerpy3 import extractors
    BOILERPY3_AVAILABLE = True
except ImportError:
    BOILERPY3_AVAILABLE = False
    print("⚠️ Boilerpy3 not installed (optional): pip install boilerpy3")


logger = logging.getLogger(__name__)


class URLScraper:
    """Scrapes and extracts article text from URLs"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize URL scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
            self.available = False
            return
        
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.available = True
        
        # User agent to avoid blocks
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _extract_with_boilerpy3(self, html: str) -> Optional[str]:
        """Extract article text using boilerpy3 (best for news articles)"""
        if not BOILERPY3_AVAILABLE:
            return None
        
        try:
            extractor = extractors.ArticleExtractor()
            content = extractor.get_content(html)
            return content.strip() if content else None
        except Exception as e:
            logger.debug(f"Boilerpy3 extraction failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, html: str) -> Optional[str]:
        """Fallback extraction using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                script.decompose()
            
            # Try to find article content
            article = None
            
            # Common article selectors
            for selector in ['article', 'div[class*="article"]', 'div[class*="content"]', 
                           'div[class*="story"]', 'main']:
                article = soup.select_one(selector)
                if article:
                    break
            
            # If no article found, use body
            if not article:
                article = soup.find('body')
            
            if article:
                # Get text
                text = article.get_text(separator=' ', strip=True)
                return text
            
            return None
            
        except Exception as e:
            logger.debug(f"BeautifulSoup extraction failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove newlines and tabs
        text = text.replace('\n', ' ').replace('\t', ' ')
        
        # Remove any HTML tags that slipped through
        text = re.sub(r'<.*?>', '', text)
        
        # Consolidate multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _scrape_sync(self, url: str) -> Dict[str, Any]:
        """Synchronous scraping (called by async wrapper)"""
        try:
            # Fetch URL
            response = requests.get(
                url, 
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            html = response.text
            
            # Try boilerpy3 first (best for articles)
            content = self._extract_with_boilerpy3(html)
            
            # Fallback to BeautifulSoup
            if not content or len(content) < 100:
                content = self._extract_with_beautifulsoup(html)
            
            if not content:
                return {
                    "success": False,
                    "text": "",
                    "error": "Could not extract article content"
                }
            
            # Clean text
            cleaned_text = self._clean_text(content)
            
            if len(cleaned_text) < 50:
                return {
                    "success": False,
                    "text": "",
                    "error": "Extracted text too short (likely not an article)"
                }
            
            return {
                "success": True,
                "text": cleaned_text,
                "url": url,
                "length": len(cleaned_text),
                "error": None
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "text": "",
                "error": f"Request timeout ({self.timeout}s)"
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "text": "",
                "error": f"HTTP error: {e.response.status_code}"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "text": "",
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Scraping error: {str(e)}"
            }
    
    async def scrape_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Scrape article text from URL (async)
        
        Args:
            url: URL to scrape
            timeout: Max time in seconds
            
        Returns:
            Dict with success, text, error
        """
        if not self.available:
            return {
                "success": False,
                "text": "",
                "error": "URL scraper not available"
            }
        
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return {
                "success": False,
                "text": "",
                "error": "Invalid URL"
            }
        
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._scrape_sync, url),
                timeout=timeout
            )
            return result
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "text": "",
                "error": "Scraping timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }


# Singleton instance
url_scraper = URLScraper()


async def scrape_url_to_text(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Simple function to scrape URL to text
    
    Args:
        url: URL to scrape
        timeout: Max time in seconds
        
    Returns:
        Dict with success, text, error
    """
    return await url_scraper.scrape_url(url, timeout)


async def extract_article_text(url: str) -> str:
    """
    Extract article text from URL (returns just text)
    
    Args:
        url: URL to scrape
        
    Returns:
        Extracted text (empty string if failed)
    """
    result = await scrape_url_to_text(url)
    return result.get("text", "") if result.get("success") else ""

