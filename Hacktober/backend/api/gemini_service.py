"""
Gemini AI Service
Handles news summarization and final verdict aggregation
Uses Google GenAI SDK with gemini-2.5-flash model
"""

import os
import asyncio
from typing import Dict, List
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
def get_gemini_client():
    """Get Gemini client instance."""
    if not GEMINI_API_KEY:
        return None
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    return genai.Client(api_key=GEMINI_API_KEY)


async def summarize_news(text: str, timeout: int = 3) -> Dict:
    """
    Summarize news text into 3-5 lines using Gemini.
    
    Args:
        text: Original news text
        timeout: Request timeout in seconds
        
    Returns:
        Dict with 'summary' and 'success' keys
    """
    client = get_gemini_client()
    if not client:
        return {
            "success": False,
            "summary": text[:500],  # Fallback: return first 500 chars
            "error": "GEMINI_API_KEY not configured"
        }
    
    prompt = f"""Summarize the following news article in 3-5 concise lines. 
Focus on the main claim and key facts. Be objective and clear.

News Article:
{text}

Summary:"""
    
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _generate():
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text
        
        # Wait for response with timeout
        summary = await asyncio.wait_for(
            loop.run_in_executor(None, _generate),
            timeout=timeout
        )
        
        return {
            "success": True,
            "summary": summary.strip()
        }
                    
    except asyncio.TimeoutError:
        print(f"⚠️ Gemini summarization timeout after {timeout}s")
        return {
            "success": False,
            "summary": text[:500],
            "error": "Timeout"
        }
    except Exception as e:
        print(f"⚠️ Gemini summarization error: {e}")
        return {
            "success": False,
            "summary": text[:500],
            "error": str(e)
        }


async def aggregate_verdict(
    original_text: str,
    gemini_summary: str,
    model_result: Dict,
    verification_results: Dict,
    timeout: int = 3
) -> Dict:
    """
    Aggregate all verification results into final verdict using Gemini.
    
    Args:
        original_text: Original news text
        gemini_summary: Summarized version
        model_result: ML model prediction
        verification_results: Dict with results from all APIs
        timeout: Request timeout in seconds
        
    Returns:
        Dict with final verdict, confidence, description, and references
    """
    if not GEMINI_API_KEY:
        # Fallback to model-only decision
        return {
            "verdict": model_result.get("prediction", "Uncertain"),
            "confidence": model_result.get("confidence", {"fake": 50, "real": 50}),
            "description": "Analysis based on ML model only (Gemini API not configured)",
            "references": []
        }
    
    # Prepare verification summary for Gemini
    verification_summary = f"""
VERIFICATION RESULTS:

1. ML MODEL (96.25% accuracy):
   - Prediction: {model_result.get('prediction', 'N/A')}
   - Confidence: {model_result.get('confidence', {})}
   - Source: Trained on 44k news articles

2. GOOGLE FACT CHECK:
   - Claims found: {verification_results.get('factcheck', {}).get('count', 0)}
   - Results: {_format_results(verification_results.get('factcheck', {}))}

3. NEWS API (70,000+ sources):
   - Label: {verification_results.get('newsapi', {}).get('label', 'N/A')}
   - Confidence: {verification_results.get('newsapi', {}).get('confidence', 'N/A')}
   - Relevant articles: {len(verification_results.get('newsapi', {}).get('relevant_links', []))}

4. TWITTER/X:
   - Posts found: {verification_results.get('twitter', {}).get('count', 0)}
   - Results: {_format_results(verification_results.get('twitter', {}))}

5. REDDIT:
   - Discussions found: {verification_results.get('reddit', {}).get('count', 0)}
   - Results: {_format_results(verification_results.get('reddit', {}))}

6. WEB SCRAPING:
   - Sources checked: {verification_results.get('webscrape', {}).get('count', 0)}
   - Results: {_format_results(verification_results.get('webscrape', {}))}
"""
    
    prompt = f"""You are a fact-checking expert analyzing news authenticity.

ORIGINAL CLAIM:
{gemini_summary}

{verification_summary}

Based on ALL the evidence above, provide a final verdict in this EXACT JSON format:
{{
  "verdict": "Real" or "Fake" or "Uncertain",
  "confidence": {{"fake": <0-100>, "real": <0-100>}},
  "description": "2-3 sentence explanation of why this is real/fake/uncertain",
  "key_factors": ["factor 1", "factor 2", "factor 3"]
}}

IMPORTANT:
- Give more weight to ML Model and News API (they're most reliable)
- Fact Check API is authoritative when claims are found
- Social media (Twitter/Reddit) are supporting evidence only
- If sources conflict, explain why in description
- Confidence scores should reflect agreement between sources
- Be objective and cite which sources support the verdict

Return ONLY the JSON, no other text."""
    
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _generate():
            client = get_gemini_client()
            if not client:
                raise Exception("Gemini client not available")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text
        
        # Wait for response with timeout
        response_text = await asyncio.wait_for(
            loop.run_in_executor(None, _generate),
            timeout=timeout
        )
        
        # Extract JSON from response
        import json
        import re
        
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            verdict_data = json.loads(json_match.group())
            
            # Add references from all sources
            references = _collect_references(verification_results)
            verdict_data['references'] = references
            
            return verdict_data
        else:
            raise ValueError("No JSON found in Gemini response")
                    
    except Exception as e:
        print(f"⚠️ Gemini verdict aggregation error: {e}")
        # Fallback to model-based decision
        model_conf = model_result.get('confidence', {"fake": 50, "real": 50})
        is_fake = model_conf.get('fake', 50) > model_conf.get('real', 50)
        
        return {
            "verdict": "Fake" if is_fake else "Real",
            "confidence": model_conf,
            "description": f"Analysis based primarily on ML model prediction. {model_result.get('prediction', '')}",
            "key_factors": [
                f"ML Model: {model_result.get('prediction', 'N/A')}",
                f"Model confidence: {max(model_conf.values())}%",
                "Other verification sources had issues"
            ],
            "references": _collect_references(verification_results),
            "fallback": True
        }


