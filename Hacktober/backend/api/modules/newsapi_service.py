"""
News API Verification Service
Searches News API for relevant articles and determines credibility based on trusted sources.
Designed for async integration with the main verification pipeline.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

# Trusted news sources for credibility scoring
TRUSTED_SOURCES = [
    'bbc.com', 'reuters.com', 'apnews.com', 'cnn.com', 'nytimes.com',
    'theguardian.com', 'washingtonpost.com', 'bloomberg.com', 'npr.org',
    'wsj.com', 'abc.net.au', 'aljazeera.com', 'cbsnews.com', 'nbcnews.com',
    'forbes.com', 'time.com', 'usatoday.com', 'economist.com', 'snopes.com',
    'politifact.com', 'factcheck.org', 'apnews.org'
]


def extract_keywords(text: str, max_keywords: int = 5) -> str:
    """Extract important keywords from text for better search results."""
    stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for'}
    words = text.lower().split()
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    return ' '.join(keywords[:max_keywords])


async def search_news_api(
    query: str,
    max_results: int = 10,
    timeout: int = 8
) -> List[Dict]:
    """
    Search News API for articles related to the query.
    
    Args:
        query: Search query text
        max_results: Maximum number of articles to return
        timeout: Request timeout in seconds
    
    Returns:
        List of articles with title, url, source, and published date
    """
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY not configured")
        return []
    
    try:
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': max_results,
            'from': from_date
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                NEWS_API_BASE_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status != 200:
                    print(f"⚠️ News API error: {response.status}")
                    return []
                
                data = await response.json()
                
                if data.get('status') == 'ok':
                    articles = []
                    for article in data.get('articles', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', '')
                        })
                    return articles
                else:
                    print(f"News API error: {data.get('message', 'Unknown')}")
                    return []
                    
    except asyncio.TimeoutError:
        print(f"⚠️ News API timeout after {timeout}s")
        return []
    except Exception as e:
        print(f"⚠️ News API error: {e}")
        return []


def analyze_article_sentiment(article: Dict, original_text: str) -> int:
    """
    Analyze if article treats the news as real or questions it.
    Returns: 1 if article treats news as real, 0 if it debunks/questions it.
    """
    title = article['title'].lower()
    description = article.get('description', '').lower()
    combined = f"{title} {description}"
    
    # Strong debunking indicators
    strong_fake_indicators = [
        'debunk', 'hoax', 'misinformation', 'disinformation', 'false claim',
        'fake news', 'fabricated', 'baseless', 'unfounded', 'myth', 'not true',
        'incorrect', 'misleading', 'unverified claim', 'no evidence'
    ]
    
    # Weak questioning indicators
    weak_fake_indicators = [
        'allegedly', 'claims', 'unverified', 'rumor', 'speculation',
        'disputed', 'controversial', 'questions raised'
    ]
    
    # Words that indicate reporting as confirmed fact
    real_indicators = [
        'confirms', 'confirmed', 'announces', 'announced', 'investigation', 
        'officials say', 'breaking', 'exclusive', 'developing', 'authorities',
        'verified', 'reports confirm', 'statement', 'according to'
    ]
    
    # Calculate scores
    strong_fake_score = sum(2 for phrase in strong_fake_indicators if phrase in combined)
    weak_fake_score = sum(1 for phrase in weak_fake_indicators if phrase in combined)
    real_score = sum(1 for phrase in real_indicators if phrase in combined)
    total_fake_score = strong_fake_score + weak_fake_score
    
    # Special handling for fact-checking sites
    source_name = article['source'].lower()
    source_url = article['url'].lower()
    fact_check_sites = ['snopes', 'politifact', 'factcheck']
    is_fact_checker = any(site in source_name or site in source_url for site in fact_check_sites)
    
    if is_fact_checker:
        if strong_fake_score > 0:
            return 0  # They're debunking it
        if real_score > 0:
            return 1  # They're confirming
    
    # Decision logic
    if strong_fake_score >= 2:
        return 0
    elif total_fake_score > real_score and total_fake_score >= 2:
        return 0
    elif real_score > total_fake_score:
        return 1
    else:
        # Check relevance and trust
        keywords = extract_keywords(original_text).split()
        relevance = sum(1 for keyword in keywords if keyword in combined)
        source_domain = article['url'].split('/')[2] if article['url'] else ''
        is_trusted = any(trusted in source_domain.lower() for trusted in TRUSTED_SOURCES)
        
        if relevance >= 3 and is_trusted:
            return 1
        if relevance < 2:
            return 0
        
        return 1


def calculate_credibility(articles: List[Dict], original_text: str) -> Dict:
    """
    Calculate credibility based on consensus of articles.
    
    Args:
        articles: List of article dictionaries
        original_text: Original text being verified
    
    Returns:
        Dict with label (0=fake, 1=real), confidence, and analysis factors
    """
    if not articles:
        return {
            'label': 0,
            'confidence': 0.0,
            'factors': ['No articles found from credible sources'],
            'reason': 'No credible sources found covering this news'
        }
    
    # Take top 5 articles
    top_5 = articles[:5]
    real_votes = 0
    fake_votes = 0
    factors = []
    
    for article in top_5:
        vote = analyze_article_sentiment(article, original_text)
        if vote == 1:
            real_votes += 1
            factors.append(f"✓ {article['source']}: Reports as real")
        else:
            fake_votes += 1
            factors.append(f"✗ {article['source']}: Questions/debunks")
    
    total_votes = len(top_5)
    
    # Calculate confidence
    if real_votes > fake_votes:
        label = 1
        confidence = real_votes / total_votes
        reason = f"Majority ({real_votes}/{total_votes}) sources report as real"
    elif fake_votes > real_votes:
        label = 0
        confidence = fake_votes / total_votes
        reason = f"Majority ({fake_votes}/{total_votes}) sources question/debunk"
    else:
        # Tie - check trusted sources
        trusted_count = sum(
            1 for article in top_5 
            if any(trusted in article['url'].lower() for trusted in TRUSTED_SOURCES)
        )
        if trusted_count >= 3:
            label = 1
            confidence = 0.6
            reason = f"Split verdict but {trusted_count}/5 from trusted sources"
        else:
            label = 0
            confidence = 0.5
            reason = "Split verdict with limited trusted sources"
    
    factors.insert(0, f"Analyzed {total_votes} articles: {real_votes} confirm, {fake_votes} question")
    
    return {
        'label': label,
        'confidence': round(confidence, 2),
        'factors': factors,
        'reason': reason
    }


async def verify_news(text: str, timeout: int = 8) -> Dict:
    """
    Main verification function - async version for pipeline integration.
    
    Args:
        text: Text to verify
        timeout: Request timeout in seconds (default 8s for 15-25s total pipeline)
    
    Returns:
        Dict with:
            - label: 0 (fake) or 1 (real)
            - confidence: 0.0-1.0 confidence score
            - relevant_links: List of top 5 articles
    """
    # Extract keywords for better search
    search_query = extract_keywords(text)
    
    # Search News API (with timeout)
    articles = await search_news_api(search_query, max_results=10, timeout=timeout)
    
    if not articles:
        return {
            'label': 0,
            'confidence': 0.0,
            'relevant_links': []
        }
    
    # Calculate credibility
    credibility = calculate_credibility(articles, text)
    
    # Prepare output
    top_articles = articles[:5]
    result = {
        'label': credibility['label'],
        'confidence': credibility['confidence'],
        'relevant_links': [
            {
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'published': article['publishedAt']
            }
            for article in top_articles
        ]
    }
    
    return result


# Synchronous wrapper for backward compatibility
def verify_news_sync(text: str, timeout: int = 8) -> Dict:
    """Synchronous wrapper for verify_news."""
    return asyncio.run(verify_news(text, timeout))


# Example usage
async def main():
    """Test the News API service."""
    test_text = "Scientists discover new planet in solar system"
    
    print("🚀 Testing News API Service")
    print(f"Query: {test_text}")
    print("=" * 60)
    
    result = await verify_news(test_text)
    
    print(f"\nLabel: {result['label']} ({'REAL' if result['label'] == 1 else 'FAKE'})")
    print(f"Confidence: {result['confidence'] * 100:.1f}%")
    print(f"\nRelevant Links: {len(result['relevant_links'])}")
    for i, link in enumerate(result['relevant_links'], 1):
        print(f"  {i}. {link['source']}: {link['title'][:60]}...")


if __name__ == "__main__":
    asyncio.run(main())

