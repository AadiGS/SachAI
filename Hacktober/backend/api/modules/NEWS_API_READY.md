# ✅ News API Module - Integration Complete

## 📦 Module Saved

**Location:** `backend/api/modules/newsapi_service.py`

**Status:** ✅ Ready for Integration

---

## 🎯 What This Module Does

Verifies news authenticity by searching 70,000+ news sources via News API and analyzing credibility based on:

1. **Keyword Extraction** - Identifies key terms from news text
2. **Source Search** - Finds relevant articles from last 30 days
3. **Sentiment Analysis** - Determines if articles confirm or debunk the claim
4. **Consensus Vote** - Majority vote from top 5 articles determines verdict
5. **Confidence Scoring** - Based on vote ratio and source trustworthiness

---

## 🔧 Key Features

### ✅ Async-Ready for Pipeline
- Fully asynchronous using `aiohttp`
- 8-second timeout (fits 15-25s total pipeline)
- Non-blocking parallel execution

### ✅ Smart Analysis
- Analyzes article titles and descriptions for stance
- Special handling for fact-checking sites (Snopes, PolitiFact, FactCheck.org)
- Keyword relevance matching
- Source trust scoring

### ✅ 22 Trusted Sources
BBC, Reuters, AP News, CNN, NY Times, The Guardian, Washington Post, Bloomberg, NPR, WSJ, Al Jazeera, CBS, NBC, Forbes, Time, USA Today, The Economist, Snopes, PolitiFact, FactCheck.org, and more!

### ✅ Graceful Degradation
- Returns empty results if API fails
- No crashes on timeout
- Handles missing API key gracefully

---

## 📊 Output Format

```json
{
  "label": 0,                    // 0 = FAKE, 1 = REAL
  "confidence": 0.85,            // 0.0-1.0 confidence score
  "relevant_links": [
    {
      "title": "Article headline",
      "url": "https://example.com/article",
      "source": "BBC News",
      "published": "2025-10-25T10:00:00Z"
    }
    // ... up to 5 articles
  ]
}
```

---

## 🚀 Usage

### Async (Recommended for Pipeline)
```python
from modules.newsapi_service import verify_news

result = await verify_news("Scientists discover new planet", timeout=8)

print(f"Label: {result['label']}")         # 0 or 1
print(f"Confidence: {result['confidence']}")  # 0.0-1.0
print(f"Links: {len(result['relevant_links'])}")  # Top 5
```

### Synchronous (For Testing)
```python
from modules.newsapi_service import verify_news_sync

result = verify_news_sync("Your news text here")
```

---

## 🔑 Environment Variable Required

Add to `backend/api/.env`:

```env
NEWS_API_KEY=your_news_api_key_here
```

**Get API Key:**
- Visit: https://newsapi.org/
- Free tier: 100 requests/day
- Sufficient for testing and moderate use

---

## 🧠 How It Works

### 1. Keyword Extraction
```
Input: "Scientists discover new planet in solar system"
Keywords: "scientists discover planet solar system"
```

### 2. News API Search
- Searches last 30 days of articles
- Returns up to 10 most relevant
- Sorted by relevancy score

### 3. Sentiment Analysis per Article

**Debunking Indicators (→ Fake):**
- "debunk", "hoax", "misinformation", "false claim"
- "fake news", "baseless", "unfounded"

**Confirming Indicators (→ Real):**
- "confirms", "announces", "verified"
- "investigation", "officials say", "breaking"

### 4. Majority Vote
```
Example:
  ✓ BBC News: Reports as real
  ✓ Reuters: Reports as real
  ✗ Snopes: Debunks claim
  ✓ CNN: Reports as real
  ✓ NYT: Reports as real

Result: 4/5 confirm → REAL (confidence: 0.80)
```

### 5. Special Rules

**Fact-Checking Sites:**
- If Snopes/PolitiFact uses debunking language → Counts as FAKE vote
- If they report without debunking → Counts as REAL vote

**Relevance Check:**
- Must match at least 2 keywords to be considered relevant
- Higher keyword matches = more weight in decision

---

## 📈 Confidence Calculation

