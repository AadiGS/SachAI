import asyncio
import sys
import io
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv()

async def test_twitter_reddit():
    from modules import search_twitter, search_reddit, twitter_analyzer, reddit_searcher
    
    print("Testing Twitter and Reddit initialization...")
    print("=" * 60)
    
    print(f"\n1. Twitter Analyzer Client: {twitter_analyzer.client}")
    print(f"   Has valid client: {'YES' if twitter_analyzer.client else 'NO'}")
    
    print(f"\n2. Reddit Searcher Client: {reddit_searcher.reddit}")
    print(f"   Has valid client: {'YES' if reddit_searcher.reddit else 'NO'}")
    
    # Try calling them
    print("\n3. Testing Twitter search...")
    try:
        result = await search_twitter("quantum computing google", label=-1, limit=2)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n4. Testing Reddit search...")
    try:
        result = await search_reddit("quantum computing google", label=-1, limit=2)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_twitter_reddit())

