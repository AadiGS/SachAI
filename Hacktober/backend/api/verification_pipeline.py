"""
Verification Pipeline
Runs all verification services in parallel using asyncio.gather
Includes ML model + 6 external APIs with timeout protection
"""

import asyncio
import time
from typing import Dict
from model_wrapper import predict as model_predict
from modules import (
    search_factcheck,
    search_twitter,
    search_reddit,
    verify_news as newsapi_verify,
    scrape_url_to_text
)


async def run_parallel_verification(text: str, gemini_summary: str) -> Dict:
    """
    Run all verification services in parallel.
    
    Args:
        text: Original news text
        gemini_summary: Gemini-generated summary (3-5 lines)
        
    Returns:
        Dict with results from all services:
            - model: ML model prediction
            - factcheck: Google Fact Check results
            - newsapi: News API results
            - twitter: Twitter/X results
            - reddit: Reddit results
            - webscrape: Web scraping results
            - execution_time: Total time taken
    """
    start_time = time.time()
    print(f"\n🔄 Starting parallel verification...")
    print(f"   Using text length: {len(text)} chars")
    print(f"   Using summary length: {len(gemini_summary)} chars")
    
    # Run all services in parallel with timeouts
    # Use return_exceptions=True so one failure doesn't break others
    results = await asyncio.gather(
        # 1. ML Model (our trained model)
        _run_model(gemini_summary),
        
        # 2. Google Fact Check API
        _run_factcheck(gemini_summary),
        
        # 3. News API (70,000+ sources)
        _run_newsapi(gemini_summary),
        
        # 4. Twitter/X API (with scrape fallback)
        _run_twitter(gemini_summary),
        
        # 5. Reddit API
        _run_reddit(gemini_summary),
        
        # 6. Web Scraping (additional sources)
        _run_webscrape(gemini_summary),
        
        return_exceptions=True
    )
    
    # Unpack results
    model_result = results[0] if not isinstance(results[0], Exception) else _error_result("model", results[0])
    factcheck_result = results[1] if not isinstance(results[1], Exception) else _error_result("factcheck", results[1])
    newsapi_result = results[2] if not isinstance(results[2], Exception) else _error_result("newsapi", results[2])
    twitter_result = results[3] if not isinstance(results[3], Exception) else _error_result("twitter", results[3])
    reddit_result = results[4] if not isinstance(results[4], Exception) else _error_result("reddit", results[4])
    webscrape_result = results[5] if not isinstance(results[5], Exception) else _error_result("webscrape", results[5])
    
    execution_time = time.time() - start_time
    
    # Log results
    print(f"\n✅ Parallel verification complete in {execution_time:.2f}s")
    print(f"   Model: {_get_status(model_result)}")
    print(f"   Fact Check: {_get_status(factcheck_result)}")
    print(f"   News API: {_get_status(newsapi_result)}")
    print(f"   Twitter: {_get_status(twitter_result)}")
    print(f"   Reddit: {_get_status(reddit_result)}")
    print(f"   Web Scrape: {_get_status(webscrape_result)}")
    
    return {
        "model": model_result,
        "factcheck": factcheck_result,
        "newsapi": newsapi_result,
        "twitter": twitter_result,
        "reddit": reddit_result,
        "webscrape": webscrape_result,
        "execution_time": round(execution_time, 2),
        "services_checked": 6,
        "services_successful": sum([
            _is_successful(model_result),
            _is_successful(factcheck_result),
            _is_successful(newsapi_result),
            _is_successful(twitter_result),
            _is_successful(reddit_result),
            _is_successful(webscrape_result)
        ])
    }


