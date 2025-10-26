import { useState, useEffect } from "react";
import { HeroSection } from "../components/chat/HeroSection";
import { ResultsSection } from "../components/chat/ResultsSection";
import { VerificationProgress } from "../components/chat/VerificationProgress";
import { Shield, Moon, Sun } from "lucide-react";
import { Link } from "react-router-dom";

export default function Verify() {
  const [hasResult, setHasResult] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isDark, setIsDark] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme ? savedTheme === 'dark' : prefersDark;
    
    setIsDark(shouldBeDark);
    if (shouldBeDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleAnalyze = async (input: string, type: string, file?: File) => {
    setInputValue(input);
    setAnalysisData(null); // Clear previous results
    setIsAnalyzing(true); // Show loading screen
    setHasResult(false);
    if (file) setSelectedFile(file);
    
    try {
      const API_BASE_URL = 'http://localhost:8000';
      let response;
      
      // Different endpoints based on input type
      if (type === 'image' && file) {
        // Image upload - use file parameter directly
        const formData = new FormData();
        formData.append('file', file);
        
        response = await fetch(`${API_BASE_URL}/api/detect/image`, {
          method: 'POST',
          body: formData,
        });
      } else if (type === 'voice' && file) {
        // Voice upload - use file parameter directly
        const formData = new FormData();
        formData.append('file', file);
        
        response = await fetch(`${API_BASE_URL}/api/detect/voice`, {
          method: 'POST',
          body: formData,
        });
      } else {
        // Text or URL
        response = await fetch(`${API_BASE_URL}/api/detect/text`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: input,
            type: type
          }),
        });
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Format the response to match our UI expectations
      const formattedData = {
        query: data.query || input,
        confidence: data.confidence || { fake: 50, real: 50 },
        isFake: data.isFake,
        prediction: data.verdict || data.prediction,
        highlightedQuery: data.highlightedQuery || [{ text: data.query || input, isSuspicious: false }],
        explanation: {
          verdict: data.verdict,
          reasons: data.key_factors || []
        },
        description: data.description,
        relatedArticles: (data.references || []).map((ref: any) => ({
          title: ref.title,
          source: ref.source,
          url: ref.url
        })),
        whatsapp_share: data.whatsapp_share,
        metadata: data.metadata
      };
      
      setAnalysisData(formattedData);
      setIsAnalyzing(false);
      setHasResult(true);
      
    } catch (error) {
      console.error('Analysis error:', error);
      
      // Show error in UI
      const errorData = {
        query: input || "Error analyzing content",
        confidence: { fake: 50, real: 50 },
        isFake: false,
        prediction: "Error",
        highlightedQuery: [{ text: input || "Error", isSuspicious: false }],
        explanation: {
          verdict: "Error",
          reasons: [
            `Failed to analyze: ${error instanceof Error ? error.message : 'Unknown error'}`,
            "Please check if the backend server is running on http://localhost:8000",
            "Make sure all required API keys are configured in .env file"
          ]
        },
        description: "An error occurred while analyzing the content. Please try again.",
        relatedArticles: []
      };
      
      setAnalysisData(errorData);
      setIsAnalyzing(false);
      setHasResult(true);
    }
  };

  const handleReset = () => {
    setHasResult(false);
    setIsAnalyzing(false);
    setInputValue("");
    setAnalysisData(null);
    setSelectedFile(null);
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden">
      {/* Soft Blue Radial Background */}
      <div
        className="absolute inset-0 z-0 transition-colors duration-300"
        style={{
          background: isDark ? "#0a0a0f" : "#ffffff",
          backgroundImage: isDark
            ? `radial-gradient(circle at top center, rgba(59, 130, 246, 0.3), transparent 70%)`
            : `radial-gradient(circle at top center, #3b82f680, transparent 70%)`,
        }}
      />
      
      <div className={`min-h-screen transition-colors duration-200 ${
        isDark 
          ? 'bg-gradient-to-b from-[#0a0a0f] via-[#0f0f1a] to-[#1a1a2e] text-white' 
          : 'bg-gradient-to-b from-gray-50 via-white to-gray-100 text-gray-900'
      }`}>
        {/* Header */}
        <header className="fixed top-0 left-0 right-0 z-50 bg-opacity-80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  SachAI
                </span>
              </Link>
              
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
                aria-label="Toggle theme"
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </header>
        
        <div className="max-w-5xl mx-auto px-6 py-8 pt-24">
          {isAnalyzing ? (
            <VerificationProgress />
          ) : !hasResult ? (
            <HeroSection onAnalyze={handleAnalyze} />
          ) : (
            <ResultsSection data={analysisData} onReset={handleReset} />
          )}
        </div>
      </div>
    </div>
  );
}