def _format_results(result: Dict) -> str:
    """Format API results for Gemini prompt."""
    if not result or result.get('count', 0) == 0:
        return "No results found"
    
    count = result.get('count', 0)
    return f"{count} result(s) found"


def _collect_references(verification_results: Dict) -> List[Dict]:
    """Collect all reference links from verification results."""
    references = []
    
    # News API links
    newsapi_results = verification_results.get('newsapi', {})
    for link in newsapi_results.get('relevant_links', []):
        references.append({
            "title": link.get('title', ''),
            "url": link.get('url', ''),
            "source": f"News API - {link.get('source', '')}",
            "relevance": "high"
        })
    
    # Fact Check links
    factcheck_results = verification_results.get('factcheck', {})
    for claim in factcheck_results.get('claims', [])[:3]:  # Top 3
        references.append({
            "title": claim.get('text', ''),
            "url": claim.get('url', ''),
            "source": f"Fact Check - {claim.get('publisher', '')}",
            "relevance": "high"
        })
    
    # Twitter links
    twitter_results = verification_results.get('twitter', {})
    for post in twitter_results.get('results', [])[:2]:  # Top 2 - FIXED: 'results' not 'posts'
        references.append({
            "title": post.get('text', '')[:100] + "...",
            "url": post.get('url', ''),
            "source": "Twitter/X",
            "relevance": "medium"
        })
    
    # Reddit links
    reddit_results = verification_results.get('reddit', {})
    for post in reddit_results.get('results', [])[:2]:  # Top 2 - FIXED: 'results' not 'posts'
        references.append({
            "title": post.get('title', ''),
            "url": post.get('reddit_url', post.get('url', '')),  # FIXED: use reddit_url
            "source": f"Reddit - r/{post.get('subreddit', '')}",
            "relevance": "medium"
        })
    
    return references[:10]  # Max 10 references


# Test function
async def test_gemini():
    """Test Gemini service."""
    test_text = "Scientists discover new planet in solar system orbiting beyond Neptune"
    
    print("Testing Gemini summarization...")
    summary_result = await summarize_news(test_text)
    print(f"Success: {summary_result['success']}")
    print(f"Summary: {summary_result['summary']}")
    
    print("\nTesting verdict aggregation...")
    mock_model = {"prediction": "Fake News", "confidence": {"fake": 85, "real": 15}}
    mock_verifications = {
        "factcheck": {"count": 2, "claims": []},
        "newsapi": {"label": 0, "confidence": 0.7, "relevant_links": []},
        "twitter": {"count": 5, "posts": []},
        "reddit": {"count": 3, "posts": []},
        "webscrape": {"count": 1}
    }
    
    verdict = await aggregate_verdict(test_text, summary_result['summary'], mock_model, mock_verifications)
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    asyncio.run(test_gemini())