async def _run_model(text: str, timeout: int = 2) -> Dict:
    """Run ML model prediction with timeout."""
    try:
        result = await asyncio.wait_for(model_predict(text), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print(f"⏱️ Model prediction timeout after {timeout}s")
        return {"error": "timeout", "count": 0}
    except Exception as e:
        print(f"❌ Model prediction error: {e}")
        return {"error": str(e), "count": 0}


async def _run_factcheck(text: str, timeout: int = 8) -> Dict:
    """Run Google Fact Check with timeout."""
    try:
        result = await asyncio.wait_for(search_factcheck(text, timeout=timeout), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print(f"⏱️ Fact Check timeout after {timeout}s")
        return {"error": "timeout", "count": 0, "claims": []}
    except Exception as e:
        print(f"❌ Fact Check error: {e}")
        return {"error": str(e), "count": 0, "claims": []}


async def _run_newsapi(text: str, timeout: int = 8) -> Dict:
    """Run News API with timeout."""
    try:
        result = await asyncio.wait_for(newsapi_verify(text, timeout=timeout), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print(f"⏱️ News API timeout after {timeout}s")
        return {"error": "timeout", "count": 0, "label": -1, "confidence": 0.0, "relevant_links": []}
    except Exception as e:
        print(f"❌ News API error: {e}")
        return {"error": str(e), "count": 0, "label": -1, "confidence": 0.0, "relevant_links": []}


async def _run_twitter(text: str, timeout: int = 8) -> Dict:
    """Run Twitter API with timeout."""
    try:
        # Twitter expects label parameter (0=fake, 1=real) - we pass -1 for unknown
        result = await asyncio.wait_for(search_twitter(text, label=-1, limit=5), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print(f"⏱️ Twitter timeout after {timeout}s")
        return {"error": "timeout", "count": 0, "results": []}
    except Exception as e:
        print(f"❌ Twitter error: {e}")
        return {"error": str(e), "count": 0, "results": []}


async def _run_reddit(text: str, timeout: int = 8) -> Dict:
    """Run Reddit API with timeout."""
    try:
        # Reddit expects label parameter (0=fake, 1=real) - we pass -1 for unknown
        result = await asyncio.wait_for(search_reddit(text, label=-1, limit=5), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print(f"⏱️ Reddit timeout after {timeout}s")
        return {"error": "timeout", "count": 0, "results": []}
    except Exception as e:
        print(f"❌ Reddit error: {e}")
        return {"error": str(e), "count": 0, "results": []}


async def _run_webscrape(text: str, timeout: int = 8) -> Dict:
    """Run web scraping for additional verification (placeholder)."""
    try:
        # For now, just return a basic result
        # In production, you might scrape additional fact-checking sites
        return {
            "count": 0,
            "sources": [],
            "note": "Web scraping not fully implemented"
        }
    except Exception as e:
        print(f"❌ Web scrape error: {e}")
        return {"error": str(e), "count": 0, "sources": []}


def _error_result(service: str, error: Exception) -> Dict:
    """Create error result dict."""
    return {
        "error": str(error),
        "service": service,
        "count": 0
    }


def _get_status(result: Dict) -> str:
    """Get status string for logging."""
    if "error" in result:
        return f"❌ Error: {result['error']}"
    count = result.get('count', result.get('label', 0))
    return f"✅ Success (count: {count})"


def _is_successful(result: Dict) -> bool:
    """Check if result was successful."""
    return "error" not in result


# Test function
async def test_pipeline():
    """Test verification pipeline."""
    test_text = "Scientists discover new planet in solar system"
    test_summary = "New planet discovered beyond Neptune by astronomers"
    
    print("🧪 Testing verification pipeline...")
    results = await run_parallel_verification(test_text, test_summary)
    
    print(f"\n📊 Results:")
    print(f"   Execution time: {results['execution_time']}s")
    print(f"   Services checked: {results['services_checked']}")
    print(f"   Services successful: {results['services_successful']}")
    print(f"\n   Model: {results['model']}")
    print(f"   Fact Check: {results['factcheck'].get('count', 0)} claims")
    print(f"   News API: {results['newsapi'].get('label', 'N/A')}")
    print(f"   Twitter: {results['twitter'].get('count', 0)} posts")
    print(f"   Reddit: {results['reddit'].get('count', 0)} posts")


if __name__ == "__main__":
    asyncio.run(test_pipeline())