```python
if real_votes > fake_votes:
    label = 1  # REAL
    confidence = real_votes / total_votes
    # Example: 4/5 = 0.80

elif fake_votes > real_votes:
    label = 0  # FAKE
    confidence = fake_votes / total_votes
    # Example: 3/5 = 0.60

else:  # Tie
    # Check if 3+ from trusted sources
    if trusted_count >= 3:
        label = 1
        confidence = 0.6
    else:
        label = 0
        confidence = 0.5
```

---

## 🔄 Integration with Main Pipeline

```python
# In verification_pipeline.py
from modules.newsapi_service import verify_news

async def run_verification_pipeline(text: str):
    # Run all services in parallel
    results = await asyncio.gather(
        verify_news(text, timeout=8),        # News API ← NEW!
        search_reddit(text, timeout=8),
        search_twitter(text, timeout=8),
        search_factcheck(text, timeout=8),
        # ... other services
    )
    
    news_api_result = results[0]
    
    # Send to Gemini for final aggregation
    final_verdict = await gemini_aggregate(
        model_prediction=model_result,
        news_api=news_api_result,           # Include News API
        reddit=reddit_result,
        twitter=twitter_result,
        factcheck=factcheck_result,
        # ...
    )
```

---

## 🎯 Why This Matters

### Before News API:
- Twitter: Limited to social media posts
- Reddit: Discussion-based, not authoritative
- Fact Check: Only covers already debunked claims

### With News API:
- ✅ Access to major news outlets
- ✅ Recent coverage (last 30 days)
- ✅ Authoritative sources (BBC, Reuters, AP)
- ✅ Broader coverage of breaking news
- ✅ Better for recent/emerging claims

---

## 🧪 Testing

### Run Standalone Test:
```bash
cd backend/api/modules
python newsapi_service.py
```

### Example Test Output:
```
🚀 Testing News API Service
Query: Scientists discover new planet in solar system
============================================================

Label: 0 (FAKE)
Confidence: 60.0%

Relevant Links: 5
  1. Snopes: Debunking: No New Planet Discovered...
  2. NASA: What We Know About the Solar System...
  3. Space.com: Why Claims of New Planet Are Premature...
```

---

## 📊 Module Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~310 lines |
| **Original** | 346 lines |
| **Reduction** | ~10% (cleaned, async-converted) |
| **Functions** | 6 main functions |
| **Dependencies** | 2 (`aiohttp`, `python-dotenv`) |
| **Timeout** | 8 seconds (configurable) |
| **Free Tier** | 100 requests/day |

---

## ✅ Integration Checklist

- [x] Module extracted from zip
- [x] Converted to async
- [x] Added timeout protection
- [x] Simplified and cleaned
- [x] Added to `__init__.py` exports
- [x] Documented in README.md
- [x] Tested independently
- [ ] Integrated into main pipeline
- [ ] Added to Gemini aggregation
- [ ] Tested end-to-end

---

## 🚀 What's Next

1. **Add to Pipeline** - Include in parallel verification
2. **Gemini Integration** - Add News API results to final aggregation
3. **Weight Assignment** - Determine News API's influence on final verdict
4. **Testing** - Verify with real news examples

---

## 📝 Notes

- **API Limits:** Free tier = 100 requests/day
- **Rate Limiting:** Built-in (8s timeout prevents abuse)
- **Fallback:** Returns empty results if fails (doesn't break pipeline)
- **Coverage:** Best for international news, major events
- **Weakness:** May not cover very recent (< 1 hour) or very local news

---

## 🎉 Status

**Module:** ✅ Complete and Integration-Ready  
**Documentation:** ✅ Complete  
**Testing:** ✅ Standalone test works  
**Pipeline Integration:** ⏳ Pending (next step)

**Total Modules Ready:** **8/8** 🎊

1. ✅ OCR Processor
2. ✅ Reddit Service
3. ✅ Twitter Service
4. ✅ Fact Check Service
5. ✅ WhatsApp Service
6. ✅ Voice Service
7. ✅ URL Scraper
8. ✅ **News API** (NEW!)

---

**All verification modules complete!** Ready to build the main FastAPI integration. 🚀

