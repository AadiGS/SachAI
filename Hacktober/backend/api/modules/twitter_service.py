"""
Twitter News Verification Module for Fake News Detection
Searches Twitter/X with fallback to web scraping
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("⚠️ Twitter dependencies not installed: pip install tweepy")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ Tavily not installed (web scraping fallback disabled): pip install tavily-python")


# Trusted Indian news domains
INDIAN_NEWS_DOMAINS = [
    "timesofindia.indiatimes.com", "thehindu.com", "hindustantimes.com",
    "indianexpress.com", "ndtv.com", "thequint.com", "thewire.in",
    "scroll.in", "news18.com", "zeenews.india.com", "dnaindia.com",
    "deccanherald.com", "firstpost.com", "livemint.com"
]


def is_valid_article_url(url: str) -> bool:
    """Check if URL is a proper article (not topic/tag page)"""
    import re
    
    excluded = ['/topic/', '/tag/', '/search/', '/category/', '/author/', 
                '/latest/', '/trending/', '/videos/', '/photogallery/']
    
    url_lower = url.lower()
    
    # Exclude aggregation pages
    if any(pattern in url_lower for pattern in excluded):
        return False
    
    # Check for article indicators
    valid = ['.html', '.htm', '/articleshow/', '/story/', '/article/', 
             '/news/', '.cms', '.ece']
    
    return any(indicator in url_lower for indicator in valid)


class TwitterNewsAnalyzer:
    """Twitter/X news verification with web scraping fallback"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 bearer_token: str = None, access_token: str = None, 
                 access_token_secret: str = None):
        """
        Initialize Twitter API client
        
        Args:
            Credentials from environment or parameters
        """
        if not TWEEPY_AVAILABLE:
            self.client = None
            return
        
        # Try environment variables
        api_key = api_key or os.getenv('TWITTER_API_KEY')
        api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not bearer_token:
            print("⚠️ Twitter API credentials not found")
            self.client = None
            return
        
        try:
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=False
            )
            self.executor = ThreadPoolExecutor(max_workers=2)
        except Exception as e:
            print(f"⚠️ Twitter initialization failed: {e}")
            self.client = None
    
    def _search_tweets_sync(self, query: str, label: Optional[int] = None) -> List[Dict]:
        """Synchronous Twitter search"""
        if not self.client:
            return "NO_API"
        
        # Build query based on label
        if label == 1:
            search_query = f'"{query}" (verified OR confirmed OR official) -is:retweet lang:en'
        elif label == 0:
            search_query = f'"{query}" (debunked OR false OR fake) -is:retweet lang:en'
        else:
            search_query = f'"{query}" -is:retweet lang:en'
        
        try:
            response = self.client.search_recent_tweets(
                query=search_query,
                max_results=20,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['name', 'username', 'verified'],
                sort_order='relevancy'
            )
            
            if not response or not response.data:
                return "NO_RESULTS"
            
            # Format tweets
            users = {user.id: user for user in response.includes.get('users', [])} if response.includes else {}
            tweets = []
            
            for tweet in response.data[:5]:  # Top 5
                author = users.get(tweet.author_id)
                tweets.append({
                    'text': tweet.text,
                    'url': f"https://twitter.com/{author.username if author else 'user'}/status/{tweet.id}",
                    'author': author.username if author else 'Unknown',
                    'likes': tweet.public_metrics.get('like_count', 0),
                    'retweets': tweet.public_metrics.get('retweet_count', 0)
                })
            
            return tweets
            
        except tweepy.errors.TooManyRequests:
            return "RATE_LIMIT"
        except Exception as e:
            print(f"⚠️ Twitter search error: {e}")
            return []
    
    def _web_scraping_fallback(self, query: str, label: Optional[int] = None) -> List[Dict]:
        """Web scraping fallback using Tavily"""
        if not TAVILY_AVAILABLE:
            return []
        
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if not tavily_api_key:
            return []
        
        try:
            client = TavilyClient(api_key=tavily_api_key)
            
            # Build query
            if label == 1:
                search_query = f"{query} verified confirmed official"
            elif label == 0:
                search_query = f"{query} debunked false fake"
            else:
                search_query = query
            
            response = client.search(
                query=search_query,
                search_depth="advanced",
                max_results=10,
                include_domains=INDIAN_NEWS_DOMAINS,
                days=365
            )
            
            results = []
            for item in response.get('results', []):
                url = item.get('url', '')
                
                if not url or not is_valid_article_url(url):
                    continue
                
                content = item.get('content', item.get('title', ''))
                if len(content.strip()) < 50:
                    continue
                
                results.append({
                    'text': content[:280],
                    'url': url,
                    'author': url.split('/')[2] if url else 'Web Source',
                    'likes': 0,
                    'retweets': 0
                })
                
                if len(results) >= 5:
                    break
            
            return results
            
        except Exception as e:
            print(f"⚠️ Web scraping error: {e}")
            return []
    
    async def search_twitter_news(self, query: str, label: Optional[int] = None, 
                                  timeout: int = 8) -> List[Dict[str, Any]]:
        """
        Async Twitter search with timeout and fallback
        
        Args:
            query: Search query
            label: 1=real, 0=fake, None=neutral
            timeout: Max time in seconds
            
        Returns:
            List of tweets/articles
        """
        try:
            # Try Twitter API first
            loop = asyncio.get_event_loop()
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self._search_tweets_sync,
                    query, label
                ),
                timeout=timeout
            )
            
            # Handle fallback cases
            if results in ["RATE_LIMIT", "NO_RESULTS", "NO_API"]:
                results = await loop.run_in_executor(
                    self.executor,
                    self._web_scraping_fallback,
                    query, label
                )
            
            return results if isinstance(results, list) else []
            
        except asyncio.TimeoutError:
            print("⚠️ Twitter search timeout")
            return []
        except Exception as e:
            print(f"⚠️ Twitter search error: {e}")
            return []


# Singleton instance
twitter_analyzer = TwitterNewsAnalyzer()


async def search_twitter(text: str, label: int = None, limit: int = 5) -> Dict[str, Any]:
    """
    Simple function to search Twitter
    
    Args:
        text: News text
        label: 1=real, 0=fake
        limit: Max results
        
    Returns:
        Dict with results and metadata
    """
    results = await twitter_analyzer.search_twitter_news(text, label)
    
    return {
        "source": "twitter",
        "count": len(results),
        "results": results[:limit]
    }

