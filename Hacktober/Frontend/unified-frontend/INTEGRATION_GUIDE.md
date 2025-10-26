# Frontend Integration Guide

## 🎉 What's Been Done

### ✅ Completed Features

1. **Unified Frontend Structure**
   - Combined landing page and chat interface into one project
   - React Router for seamless navigation
   - Shared components and styling

2. **Landing Page Enhancements**
   - ✅ Added "Try AI Detector" button to navbar (navigates to `/verify`)
   - ✅ Added images to bento grids with gradient overlays
   - ✅ Responsive design maintained

3. **Verification Interface Improvements**
   - ✅ Replaced file upload with Aceternity UI component
   - ✅ Added confidence score pie chart (Fake vs Real visualization)
   - ✅ Added WhatsApp share button with pre-formatted message
   - ✅ Multiple input methods (Text, URL, Image, Voice)

## 📂 File Structure

```
unified-frontend/
├── src/
│   ├── components/
│   │   ├── chat/                    # Verification components
│   │   │   ├── HeroSection.tsx      # Input interface
│   │   │   ├── ResultsSection.tsx   # Results with pie chart & WhatsApp
│   │   │   ├── RecordingInterface.tsx
│   │   │   └── figma/
│   │   ├── FeaturesSection.tsx      # Bento grid with images
│   │   ├── Header.tsx               # Landing page header with "Try AI" button
│   │   └── ui/
│   │       ├── file-upload.tsx      # Aceternity file upload
│   │       └── ...                  # Other shadcn/ui components
│   ├── pages/
│   │   ├── Index.tsx                # Landing page (/)
│   │   └── Verify.tsx               # Verification page (/verify)
│   └── App.tsx                      # Router config
```

## 🔌 Backend Integration Steps

### 1. Update API Endpoint

In `src/pages/Verify.tsx`, replace the mock `handleAnalyze` function:

**Current (Mock):**
```typescript
const handleAnalyze = async (input: string, type: string) => {
  // Mock data...
  setAnalysisData(mockData);
  setHasResult(true);
};
```

**Replace with:**
```typescript
const handleAnalyze = async (input: string, type: string) => {
  try {
    // Prepare the request based on input type
    let payload: any = { type };
    
    if (type === 'text' || type === 'url') {
      payload.text = input;
    } else if (type === 'image' && selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('type', type);
      
      const response = await fetch('http://localhost:8000/api/detect', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setAnalysisData(data);
      setHasResult(true);
      return;
    }
    
    // For text/url
    const response = await fetch('http://localhost:8000/api/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    
    const data = await response.json();
    setAnalysisData(data);
    setHasResult(true);
  } catch (error) {
    console.error('Analysis failed:', error);
    // Show error to user
  }
};
```

### 2. Expected Backend Response Format

The backend should return data in this format:

```typescript
{
  query: string;                    // The analyzed text
  confidence: {
    fake: number;                   // 0-100
    real: number;                   // 0-100
  };
  isFake: boolean;                  // true/false
  prediction: string;               // "Fake News" or "Real News"
  highlightedQuery: Array<{
    text: string;
    isSuspicious: boolean;
  }>;
  description: string;              // Short verdict description
  explanation: {
    verdict: string;                // "Likely False" or "Likely True"
    reasons: string[];              // Array of reason strings
  };
  relatedArticles: Array<{
    title: string;
    source: string;
    url: string;
  }>;
}
```

### 3. Handle File Uploads

The Aceternity file upload component triggers `handleFilesChange`:

```typescript
// Already implemented in HeroSection.tsx
const handleFilesChange = (files: File[]) => {
  if (files && files.length > 0) {
    setSelectedFile(files[0]);
    // File is now ready for analysis
  }
};
```

When user clicks "Analyze", the file should be sent via FormData.

### 4. Voice Input Integration

For voice recording, you'll need to:

1. Process the audio blob from `RecordingInterface`
2. Send to backend STT service
3. Use the transcribed text for analysis

**Update in `src/pages/Verify.tsx`:**
```typescript
const handleVoiceStop = async (audioBlob: Blob) => {
  setIsRecording(false);
  
  // Send to STT service
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  
  const response = await fetch('http://localhost:8000/api/voice/stt', {
    method: 'POST',
    body: formData,
  });
  
  const { text } = await response.json();
  
  // Now analyze the transcribed text
  handleAnalyze(text, 'voice');
};
```

## 🎨 UI Customization

### Pie Chart Colors

Edit `src/components/chat/ResultsSection.tsx`:

```typescript
const pieData = [
  { name: 'Fake', value: data.confidence?.fake || 0, color: '#ef4444' },  // Red
  { name: 'Real', value: data.confidence?.real || 0, color: '#22c55e' }   // Green
];
```

### WhatsApp Message Format

Edit in `ResultsSection.tsx`:

```typescript
const handleWhatsAppShare = () => {
  const message = encodeURIComponent(
    `🔍 VerifyAI Analysis Results\n\n` +
    `Verdict: ${data.prediction}\n` +
    `Confidence: ${data.confidence?.fake}%\n\n` +
    `${data.description}\n\n` +
    `Checked with VerifyAI`
  );
  window.open(`https://wa.me/?text=${message}`, '_blank');
};
```

### Bento Grid Images

Edit `src/components/FeaturesSection.tsx`:

```typescript
const features = [
  {
    title: "Real-Time Analysis",
    image: "your-custom-image-url",
    // ... other props
  }
];
```

## 🚀 Running the App

### Development Mode
```bash
cd Frontend/unified-frontend
npm run dev
```

Visit:
- **Landing Page:** http://localhost:5173/
- **Verification:** http://localhost:5173/verify

### Production Build
```bash
npm run build
npm run preview
```

## 🔗 CORS Configuration

If you encounter CORS errors, configure your FastAPI backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Testing WhatsApp Share

1. Run the app and navigate to `/verify`
2. Analyze any content (mock data works)
3. Click "Share on WhatsApp" button
4. Should open WhatsApp (web or app) with pre-filled message

## 🎯 Next Steps

1. ✅ Frontend is ready
2. ⏳ Connect to backend API endpoints
3. ⏳ Test with real data
4. ⏳ Deploy frontend and backend
5. ⏳ Set up environment variables for production

## 📊 Performance Targets

- Landing page load: < 2s
- Verification result: 15-25s (as per your requirement)
- WhatsApp share: Instant redirect

## 🐛 Troubleshooting

### Issue: Module not found errors
```bash
npm install
npm run dev
```

### Issue: Recharts not rendering
- Check if `recharts` is installed: `npm install recharts`

### Issue: File upload not working
- Ensure `react-dropzone` is installed
- Check browser console for errors

### Issue: Images not loading in bento grid
- Verify image URLs are accessible
- Check network tab in browser DevTools

## 📞 Support

For issues or questions about the frontend integration:
1. Check browser console for errors
2. Verify API response format matches expected structure
3. Test with mock data first before connecting to backend

---

**Frontend Status:** ✅ Ready for Integration
**All Tasks Completed:** Yes
**Tested:** Structure complete, awaiting backend connection

