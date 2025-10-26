import asyncio
import sys
import io
from dotenv import load_dotenv

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

async def test_all_apis():
    from modules import search_factcheck, search_twitter, search_reddit, verify_news
    
    test_text = "Google's Willow quantum processor outperformed classical supercomputers"
    
    print("Testing APIs with real request...")
    print("=" * 60)
    
    # Test Fact Check
    print("\n1. Testing Google Fact Check...")
    try:
        result = await search_factcheck(test_text, timeout=5)
        print(f"   Result: {result.get('count', 0)} claims found")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test News API
    print("\n2. Testing News API...")
    try:
        result = await verify_news(test_text, timeout=5)
        print(f"   Result: {result.get('count', 0)} articles found")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test Twitter
    print("\n3. Testing Twitter...")
    try:
        result = await search_twitter(test_text, label=-1, limit=5, timeout=5)
        print(f"   Result: {result.get('count', 0)} posts found")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test Reddit
    print("\n4. Testing Reddit...")
    try:
        result = await search_reddit(test_text, label=-1, limit=5, timeout=5)
        print(f"   Result: {result.get('count', 0)} posts found")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_all_apis())

