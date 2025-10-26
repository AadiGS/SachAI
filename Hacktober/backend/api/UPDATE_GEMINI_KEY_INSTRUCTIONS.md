# 🔑 Update Gemini API Key Instructions

## Your New Gemini API Key:
```
AIzaSyAWF4dfNSDO8NA7j-EKk8ujOVwk_oW1vjE
```

---

## 📝 How to Update:

### **Step 1: Open `.env` file**

**Path:** `D:\Hackathons\Hacktober\backend\api\.env`

Open this file in any text editor (Notepad, VS Code, etc.)

---

### **Step 2: Find the Gemini line**

Look for:
```
GEMINI_API_KEY=AIzaSyAMP3Ml_o6QPxf008GC0qHJ92etMyqGy5U
```

---

### **Step 3: Replace with new key**

Change it to:
```
GEMINI_API_KEY=AIzaSyAWF4dfNSDO8NA7j-EKk8ujOVwk_oW1vjE
```

---

### **Step 4: Save the file**

Press `Ctrl+S` to save.

---

### **Step 5: Restart Backend**

**Stop backend** (Ctrl+C in terminal)

**Start again:**
```bash
cd D:\Hackathons\Hacktober\backend\api
python main.py
```

---

## 🎯 Why This Matters:

### **Example: "Delhi Capitals won IPL"**

**Without Gemini (Current - WRONG):**
```
ML Model: "Looks like real news" (60%)
    ↓
Result: ✅ Real News ❌ WRONG!
```

**With Gemini (After Update - CORRECT):**
```
ML Model: "Looks like real news" (60%)
    ↓
Gemini extracts claim: "Delhi Capitals won IPL"
    ↓
Google Fact Check: "No records found"
    ↓
Twitter: No celebration tweets from Delhi Capitals
    ↓
News API: No articles about Delhi Capitals winning
    ↓
Gemini aggregates: "No evidence found. Likely FAKE."
    ↓
Result: ❌ Fake News ✅ CORRECT!
```

---

## 📊 What Each Component Does:

### **ML Model:**
- Checks text patterns
- Grammar, style, writing quality
- **Doesn't know facts!**
- Can be fooled by well-written fake news

### **Gemini + APIs:**
- Fact-checks actual claims
- Searches multiple sources
- Cross-references information
- **Knows real-world facts!**
- Catches factual errors

---

## 🧪 Test After Updating:

### **Test 1: Delhi Capitals (Should be FAKE)**
Input: "Delhi Capitals won the ipl trophy"
**Expected with Gemini:** ❌ Fake News

### **Test 2: Mumbai Indians (Should be REAL)**
Input: "Mumbai Indians won the IPL trophy in 2020"
**Expected with Gemini:** ✅ Real News (They actually won in 2020!)

### **Test 3: Chennai Super Kings (Should be REAL)**
Input: "Chennai Super Kings is a successful IPL team"
**Expected with Gemini:** ✅ Real News (They won multiple times!)

---

## 🔧 Complete `.env` File Reference:

After updating, your `.env` should look like:

```env
GEMINI_API_KEY=AIzaSyAWF4dfNSDO8NA7j-EKk8ujOVwk_oW1vjE
TAVILY_API_KEY=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
TWITTER_API_KEY=9viJ8mkbKvITzSIY9csGr9ZCa
TWITTER_API_SECRET=sl9USIWRTYZI9yxmTgkCL5LTVXQMtHYnHMj2rCe89iCYCmPNr4
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAIJ34gEAAAAAO5i%2B0JnTSYiYxW59nRiYFN2Uues%3D8CuWkN5s7sikR7ycgjq25mZJOwH6S7bBAn6VZlIEik3eJaZQGD
TWITTER_ACCESS_TOKEN=1974900723084132352-TEHS9VOdChtEGhEcqABR6496cDcoKP
TWITTER_ACCESS_TOKEN_SECRET=rziZIL4kZr3vHhGfJVGBnpLNfHQPBUNr9rNespruJMXch
REDDIT_CLIENT_ID=o8Mm_utEoVOCpWFl36CSiQ
REDDIT_CLIENT_SECRET=_eiKxfqCohb8F-meTzrpy-8DNGr5gA
NEWS_API_KEY=24f9c193902b42f5a20242dfb95363d0
ELEVENLABS_API_KEY=sk_6f8259b95d0068475e53f8e132f3712e7d07f7b38a9939c3
ELEVENLABS_TTS_VOICE_ID=pNInz6obpgDQGcFmaJgB
GOOGLE_FACTCHECK_API_KEY=AIzaSyA0fkCUHlZdZCMvoZNlawAAK5i5IUbPOSk
```

**Only the first line changed!**

---

## 🎯 Summary:

**Problem:** ML model alone can't verify facts
**Solution:** Update Gemini API key to enable intelligent fact-checking
**Result:** System will correctly identify factually wrong claims as fake

---

**Update the key and restart backend to fix the issue!** 🔑✨

