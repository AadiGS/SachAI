# 💬 WhatsApp Share Integration Guide

## 📋 Overview

The WhatsApp Share feature allows users to instantly share fake news verification results via WhatsApp with a single click.

---

## 🎯 How It Works

### Flow:
1. **User completes verification** → Gets result (Real/Fake + description)
2. **System generates WhatsApp data** → Formats message + creates share URL
3. **User clicks "Share on WhatsApp"** → Opens WhatsApp with pre-filled message
4. **User selects recipient** → Sends verification result

---

## 📦 Module Structure

```
backend/api/modules/
├── whatsapp_service.py    # Core service (message formatting + URL generation)
└── share_page.html        # Optional: Standalone share page UI
```

---

## 🚀 Integration with Main API

### Option 1: Add to Verification Response (Recommended)

Include WhatsApp share data in every verification response:

```python
from modules import create_whatsapp_share_from_result

# After getting verification result
verification_result = {
    "text": "News article text...",
    "prediction": "Fake News",
    "confidence": {"fake": 87.5, "real": 12.5},
    "description": "Multiple sources debunked this claim"
}

# Generate WhatsApp share data
whatsapp_data = create_whatsapp_share_from_result(verification_result)

# Add to response
final_response = {
    **verification_result,
    "whatsapp_share": whatsapp_data
}

return final_response
```

**Response Structure:**
```json
{
  "text": "News article text...",
  "prediction": "Fake News",
  "confidence": {
    "fake": 87.5,
    "real": 12.5
  },
  "description": "Multiple sources debunked this claim",
  "whatsapp_share": {
    "formatted_message": "*The news \"...\"*\n\n*is FAKE.*\n\n*Description:* ...\n\n*Verified by Sach.ai*",
    "share_url": "https://wa.me/?text=...",
    "is_fake": true,
    "status": "FAKE"
  }
}
```

### Option 2: Dedicated Endpoint

Create a separate endpoint for generating WhatsApp share links:

```python
from fastapi import APIRouter
from modules import generate_whatsapp_share

router = APIRouter()

@router.post("/api/share/whatsapp")
async def create_whatsapp_share(data: dict):
    """
    Generate WhatsApp share link from verification result
    """
    share_data = generate_whatsapp_share(
        text=data.get("text", ""),
        is_fake=data.get("prediction", "").lower() == "fake news",
        description=data.get("description", "")
    )
    
    return share_data
```

---

## 🎨 Frontend Integration

### React/JavaScript Example:

```javascript
// After getting verification result from API
const result = await fetch('/api/detect', {
  method: 'POST',
  body: JSON.stringify({ text: newsText })
});

const data = await result.json();

// Get WhatsApp share data
const whatsappShare = data.whatsapp_share;

// Show share button
<a 
  href={whatsappShare.share_url} 
  target="_blank"
  className="whatsapp-share-btn"
>
  📱 Share on WhatsApp
</a>

// Or open programmatically
function shareOnWhatsApp() {
  window.open(whatsappShare.share_url, '_blank');
}
```

### Vue Example:

```vue
<template>
  <button @click="shareToWhatsApp" class="whatsapp-btn">
    📱 Share Result
  </button>
</template>

<script>
export default {
  props: ['verificationResult'],
  methods: {
    shareToWhatsApp() {
      const url = this.verificationResult.whatsapp_share.share_url;
      window.open(url, '_blank');
    }
  }
}
</script>
```

---

## 📱 Message Format

### Formatted Message Structure:

```
*The news "[article text]"*

*is FAKE/REAL.*

*Description:* [verification explanation]

*Verified by Sach.ai*
```

### Example Output:

**For Fake News:**
```
*The news "Government giving free laptops to students"*

*is FAKE.*

*Description:* This claim has been debunked by multiple fact-checking sources. No such announcement was made.

*Verified by Sach.ai*
```

**For Real News:**
```
*The news "New climate policy announced by government"*

*is REAL.*

*Description:* Verified by official government sources and major news outlets.

*Verified by Sach.ai*
```

---

## 🔧 Customization

### Change Brand Name:

```python
from modules.whatsapp_service import WhatsAppShareService

# Create custom instance
custom_service = WhatsAppShareService(brand_name="YourBrand.ai")

# Use it
share_data = custom_service.create_share_data(verification_result)
```

### Direct Phone Sharing:

```python
share_data = generate_whatsapp_share(
    text="News text",
    is_fake=False,
    description="Verified"
)

# Generate URL for specific phone number
share_url_with_phone = whatsapp_service.generate_share_url(
    text="News text",
    is_fake=False,
    description="Verified",
    phone_number="919876543210"  # Country code + number (no + or spaces)
)
```

