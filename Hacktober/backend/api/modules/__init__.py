"""
Modules for Fake News Detection System
Provides OCR, Reddit, Twitter, Fact Check, WhatsApp Share, and other verification services
"""

from .ocr_processor import process_image_to_text, ocr_processor
from .reddit_service import search_reddit, reddit_searcher
from .twitter_service import search_twitter, twitter_analyzer
from .factcheck_service import search_factcheck, factcheck_searcher
from .whatsapp_service import (
    generate_whatsapp_share, 
    create_whatsapp_share_from_result,
    whatsapp_service
)
from .voice_service import (
    transcribe_voice,
    generate_voice,
    process_voice_complete,
    voice_processor
)
from .url_scraper_service import (
    scrape_url_to_text,
    extract_article_text,
    url_scraper
)
from .newsapi_service import (
    verify_news,
    verify_news_sync,
    search_news_api
)

__all__ = [
    'process_image_to_text',
    'ocr_processor',
    'search_reddit',
    'reddit_searcher',
    'search_twitter',
    'twitter_analyzer',
    'search_factcheck',
    'factcheck_searcher',
    'generate_whatsapp_share',
    'create_whatsapp_share_from_result',
    'whatsapp_service',
    'transcribe_voice',
    'generate_voice',
    'process_voice_complete',
    'voice_processor',
    'scrape_url_to_text',
    'extract_article_text',
    'url_scraper',
    'verify_news',
    'verify_news_sync',
    'search_news_api'
]

