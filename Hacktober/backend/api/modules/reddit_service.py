"""
Reddit News Search Module for Fake News Detection
Searches Reddit for relevant news articles and discussions
"""

import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("⚠️ Reddit dependencies not installed: pip install praw")


class RedditNewsSearcher:
    """Searches Reddit for news verification"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize Reddit API connection
        
        Args:
            client_id: Reddit API client ID (or from env)
            client_secret: Reddit API client secret (or from env)
        """
        if not PRAW_AVAILABLE:
            self.reddit = None
            return
        
        client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("⚠️ Reddit API credentials not found")
            self.reddit = None
            return
        
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="python:NewsDetectorBot:v1.0 (by /u/newsbot)"
            )
            self.executor = ThreadPoolExecutor(max_workers=2)
        except Exception as e:
            print(f"⚠️ Reddit initialization failed: {e}")
            self.reddit = None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 
                     'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        words = text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w.lower() not in stop_words and len(w) > 2]
        return keywords[:5]
    
    def _search_reddit_sync(self, text: str, label: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Synchronous Reddit search (called by async wrapper)"""
        if not self.reddit:
            return []
        
        # Select subreddits based on label
        if label == 1:  # Real news
            subreddits = ['news', 'worldnews', 'politics', 'technology', 'business']
        elif label == 0:  # Fake news
            subreddits = ['fakenews', 'skeptic', 'OutOfTheLoop']
        else:  # Neutral
            subreddits = ['news', 'worldnews', 'politics']
        
        keywords = self._extract_keywords(text)
        search_query = ' '.join(keywords)
        results = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts_per_sub = max(1, limit // len(subreddits) + 1)
                
                for submission in subreddit.search(search_query, limit=posts_per_sub, 
                                                   sort='relevance', time_filter='month'):
                    results.append({
                        'id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext[:500] if submission.selftext else '',
                        'url': submission.url,
                        'reddit_url': f"https://reddit.com{submission.permalink}",
                        'subreddit': subreddit_name,
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'upvote_ratio': submission.upvote_ratio,
                        'author': str(submission.author) if submission.author else '[deleted]'
                    })
            except Exception as e:
                print(f"⚠️ Reddit subreddit error ({subreddit_name}): {e}")
                continue
        
        # Sort by engagement
        results.sort(key=lambda x: (x['score'] * x['upvote_ratio']), reverse=True)
        return results[:limit]
    
    async def search_reddit_news(self, text: str, label: int = None, limit: int = 5, 
                                 timeout: int = 8) -> List[Dict[str, Any]]:
        """
        Async Reddit search with timeout
        
        Args:
            text: News text to search
            label: 1=real, 0=fake, None=neutral
            limit: Max results
            timeout: Max time in seconds
            
        Returns:
            List of Reddit posts
        """
        if not self.reddit:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self._search_reddit_sync,
                    text, label, limit
                ),
                timeout=timeout
            )
            return results
        except asyncio.TimeoutError:
            print("⚠️ Reddit search timeout")
            return []
        except Exception as e:
            print(f"⚠️ Reddit search error: {e}")
            return []


# Singleton instance
reddit_searcher = RedditNewsSearcher()


async def search_reddit(text: str, label: int = None, limit: int = 5) -> Dict[str, Any]:
    """
    Simple function to search Reddit
    
    Args:
        text: News text
        label: 1=real, 0=fake
        limit: Max results
        
    Returns:
        Dict with results and metadata
    """
    results = await reddit_searcher.search_reddit_news(text, label, limit)
    
    return {
        "source": "reddit",
        "count": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

