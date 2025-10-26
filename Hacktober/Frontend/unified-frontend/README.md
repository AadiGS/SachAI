# VerifyAI - Unified Frontend

A modern, full-featured fake news detection application with landing page and verification interface.

## ✨ Features

### Landing Page
- Beautiful hero section with gradient backgrounds
- Bento grid feature showcase with images
- "Try AI Detector" button in navbar
- Responsive design
- Modern UI with Tailwind CSS

### Verification Interface (`/verify`)
- **Multiple Input Methods:**
  - Text input
  - URL input
  - Image upload (with Aceternity UI file upload component)
  - Voice recording

- **Results Display:**
  - Confidence score pie chart (Fake vs Real percentages)
  - WhatsApp share button for easy sharing
  - Highlighted suspicious text segments
  - Detailed analysis with reasoning
  - Related articles
  - Feedback system with star ratings

## 🚀 Getting Started

### Installation

```bash
cd Frontend/unified-frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on `http://localhost:5173` (or next available port).

### Build for Production

```bash
npm run build
```

## 📁 Project Structure

```
unified-frontend/
├── src/
│   ├── components/
│   │   ├── chat/           # Verification interface components
│   │   │   ├── HeroSection.tsx
│   │   │   ├── ResultsSection.tsx
│   │   │   ├── FileUploadInterface.tsx
│   │   │   ├── RecordingInterface.tsx
│   │   │   └── figma/
│   │   ├── landing/        # Landing page components
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   └── ...
│   │   └── ui/            # Shared UI components (shadcn/ui + Aceternity)
│   ├── pages/
│   │   ├── Index.tsx      # Landing page
│   │   ├── Verify.tsx     # Verification interface
│   │   └── NotFound.tsx
│   ├── App.tsx            # Main app with routing
│   └── main.tsx
├── package.json
└── README.md
```

## 🎨 Key Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Aceternity UI** - File upload component
- **Recharts** - Pie chart visualization
- **Motion** - Animations
- **Lucide React** - Icons

## 🔗 Routes

- `/` - Landing page
- `/verify` - Verification interface
- `*` - 404 page

## 🎯 Integration with Backend

To connect to the backend API, update the API endpoint in:
- `src/pages/Verify.tsx` - Replace mock data with actual API calls

Example:
```typescript
const handleAnalyze = async (input: string, type: string) => {
  const response = await fetch('http://localhost:8000/api/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: input, type })
  });
  const data = await response.json();
  setAnalysisData(data);
  setHasResult(true);
};
```

## 📱 WhatsApp Share Feature

The WhatsApp share button automatically formats the analysis results and opens WhatsApp with a pre-filled message:

```
🔍 VerifyAI Analysis Results

Verdict: [Fake/Real News]
Confidence: [XX]%

[Description]

Checked with VerifyAI - Your trusted fact-checking companion
```

## 🎨 Customization

### Theme Colors
The app uses a blue-to-purple gradient theme. Modify in Tailwind config:
- Primary: `from-[hsl(220_80%_60%)] to-[hsl(262_83%_58%)]`

### Bento Grid Images
Update images in `src/components/FeaturesSection.tsx`:
```typescript
const features = [
  {
    image: "your-image-url-here"
  }
]
```

## 🐛 Known Issues

- File upload currently shows mock data (needs backend integration)
- Voice recording needs backend STT integration
- Some UI components may need path adjustments based on your setup

## 📝 License

MIT

---

Built with ❤️ for Hacktober 2025
