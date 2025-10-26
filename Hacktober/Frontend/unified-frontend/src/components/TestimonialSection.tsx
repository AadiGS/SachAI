import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Quote, MoveLeft, MoveRight } from 'lucide-react';

// --- Data for the Testimonials ---
const testimonials = [
  {
    id: 1,
    quote:
      "SachAI has transformed how our newsroom approaches fact-checking. What used to take hours now takes minutes, and we can confidently publish knowing we've verified every claim.",
    name: 'Sarah Mitchell',
    title: 'Senior Investigative Journalist, Global News Network',
    bgColor: 'bg-blue-600',
  },
  {
    id: 2,
    quote:
      "As a financial analyst, accuracy is non-negotiable. This tool's ability to cross-reference data from multiple sources in real-time is unparalleled. It's become an indispensable part of my workflow.",
    name: 'David Chen',
    title: 'Financial Analyst, Apex Investments',
    bgColor: 'bg-purple-600',
  },
  {
    id: 3,
    quote:
      "In academia, validating sources is tedious but critical. SachAI streamlines this process, allowing me to focus more on research and less on verification. A true game-changer for my team.",
    name: 'Dr. Emily Rodriguez',
    title: 'University Researcher & Professor',
    bgColor: 'bg-green-600',
  },
  {
    id: 4,
    quote:
      'The speed and reliability are impressive. We use it to vet partner claims and marketing copy, ensuring everything we put out is 100% accurate. Our legal team has never been happier.',
    name: 'Michael Tunde',
    title: 'Marketing Director, TechCorp',
    bgColor: 'bg-indigo-600',
  },
];

// --- The Stacking Card Component ---
const TestimonialStack = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  const handleNext = () => {
    setActiveIndex((prev) => (prev + 1) % testimonials.length);
  };

  const handlePrev = () => {
    setActiveIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  // Spring transition for a bouncier feel
  const spring = {
    type: "spring" as const,
    stiffness: 300,
    damping: 30,
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div className="relative h-96">
        <AnimatePresence initial={false}>
          {testimonials.map((item, index) => {
            // Calculate the position in the stack
            const stackIndex = (index - activeIndex + testimonials.length) % testimonials.length;
            // Only render the active card and the next 2 in the stack
            if (stackIndex > 2) return null;

            return (
              <motion.div
                key={item.id}
                className={`absolute inset-0 p-8 rounded-2xl shadow-2xl text-white ${item.bgColor} flex flex-col justify-between`}
                initial={{ scale: 0.9, y: 0, opacity: 0 }}
                animate={{
                  scale: 1 - stackIndex * 0.05, // Decrease scale for stacked cards
                  y: stackIndex * 20, // Offset cards in the stack
                  opacity: stackIndex === 0 ? 1 : 1 - stackIndex * 0.3, // Fade out stacked cards
                  zIndex: testimonials.length - stackIndex, // Set z-index
                }}
                exit={{ scale: 0.9, y: -20, opacity: 0 }}
                transition={spring}
                // Drag functionality for the top card
                drag={stackIndex === 0 ? 'x' : false}
                dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
                onDragEnd={(_, info) => {
                  if (info.offset.x > 100) handlePrev();
                  else if (info.offset.x < -100) handleNext();
                }}
              >
                {/* Card Content */}
                <div className="flex-1 space-y-4">
                  <Quote className="w-10 h-10 text-white/50" strokeWidth={1.5} />
                  <blockquote className="text-xl font-medium leading-relaxed">
                    "{item.quote}"
                  </blockquote>
                </div>
                <div className="mt-6 border-t border-white/20 pt-4">
                  <p className="font-semibold text-lg">{item.name}</p>
                  <p className="text-sm text-white/70">{item.title}</p>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-center gap-4 mt-8">
        <button
          onClick={handlePrev}
          className="p-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-all shadow-md"
          aria-label="Previous testimonial"
        >
          <MoveLeft className="w-5 h-5" />
        </button>
        <button
          onClick={handleNext}
          className="p-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-all shadow-md"
          aria-label="Next testimonial"
        >
          <MoveRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

// --- Main App Component ---
export default function App() {
  return (
    <section className="min-h-screen w-full bg-gray-50 py-24 px-6 flex items-center justify-center font-sans">
      {/* Background gradient */}
      <div
        className="absolute inset-0 -z-10 opacity-30"
        style={{
          background:
            'radial-gradient(circle at 10% 20%, rgb(226, 240, 254) 0%, rgb(255, 255, 255) 47.4%, rgb(226, 240, 254) 90%)',
        }}
      />

      <div className="container mx-auto max-w-4xl text-center">
        <h2 className="text-4xl font-bold text-gray-800 mb-4">
          Trusted by Professionals Worldwide
        </h2>
        <p className="text-lg text-gray-600 mb-16 max-w-2xl mx-auto">
          See how industry leaders are leveraging our platform to enhance accuracy,
          save time, and build unbreakable trust.
        </p>

        {/* Render the stacking component */}
        <TestimonialStack />
      </div>
    </section>
  );
}