---

## 🧪 Testing

### Test Message Generation:

```python
from modules.whatsapp_service import generate_whatsapp_share

# Test fake news
fake_share = generate_whatsapp_share(
    text="Government giving 5000 rupees to everyone",
    is_fake=True,
    description="This is a viral hoax. No such scheme exists."
)

print("Formatted Message:")
print(fake_share['formatted_message'])
print("\nShare URL:")
print(fake_share['share_url'])

# Test real news
real_share = generate_whatsapp_share(
    text="New vaccine approved by WHO",
    is_fake=False,
    description="Confirmed by WHO official announcement."
)

print("\nReal News Share URL:")
print(real_share['share_url'])
```

### Expected Output:
```
Formatted Message:
*The news "Government giving 5000 rupees to everyone"*

*is FAKE.*

*Description:* This is a viral hoax. No such scheme exists.

*Verified by Sach.ai*

Share URL:
https://wa.me/?text=*The%20news%20%22Government%20giving%205000%20rupees%20to%20everyone%22*%0A%0A*is%20FAKE.*%0A%0A*Description%3A*%20This%20is%20a%20viral%20hoax.%20No%20such%20scheme%20exists.%0A%0A*Verified%20by%20Sach.ai*
```

---

## 🎯 Use Cases

### 1. **Instant Sharing After Verification**
User verifies news → Clicks share → Sends to family/friends group

### 2. **Report Fake News**
User finds fake news → Verifies → Shares correction to source

### 3. **Spread Awareness**
User educates community by sharing verified results

### 4. **Save for Later**
User sends to own WhatsApp (saved messages) for reference

---

## 🌐 Mobile Optimization

WhatsApp URLs work differently on mobile vs desktop:

- **Mobile (iOS/Android):** Opens WhatsApp app directly
- **Desktop:** Opens WhatsApp Web (if logged in) or WhatsApp app (if installed)
- **Fallback:** Opens WhatsApp Web in browser

The `wa.me` format handles all cases automatically! ✅

---

## 📊 Analytics (Optional)

Track WhatsApp shares:

```python
@router.post("/api/detect")
async def detect_news(data: dict):
    # ... verification logic ...
    
    # Generate WhatsApp share
    whatsapp_data = create_whatsapp_share_from_result(result)
    
    # Track share URL generation (optional)
    await analytics.track_event("whatsapp_share_generated", {
        "is_fake": whatsapp_data["is_fake"],
        "text_length": len(data["text"])
    })
    
    return {
        **result,
        "whatsapp_share": whatsapp_data
    }
```

---

## ✅ Integration Checklist

- [ ] Import `create_whatsapp_share_from_result` in main API
- [ ] Add WhatsApp share data to verification response
- [ ] Update frontend to show "Share on WhatsApp" button
- [ ] Test on mobile devices
- [ ] Test message formatting (fake vs real)
- [ ] Verify long text truncation works
- [ ] Test share URL encoding
- [ ] (Optional) Add analytics tracking

---

## 🚀 Quick Integration Example

### FastAPI Backend:

```python
from fastapi import FastAPI
from modules import create_whatsapp_share_from_result

app = FastAPI()

@app.post("/api/detect")
async def detect_fake_news(data: dict):
    # Your verification logic here
    result = await verify_news(data["text"])
    
    # Add WhatsApp share (ONE LINE!)
    result["whatsapp_share"] = create_whatsapp_share_from_result(result)
    
    return result
```

### Frontend (React):

```jsx
function ResultDisplay({ result }) {
  return (
    <div>
      <h2>{result.prediction}</h2>
      <p>{result.description}</p>
      
      {/* WhatsApp Share Button */}
      <a 
        href={result.whatsapp_share.share_url}
        target="_blank"
        className="btn btn-whatsapp"
      >
        📱 Share on WhatsApp
      </a>
    </div>
  );
}
```

**That's it! Integration complete.** 🎉

---

## 📝 Notes

- No external API calls needed (unlike Twitter/Facebook share)
- Works offline (just opens WhatsApp)
- No rate limits
- No authentication required
- Universal compatibility (iOS, Android, Web)
- Free to use

---

## 🎨 Optional: Standalone Share Page

Serve `share_page.html` for a dedicated share interface:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

@app.get("/share")
async def share_page():
    return FileResponse("modules/share_page.html")
```

Users can access: `http://yoursite.com/share` to see a beautiful share interface.

---

**Status: ✅ INTEGRATION-READY**

WhatsApp share module is complete and ready to integrate! 🚀

