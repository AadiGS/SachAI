"""
WhatsApp Share Integration - Quick Example
Shows how to integrate WhatsApp sharing into your API
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Example 1: Simple Integration
# ============================================

from modules import create_whatsapp_share_from_result

# Your verification result
verification_result = {
    "text": "Government announces free laptops for students",
    "prediction": "Fake News",
    "confidence": {
        "fake": 87.5,
        "real": 12.5
    },
    "description": "This claim has been debunked by multiple fact-checking sources. No such announcement was made."
}

# Generate WhatsApp share data (ONE LINE!)
whatsapp_share = create_whatsapp_share_from_result(verification_result)

# Print results
print("=" * 60)
print("WhatsApp Share Data Generated:")
print("=" * 60)
print(f"\nStatus: {whatsapp_share['status']}")
print(f"Is Fake: {whatsapp_share['is_fake']}")
print(f"\nFormatted Message:")
print("-" * 60)
print(whatsapp_share['formatted_message'])
print("-" * 60)
print(f"\nShare URL:")
print(whatsapp_share['share_url'])
print("\n" + "=" * 60)


# Example 2: FastAPI Integration
# ============================================

"""
from fastapi import FastAPI
from modules import create_whatsapp_share_from_result

app = FastAPI()

@app.post("/api/detect")
async def detect_fake_news(data: dict):
    # Your verification logic
    result = {
        "text": data["text"],
        "prediction": "Fake News",  # or "Real News"
        "confidence": {"fake": 87.5, "real": 12.5},
        "description": "Verification explanation..."
    }
    
    # Add WhatsApp share (just one line!)
    result["whatsapp_share"] = create_whatsapp_share_from_result(result)
    
    return result

# Response will include:
# {
#   "text": "...",
#   "prediction": "Fake News",
#   "confidence": {...},
#   "description": "...",
#   "whatsapp_share": {
#     "formatted_message": "...",
#     "share_url": "https://wa.me/?text=...",
#     "is_fake": true,
#     "status": "FAKE"
#   }
# }
"""


# Example 3: Custom Message Generation
# ============================================

from modules import generate_whatsapp_share

# Generate custom share
custom_share = generate_whatsapp_share(
    text="Breaking: Scientists discover cure for common cold",
    is_fake=False,
    description="Verified by multiple reputable medical journals and WHO."
)

print("\n\nCustom Share Example (Real News):")
print("=" * 60)
print(custom_share['formatted_message'])
print("\nShare URL:", custom_share['share_url'])


# Example 4: Direct Phone Number Sharing
# ============================================

from modules.whatsapp_service import whatsapp_service

# Share to specific phone number
direct_share_url = whatsapp_service.generate_share_url(
    text="Government announces new policy",
    is_fake=False,
    description="Confirmed by official sources",
    phone_number="919876543210"  # Country code + number (no + or spaces)
)

print("\n\nDirect Phone Share URL:")
print("=" * 60)
print(direct_share_url)
print("\n(This opens WhatsApp with message pre-filled for specific contact)")


# Example 5: Frontend Usage
# ============================================

"""
// React Component Example
import React from 'react';

function VerificationResult({ result }) {
  const handleWhatsAppShare = () => {
    // Open WhatsApp with pre-filled message
    window.open(result.whatsapp_share.share_url, '_blank');
  };

  return (
    <div className="result-card">
      <h2>{result.prediction}</h2>
      <p>{result.description}</p>
      
      {/* WhatsApp Share Button */}
      <button 
        onClick={handleWhatsAppShare}
        className="whatsapp-share-btn"
        style={{
          background: '#25D366',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '25px',
          border: 'none',
          cursor: 'pointer'
        }}
      >
        📱 Share on WhatsApp
      </button>
      
      {/* Or as a link */}
      <a 
        href={result.whatsapp_share.share_url}
        target="_blank"
        rel="noopener noreferrer"
        className="whatsapp-link"
      >
        Share via WhatsApp
      </a>
    </div>
  );
}

export default VerificationResult;
"""


# Example 6: Testing Different Scenarios
# ============================================

print("\n\n" + "=" * 60)
print("Testing Different Scenarios:")
print("=" * 60)

test_cases = [
    {
        "text": "Short fake news",
        "prediction": "Fake News",
        "description": "Debunked"
    },
    {
        "text": "This is a very long news article " * 20,  # Long text
        "prediction": "Real News",
        "description": "Verified by multiple sources"
    },
    {
        "text": "News with special characters: #trending @user https://link.com",
        "prediction": "Fake News",
        "description": "Contains misleading hashtags"
    }
]

for i, case in enumerate(test_cases, 1):
    print(f"\n\nTest Case {i}:")
    print("-" * 60)
    share = create_whatsapp_share_from_result(case)
    print(f"Text Length: {len(case['text'])} chars")
    print(f"Status: {share['status']}")
    print(f"URL Length: {len(share['share_url'])} chars")
    print(f"Message Preview: {share['text_preview']}")


print("\n\n" + "=" * 60)
print("✅ All examples completed!")
print("=" * 60)
print("\n💡 Integration is as simple as:")
print("   result['whatsapp_share'] = create_whatsapp_share_from_result(result)")
print("\n🎉 Ready to use in production!")

