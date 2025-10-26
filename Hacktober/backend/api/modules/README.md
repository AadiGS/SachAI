# Fake News Detection - Verification Modules

This directory contains the verification modules extracted and organized from your provided code.

## 📁 Module Organization

```
backend/api/modules/
├── __init__.py              # Module exports
├── ocr_processor.py         # Image to text extraction (OCR)
├── reddit_service.py        # Reddit news search
├── twitter_service.py       # Twitter/X verification with fallback
├── factcheck_service.py     # Google Fact Check API + Gemini
├── whatsapp_service.py      # WhatsApp share message generator
├── voice_service.py         # Voice STT/TTS processor
├── url_scraper_service.py   # URL to text extractor
├── newsapi_service.py       # News API verification (NEW!)
├── share_page.html          # WhatsApp share UI page
├── voice_interface.html     # Voice recording interface
└── README.md               # This file
```

## 🔧 Modules Overview

### 1. OCR Processor (`ocr_processor.py`)
**Purpose:** Extract text from news images

**Features:**
- Tesseract OCR with image preprocessing
- Async-ready for fast processing
- Supports multiple image formats (JPG, PNG, etc.)
- Auto-contrast and sharpening for better accuracy

**Usage:**
```python
from modules.ocr_processor import process_image_to_text

text = await process_image_to_text(image_path)
# or with bytes
text = await process_image_to_text(image_bytes)
```

**Requirements:**
- `pytesseract` + `Pillow`
- Tesseract OCR installed on system

---

### 2. Reddit Service (`reddit_service.py`)
**Purpose:** Search Reddit for news discussions

**Features:**
- Searches relevant subreddits (news, worldnews, politics, etc.)
- Filters by label (real/fake news subreddits)
- Keyword extraction for better results
- Async with timeout protection

**Usage:**
```python
from modules.reddit_service import search_reddit

results = await search_reddit(
    text="news article text",
    label=1,  # 1=real, 0=fake, None=neutral
    limit=5
)
```

**Requirements:**
- `praw` (Python Reddit API Wrapper)
- Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)

---

### 3. Twitter Service (`twitter_service.py`)
**Purpose:** Verify news on Twitter/X

**Features:**
- Twitter API v2 integration
- Web scraping fallback (Tavily) when rate-limited
- Searches Indian news domains
- URL validation (filters out topic/tag pages)
- Async with timeout protection

**Usage:**
```python
from modules.twitter_service import search_twitter

results = await search_twitter(
    text="news article text",
    label=1,  # 1=real, 0=fake, None=neutral
    limit=5
)
```

**Requirements:**
- `tweepy` (Twitter API)
- `tavily-python` (Web scraping fallback)
- Twitter API credentials + Tavily API key

---

### 4. Fact Check Service (`factcheck_service.py`)
**Purpose:** Verify claims using Google Fact Check API

**Features:**
- Google Fact Check Tools API integration
- Gemini AI to extract verifiable claims
- Gemini AI to select top 5 most relevant sources
- Async with timeout protection
- Returns fact-check ratings and publisher info

**Usage:**
```python
from modules.factcheck_service import search_factcheck

results = await search_factcheck(
    text="news article text",
    timeout=8
)
```

**Requirements:**
- `requests` (HTTP client)
- `google-generativeai` (Gemini AI)
- Google Fact Check API key + Gemini API key

---

### 5. WhatsApp Share Service (`whatsapp_service.py`)
**Purpose:** Generate WhatsApp share messages and links

**Features:**
- Format verification results as WhatsApp messages
- Generate wa.me share URLs
- Customizable brand name
- Truncates long text automatically
- Supports direct phone sharing

**Usage:**
```python
from modules.whatsapp_service import generate_whatsapp_share

share_data = generate_whatsapp_share(
    text="News article text here",
    is_fake=False,
    description="Verified by multiple sources"
)

print(share_data['share_url'])  # WhatsApp share link
print(share_data['formatted_message'])  # Formatted message
```

**Or from verification result:**
```python
from modules.whatsapp_service import create_whatsapp_share_from_result

result = {
    "text": "News article",
    "prediction": "Real News",
    "description": "Verified",
    "confidence": {"real": 85.5}
}

share_data = create_whatsapp_share_from_result(result)
```

**Requirements:**
- No external dependencies (uses built-in urllib)

---

### 6. Voice Service (`voice_service.py`)
**Purpose:** Speech-to-Text and Text-to-Speech processing

**Features:**
- Speech-to-Text (STT) using ElevenLabs API
- Text-to-Speech (TTS) using ElevenLabs API
- Language detection (auto-detect from speech)
- Async with timeout protection
- Complete voice workflow (voice → text → verify → voice response)

**Usage:**
```python
from modules.voice_service import transcribe_voice, generate_voice

# Speech to text
stt_result = await transcribe_voice(audio_bytes)
print(f"Text: {stt_result['text']}")
print(f"Language: {stt_result['language']}")

# Text to speech
tts_result = await generate_voice("This news is fake")
audio_base64 = tts_result['audio_base64']
```

**Complete workflow:**
```python
from modules.voice_service import process_voice_complete

result = await process_voice_complete(
    audio_bytes=audio_data,
    verification_result={"prediction": "Fake News", "description": "..."}
)

# Returns transcription + verification + voice response
```

**Requirements:**
- `elevenlabs` (ElevenLabs API)
- `langdetect` (Optional: language detection)
- ElevenLabs API key

---

### 7. URL Scraper Service (`url_scraper_service.py`)
**Purpose:** Extract article text from URLs

