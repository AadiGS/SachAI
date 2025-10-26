"use client";

// Import your new FocusCards component
import { FocusCards } from "@/components/ui/focus-cards";

// 1. We create a new data array that matches the props for FocusCards
// It needs a 'title' and an image 'src'
const stepsData = [
  {
    title: "01. Submit Content: Upload text, paste a URL, or submit media.",
    // NOTE: Replace these placeholders with your actual image paths
    src: "https://placehold.co/600x400/3b82f6/FFFFFF?text=Submit+Content",
  },
  {
    title: "02. AI & API Analysis: Our AI cross-references multiple sources.",
    src: "https://placehold.co/600x400/8b5cf6/FFFFFF?text=AI+Analysis",
  },
  {
    title: "03. Get Your Truth Score: Receive a detailed, evidence-based report.",
    src: "https://placehold.co/600x400/10b981/FFFFFF?text=Get+Report",
  },
];

const HowItWorksSection = () => {
  return (
    // We keep the main section styling, but remove min-height/overflow
    <section className="py-24 px-6 relative bg-background">
      {/* Background gradient (optional, you can remove this if you prefer) */}
      <div
        className="absolute inset-0 -z-10 opacity-50"
        style={{ background: "var(--gradient-hero)" }}
      />

      <div className="container mx-auto max-w-7xl">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold">How It Works</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to verify any information
          </p>
        </div>

        {/* 2. Replace the old StickyScrollReveal component with FocusCards */}
        <FocusCards cards={stepsData} />
      </div>
    </section>
  );
};

export default HowItWorksSection;