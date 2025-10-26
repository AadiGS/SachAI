import React, { useRef, useState } from "react";
import { Mic, MicOff, AlertCircle } from "lucide-react";

interface RecordingInterfaceProps {
  onStop: (audioBlob: Blob) => void;
}

export const RecordingInterface: React.FC<RecordingInterfaceProps> = ({ onStop }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [error, setError] = useState<string | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      setError(null);
      
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser doesn't support audio recording");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      audioChunks.current = [];
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunks.current.push(e.data);
        }
      };
      
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        onStop(audioBlob);
      };
      
      recorder.start();
      setIsRecording(true);
    } catch (err: any) {
      console.error("Recording error:", err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError("Microphone permission denied. Please allow microphone access.");
      } else if (err.name === 'NotFoundError') {
        setError("No microphone found. Please connect a microphone.");
      } else {
        setError("Failed to start recording. Please try again.");
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-full min-h-[200px] p-6 space-y-4">
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}
      
      <div className="flex flex-col items-center gap-4">
        {isRecording ? (
          <>
            <div className="relative">
              <div className="w-20 h-20 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
                <MicOff className="w-10 h-10 text-white" />
              </div>
              <div className="absolute inset-0 w-20 h-20 bg-red-500 rounded-full animate-ping opacity-75"></div>
            </div>
            <button 
              onClick={stopRecording} 
              className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
            >
              <MicOff className="w-5 h-5" />
              Stop Recording
            </button>
            <p className="text-sm text-muted-foreground">Recording... Click stop when done</p>
          </>
        ) : (
          <>
            <div className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center">
              <Mic className="w-10 h-10 text-white" />
            </div>
            <button 
              onClick={startRecording} 
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
            >
              <Mic className="w-5 h-5" />
              Start Recording
            </button>
            <p className="text-sm text-muted-foreground">Click to start voice recording</p>
          </>
        )}
      </div>
    </div>
  );
};
