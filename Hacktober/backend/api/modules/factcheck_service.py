"""
Google Fact Check API Module for Fake News Detection
Searches Google Fact Check API and uses Gemini to select top 5 sources
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Requests not installed: pip install requests")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ Gemini not installed: pip install google-generativeai")


class GoogleFactCheckSearcher:
    """Google Fact Check API integration with Gemini analysis"""
    
    def __init__(self, factcheck_api_key: str = None, gemini_api_key: str = None):
        """
        Initialize Fact Check API and Gemini
        
        Args:
            factcheck_api_key: Google Fact Check API key (or from env)
            gemini_api_key: Gemini API key (or from env)
        """
        self.factcheck_api_key = factcheck_api_key or os.getenv('GOOGLE_FACTCHECK_API_KEY')
        gemini_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        if not REQUESTS_AVAILABLE or not GENAI_AVAILABLE:
            self.available = False
            return
        
        if not self.factcheck_api_key or not gemini_key:
            print("⚠️ Fact Check API credentials not found")
            self.available = False
            return
        
        try:
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.executor = ThreadPoolExecutor(max_workers=2)
            self.available = True
        except Exception as e:
            print(f"⚠️ Fact Check initialization failed: {e}")
            self.available = False
    
    def _extract_claims_sync(self, text: str) -> List[str]:
        """Extract verifiable claims from text using Gemini"""
        try:
            prompt = f"""
Extract 3-5 key factual claims that can be verified using fact-checking sources.
Focus on specific, verifiable statements (names, dates, events, statistics).

Article: {text[:1000]}

Return ONLY a JSON array of claim strings.
Example: ["Claim 1", "Claim 2", "Claim 3"]
"""
            
            response = self.gemini_model.generate_content(prompt)
            claims_text = response.text.strip()
            
            # Parse JSON
            if claims_text.startswith('```'):
                claims_text = claims_text.split('```')[1]
                if claims_text.startswith('json'):
                    claims_text = claims_text[4:]
            
            claims = json.loads(claims_text.strip())
            return claims[:5]  # Max 5 claims
            
        except Exception as e:
            print(f"⚠️ Claim extraction failed: {e}")
            # Fallback: use first 200 chars as claim
            return [text[:200]]
    
    def _search_factcheck_api_sync(self, claims: List[str]) -> List[Dict[str, Any]]:
        """Search Google Fact Check API"""
        base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        all_results = []
        
        for claim in claims:
            try:
                params = {
                    'query': claim,
                    'languageCode': 'en',
                    'key': self.factcheck_api_key
                }
                
                response = requests.get(base_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'claims' in data:
                        for item in data['claims']:
                            claim_reviews = item.get('claimReview', [])
                            for claim_review in claim_reviews:
                                result = {
                                    'claim': item.get('text', claim),
                                    'claimant': item.get('claimant', 'Unknown'),
                                    'url': claim_review.get('url', ''),
                                    'title': claim_review.get('title', ''),
                                    'publisher': claim_review.get('publisher', {}).get('name', 'Unknown'),
                                    'rating': claim_review.get('textualRating', 'Unknown'),
                                    'date': claim_review.get('reviewDate', '')
                                }
                                
                                if result['url']:
                                    all_results.append(result)
            
            except Exception as e:
                print(f"⚠️ Fact Check API error: {e}")
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results
    
    def _select_top_5_sync(self, sources: List[Dict[str, Any]], article_text: str) -> Dict[str, Any]:
        """Use Gemini to select top 5 most relevant sources"""
        try:
            # Format sources
            sources_text = ""
            for i, source in enumerate(sources[:20], 1):  # Limit to 20 for analysis
                sources_text += f"\n{i}. {source['title']}\n"
                sources_text += f"   Publisher: {source['publisher']}\n"
                sources_text += f"   Rating: {source['rating']}\n"
                sources_text += f"   Claim: {source['claim'][:100]}\n"
                sources_text += f"   URL: {source['url']}\n"
            
            prompt = f"""
You are a fact-checking expert. Analyze this article and the fact-check sources.

Article: {article_text[:500]}

Available Fact-Check Sources:
{sources_text}

Task:
1. Select the TOP 5 most relevant and credible fact-check sources
2. For each source, explain its relevance
3. Provide an overall assessment

Return ONLY valid JSON:
{{
  "overall_explanation": "Brief assessment based on fact-check sources",
  "top_5_sources": [
    {{
      "rank": 1,
      "url": "source url",
      "title": "source title",
      "publisher": "publisher name",
      "rating": "fact-check rating",
      "relevance": "high/medium/low",
      "explanation": "Why this source is relevant"
    }}
  ]
}}
"""
            
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            print(f"⚠️ Gemini selection failed: {e}")
            # Fallback: return first 5
            return {
                "overall_explanation": "Analysis based on available fact-check sources",
                "top_5_sources": [
                    {
                        "rank": i+1,
                        "url": src['url'],
                        "title": src['title'],
                        "publisher": src['publisher'],
                        "rating": src['rating'],
                        "relevance": "medium",
                        "explanation": f"Fact-check source from {src['publisher']}"
                    }
                    for i, src in enumerate(sources[:5])
                ]
            }
    
    async def verify_with_factcheck(self, text: str, timeout: int = 8) -> Dict[str, Any]:
        """
        Async fact check verification
        
        Args:
            text: News article text
            timeout: Max time in seconds
            
        Returns:
            Dict with verification results
        """
        if not self.available:
            return {
                "source": "factcheck",
                "available": False,
                "results": []
            }
        
        try:
            loop = asyncio.get_event_loop()
            
            # Step 1: Extract claims
            claims = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._extract_claims_sync, text),
                timeout=timeout/3
            )
            
            if not claims:
                return {
                    "source": "factcheck",
                    "available": True,
                    "count": 0,
                    "results": [],
                    "explanation": "No verifiable claims found"
                }
            
            # Step 2: Search Fact Check API
            sources = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._search_factcheck_api_sync, claims),
                timeout=timeout/2
            )
            
            if not sources:
                return {
                    "source": "factcheck",
                    "available": True,
                    "count": 0,
                    "results": [],
                    "explanation": "No fact-check sources found"
                }
            
            # Step 3: Select top 5 with Gemini
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._select_top_5_sync, sources, text),
                timeout=timeout/3
            )
            
            return {
                "source": "factcheck",
                "available": True,
                "count": len(result.get('top_5_sources', [])),
                "explanation": result.get('overall_explanation', ''),
                "results": result.get('top_5_sources', [])
            }
            
        except asyncio.TimeoutError:
            print("⚠️ Fact Check timeout")
            return {
                "source": "factcheck",
                "available": True,
                "count": 0,
                "results": [],
                "explanation": "Verification timeout"
            }
        except Exception as e:
            print(f"⚠️ Fact Check error: {e}")
            return {
                "source": "factcheck",
                "available": True,
                "count": 0,
                "results": [],
                "explanation": f"Error: {str(e)}"
            }


# Singleton instance
factcheck_searcher = GoogleFactCheckSearcher()


async def search_factcheck(text: str, timeout: int = 8) -> Dict[str, Any]:
    """
    Simple function to search Google Fact Check
    
    Args:
        text: News article text
        timeout: Max time in seconds
        
    Returns:
        Dict with fact-check results
    """
    return await factcheck_searcher.verify_with_factcheck(text, timeout)