**Features:**
- Scrapes article content from news URLs
- Uses boilerpy3 for clean article extraction
- BeautifulSoup fallback for non-standard sites
- Removes ads, navigation, and clutter
- Async with timeout protection
- User-agent spoofing to avoid blocks

**Usage:**
```python
from modules.url_scraper_service import scrape_url_to_text

# Get full result with metadata
result = await scrape_url_to_text("https://news-site.com/article")
print(f"Success: {result['success']}")
print(f"Text: {result['text']}")

# Or just get the text directly
from modules.url_scraper_service import extract_article_text
text = await extract_article_text("https://news-site.com/article")
```

**Requirements:**
- `requests` (HTTP client)
- `beautifulsoup4` (HTML parsing)
- `lxml` (Parser)
- `boilerpy3` (Article extraction - optional but recommended)

---

### 8. News API Service (`newsapi_service.py`)
**Purpose:** Verify news by searching credible sources via News API

**Features:**
- Searches 70,000+ news sources worldwide
- Focuses on trusted sources (BBC, Reuters, AP, CNN, NYT, etc.)
- Analyzes article sentiment (confirms vs debunks)
- Majority vote consensus for credibility
- Async with 8-second timeout
- Returns top 5 most relevant articles

**Usage:**
```python
from modules.newsapi_service import verify_news

# Verify news claim
result = await verify_news("Scientists discover new planet")

# Result contains:
# {
#   'label': 0 or 1,              # 0=fake, 1=real
#   'confidence': 0.0-1.0,         # confidence score
#   'relevant_links': [...]        # top 5 articles
# }

print(f"Label: {result['label']}")
print(f"Confidence: {result['confidence']}")
for link in result['relevant_links']:
    print(f"  {link['source']}: {link['title']}")
```

**Credibility Logic:**
1. Extracts keywords from news text
2. Searches News API for related articles (last 30 days)
3. Analyzes each article's stance:
   - Debunking indicators: "hoax", "misinformation", "false claim"
   - Confirming indicators: "confirms", "announces", "verified"
   - Special handling for fact-checking sites (Snopes, PolitiFact)
4. Majority vote determines verdict
5. Confidence based on vote ratio

**Trusted Sources (22 major outlets):**
- BBC, Reuters, AP News, CNN, NY Times, The Guardian
- Washington Post, Bloomberg, NPR, WSJ, Al Jazeera
- CBS, NBC, Forbes, Time, USA Today, The Economist
- Snopes, PolitiFact, FactCheck.org

**Requirements:**
- `aiohttp` (async HTTP client)
- `python-dotenv` (environment variables)
- News API key (free tier: 100 requests/day)

---

## 🔑 Environment Variables

Create a `.env` file in `backend/api/`:

```env
# Reddit
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Twitter/X
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret

# Tavily (Web Scraping Fallback)
TAVILY_API_KEY=your_tavily_key

# Gemini AI
GEMINI_API_KEY=your_gemini_key

# News API
NEWS_API_KEY=your_news_api_key

# Google Fact Check API
GOOGLE_FACTCHECK_API_KEY=your_google_factcheck_key

# ElevenLabs Voice API
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_TTS_VOICE_ID=your_voice_id  # Optional (has default)
```

---

## ⚡ Key Optimizations

### Async-First Design
All modules use `asyncio` for non-blocking I/O:
- OCR runs in thread executor
- Reddit/Twitter have async wrappers
- Enables parallel processing (all APIs run simultaneously)

### Timeout Protection
Every module has timeout limits (default 8 seconds):
```python
results = await search_twitter(text, timeout=8)
```

### Graceful Degradation
- Twitter falls back to web scraping if rate-limited
- Missing credentials skip that module (doesn't break the system)
- Empty results return empty list (no errors)

### Smart Filtering
- Twitter: Filters out topic/tag pages, only returns articles
- Reddit: Sorts by engagement (score × upvote_ratio)
- OCR: Preprocesses images for better accuracy

---

## 🧪 Testing Modules

Test individual modules:

```python
import asyncio
from modules import search_reddit, search_twitter, process_image_to_text

async def test():
    # Test Reddit
    reddit_results = await search_reddit("climate change", label=1, limit=5)
    print(f"Reddit: {reddit_results['count']} results")
    
    # Test Twitter
    twitter_results = await search_twitter("climate change", label=1, limit=5)
    print(f"Twitter: {twitter_results['count']} results")
    
    # Test Fact Check
    factcheck_results = await search_factcheck("climate change")
    print(f"Fact Check: {factcheck_results['count']} results")
    
    # Test OCR
    text = await process_image_to_text("test_image.jpg")
    print(f"OCR: {len(text)} characters extracted")

asyncio.run(test())
```

---

## 📦 Installation

Install all dependencies:

```bash
cd backend/api
pip install -r requirements.txt
```

Install Tesseract OCR (for Windows):
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or it will auto-detect common locations

---

## 🔄 Next Steps

1. ✅ **Modules Organized** (DONE)
2. ⏳ Create FastAPI integration (`main.py`)
3. ⏳ Add model wrapper (`model_wrapper.py`)
4. ⏳ Implement Gemini service (`gemini_service.py`)
5. ⏳ Create parallel verification (`verification_services.py`)
6. ⏳ Add input processors (`input_processors.py`)
7. ⏳ Connect frontend to backend

---

## 🎯 Integration-Ready

These modules are **production-ready** and optimized for:
- ✅ Parallel processing (all run simultaneously)
- ✅ Timeout protection (8s limit per module)
- ✅ Error handling (graceful degradation)
- ✅ FastAPI integration (async-compatible)
- ✅ 15-25 second target (fast responses)

**Status:** Ready for FastAPI integration! 🚀

