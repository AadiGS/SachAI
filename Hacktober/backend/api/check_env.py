from dotenv import load_dotenv
import os
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

print("Checking API Keys Configuration:")
print("=" * 50)
print(f"GEMINI_API_KEY: {'[OK]' if os.getenv('GEMINI_API_KEY') else '[MISSING]'}")
print(f"REDDIT_CLIENT_ID: {'[OK]' if os.getenv('REDDIT_CLIENT_ID') else '[MISSING]'}")
print(f"REDDIT_CLIENT_SECRET: {'[OK]' if os.getenv('REDDIT_CLIENT_SECRET') else '[MISSING]'}")
print(f"TWITTER_API_KEY: {'[OK]' if os.getenv('TWITTER_API_KEY') else '[MISSING]'}")
print(f"TWITTER_BEARER_TOKEN: {'[OK]' if os.getenv('TWITTER_BEARER_TOKEN') else '[MISSING]'}")
print(f"NEWS_API_KEY: {'[OK]' if os.getenv('NEWS_API_KEY') else '[MISSING]'}")
print(f"GOOGLE_FACTCHECK_API_KEY: {'[OK]' if os.getenv('GOOGLE_FACTCHECK_API_KEY') else '[MISSING]'}")
print(f"ELEVENLABS_API_KEY: {'[OK]' if os.getenv('ELEVENLABS_API_KEY') else '[MISSING]'}")
print(f"TAVILY_API_KEY: {'[OK]' if os.getenv('TAVILY_API_KEY') else '[MISSING]'}")
print("=" * 50)

# Show first/last few chars of each key
if os.getenv('GEMINI_API_KEY'):
    key = os.getenv('GEMINI_API_KEY')
    print(f"\nGEMINI_API_KEY: {key[:10]}...{key[-10:]}")
if os.getenv('REDDIT_CLIENT_ID'):
    key = os.getenv('REDDIT_CLIENT_ID')
    print(f"REDDIT_CLIENT_ID: {key}")
if os.getenv('NEWS_API_KEY'):
    key = os.getenv('NEWS_API_KEY')
    print(f"NEWS_API_KEY: {key}")

