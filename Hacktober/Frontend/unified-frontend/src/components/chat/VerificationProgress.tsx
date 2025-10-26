import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Loader2, Clock, Brain, Twitter, MessageCircle, Globe, Newspaper, Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

interface VerificationStep {
  id: string;
  name: string;
  icon: any;
  status: "pending" | "running" | "completed" | "skipped";
  duration?: number;
}

interface VerificationProgressProps {
  onComplete?: () => void;
}

export function VerificationProgress({ onComplete }: VerificationProgressProps) {
  const [steps, setSteps] = useState<VerificationStep[]>([
    { id: "model", name: "ML Model Analysis", icon: Brain, status: "pending" },
    { id: "factcheck", name: "Google Fact Check", icon: Search, status: "pending" },
    { id: "twitter", name: "Twitter Verification", icon: Twitter, status: "pending" },
    { id: "reddit", name: "Reddit Search", icon: MessageCircle, status: "pending" },
    { id: "newsapi", name: "News API Lookup", icon: Newspaper, status: "pending" },
    { id: "webscrape", name: "Web Scraping", icon: Globe, status: "pending" },
    { id: "gemini", name: "AI Verdict Aggregation", icon: Sparkles, status: "pending" },
  ]);

  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Show each verification step for minimum 1.5 seconds for better UX
    const totalSteps = steps.length;
    const minStepDuration = 1500; // Minimum 1.5 seconds per step
    const totalMinDuration = totalSteps * minStepDuration; // Total minimum animation time
    
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + (100 / (totalMinDuration / 100)); // Smooth progress over total duration
      });
    }, 100);

    // Update steps status with minimum display time
    const stepInterval = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev >= totalSteps) {
          clearInterval(stepInterval);
          // Only call onComplete after all steps shown
          if (onComplete) {
            setTimeout(onComplete, 500);
          }
          return prev;
        }

        // Mark current step as running
        setSteps((currentSteps) =>
          currentSteps.map((step, idx) => {
            if (idx < prev) return { ...step, status: "completed" as const };
            if (idx === prev) return { ...step, status: "running" as const };
            return step;
          })
        );

        return prev + 1;
      });
    }, minStepDuration); // Each step shows for minimum duration

    return () => {
      clearInterval(progressInterval);
      clearInterval(stepInterval);
    };
  }, [steps.length, onComplete]);

  const completedSteps = steps.filter((s) => s.status === "completed").length;
  const progressPercent = Math.round(progress);

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl"
      >
        {/* Main Card */}
        <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
          {/* Animated Background Gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5 dark:from-blue-500/10 dark:via-purple-500/10 dark:to-pink-500/10" />
          
          {/* Animated Orb */}
          <motion.div
            className="absolute -top-24 -right-24 w-48 h-48 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          <div className="relative p-8 sm:p-12">
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", duration: 0.6 }}
                className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-4"
              >
                <Loader2 className="w-8 h-8 text-white animate-spin" />
              </motion.div>
              
              <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent mb-2">
                Analyzing Content
              </h2>
              
              <p className="text-muted-foreground text-sm sm:text-base">
                Running {steps.length} verification checks across multiple sources
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-muted-foreground">
                  Progress: {completedSteps}/{steps.length} checks completed
                </span>
                <span className="font-semibold text-foreground">{progressPercent}%</span>
              </div>
              
              <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
                
                {/* Shimmer effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{
                    x: ["-100%", "200%"],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                />
              </div>
            </div>

            {/* Verification Steps */}
            <div className="space-y-3">
              {steps.map((step, index) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`
                    relative flex items-center gap-4 p-4 rounded-xl border transition-all duration-300
                    ${
                      step.status === "completed"
                        ? "bg-green-500/5 border-green-500/20 dark:bg-green-500/10"
                        : step.status === "running"
                        ? "bg-blue-500/5 border-blue-500/30 dark:bg-blue-500/10 shadow-lg shadow-blue-500/10"
                        : "bg-muted/30 border-border/50"
                    }
                  `}
                >
                  {/* Status Icon */}
                  <div
                    className={`
                      flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300
                      ${
                        step.status === "completed"
                          ? "bg-green-500 text-white"
                          : step.status === "running"
                          ? "bg-blue-500 text-white"
                          : "bg-muted text-muted-foreground"
                      }
                    `}
                  >
                    {step.status === "completed" ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", duration: 0.5 }}
                      >
                        <CheckCircle2 className="w-5 h-5" />
                      </motion.div>
                    ) : step.status === "running" ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Clock className="w-5 h-5" />
                    )}
                  </div>

                  {/* Step Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <step.icon
                        className={`w-4 h-4 flex-shrink-0 ${
                          step.status === "completed"
                            ? "text-green-600 dark:text-green-400"
                            : step.status === "running"
                            ? "text-blue-600 dark:text-blue-400"
                            : "text-muted-foreground"
                        }`}
                      />
                      <span
                        className={`font-medium text-sm sm:text-base truncate ${
                          step.status === "pending"
                            ? "text-muted-foreground"
                            : "text-foreground"
                        }`}
                      >
                        {step.name}
                      </span>
                    </div>
                    
                    {step.status === "running" && (
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs text-blue-600 dark:text-blue-400 mt-1"
                      >
                        Checking now...
                      </motion.p>
                    )}
                    
                    {step.status === "completed" && (
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs text-green-600 dark:text-green-400 mt-1"
                      >
                        ✓ Completed
                      </motion.p>
                    )}
                  </div>

                  {/* Pulse effect for running step */}
                  {step.status === "running" && (
                    <motion.div
                      className="absolute inset-0 rounded-xl border-2 border-blue-500/50"
                      animate={{
                        scale: [1, 1.02, 1],
                        opacity: [0.5, 0.8, 0.5],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                  )}
                </motion.div>
              ))}
            </div>

            {/* Footer Message */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="mt-8 text-center"
            >
              <p className="text-xs sm:text-sm text-muted-foreground">
                This may take 15-25 seconds. We're checking multiple sources to ensure accuracy.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

