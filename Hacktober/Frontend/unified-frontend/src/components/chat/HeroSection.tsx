import { useState } from "react";
import { Link2, FileText, Image, Mic } from "lucide-react";
import { Button } from "../ui/button";
import { FileUpload } from "../ui/file-upload";
import { RecordingInterface } from "./RecordingInterface";

interface HeroSectionProps {
  onAnalyze: (input: string, type: string, file?: File) => void;
}

export function HeroSection({ onAnalyze }: HeroSectionProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const [inputValue, setInputValue] = useState("");
  const [activeInput, setActiveInput] = useState<string>("text");

  // Placeholder text for each input type
  const placeholderText: Record<string, string> = {
    text: "Paste or type the text you want to verify...",
    url: "Paste a URL to check its authenticity...",
    image: "Upload an image to verify...",
    file: "Upload a document to verify...",
    voice: "Record your voice to verify...",
  };

  // Handle file selection for image upload
  const handleFilesChange = (files: File[]) => {
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
      setInputValue("");
    }
  };

  // Handle voice recording stop
  const handleVoiceStop = (audioBlob: Blob) => {
    setIsRecording(false);
    const audioFile = new File([audioBlob], "voice-recording.webm", { type: "audio/webm" });
    onAnalyze("", "voice", audioFile);
  };

  const handleSubmit = () => {
    if (activeInput === "image" && selectedFile) {
      onAnalyze("", "image", selectedFile);
    } else if (inputValue.trim()) {
      onAnalyze(inputValue, activeInput);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen relative z-50">

      {/* Main Headline */}
<h1 className="text-5xl md:text-6xl text-center mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-black max-w-3xl" style={{ fontFamily: 'Montserrat, sans-serif' }}>

        What do you want to check?
      </h1>

      {/* Subtitle */}
      <p className="text-muted-foreground text-center mb-12 max-w-xl z-40">
        Verify news articles, social media posts, and claims with AI-powered fact checking.
      </p>

      {/* Input Container */}
      <div className="w-full max-w-3xl">
        <div className="relative bg-card/50 backdrop-blur-sm border border-border rounded-2xl p-2 shadow-2xl">
          {/* Textarea */}
          {/* Render input area based on active input type */}
          {activeInput === "image" ? (
            <div className="min-h-[200px]">
              <FileUpload onChange={handleFilesChange} />
            </div>
          ) : activeInput === "voice" ? (
            <RecordingInterface onStop={handleVoiceStop} />
          ) : (
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholderText[activeInput] || "Paste a URL, enter text, or describe what you want to verify..."}
              className="w-full bg-transparent text-foreground placeholder-muted-foreground resize-none outline-none px-4 py-3 min-h-[120px] max-h-[300px]"
            />
          )}

          {/* Input Type Icons */}
          <div className="flex items-center justify-between px-2 py-2 border-t border-border/50">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveInput("url")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "url"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check URL"
              >
                <Link2 size={18} />
              </button>
              <button
                onClick={() => setActiveInput("text")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "text"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check Text"
              >
                <FileText size={18} />
              </button>
              <button
                onClick={() => setActiveInput("image")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "image"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check Image"
              >
                <Image size={18} />
              </button>
              <button
                onClick={() => setActiveInput("voice")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "voice"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Voice Input"
              >
                <Mic size={18} />
              </button>
            </div>

            <Button
              onClick={handleSubmit}
              className="text-white px-6 rounded-xl"
            >
              Analyze
            </Button>
          </div>
        </div>

 <div className="mt-6 flex flex-wrap justify-center gap-2 relative z-50">
          <button
            onClick={() => window.open("https://news.google.com", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Google News
          </button>

          <button
            onClick={() => window.open("https://inshorts.com/en/read", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Inshorts
          </button>

            <button
            onClick={() => window.open("https://m.dailyhunt.in/news/india/english/for+you?launch=true&mode=pwa", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Dailyhunt
          </button>

          
        </div>
      </div>
    </div>
  );

 

}