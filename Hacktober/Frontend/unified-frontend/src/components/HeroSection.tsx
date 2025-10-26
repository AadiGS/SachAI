import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import heroImage from "@/assets/hero-verification.jpg";
import { MacbookScroll } from "@/components/ui/macbook-scroll";


const HeroSection = () => {
  return (
    <section className="relative px-6 overflow-hidden">
      {/* Background gradient */}
      <div 
        className="absolute inset-0 -z-10"
        style={{ background: 'var(--gradient-hero)' }}
      />
      
      <div className="container mx-auto max-w-7xl">
        <div className="items-center">
          {/* Right image */}
          <div className="relative">
            {/* Right content — Macbook Scroll Animation */}
            <div className="relative flex justify-center items-center">
              <MacbookScroll src={heroImage} title="" showGradient />
            </div>

            {/* Floating accent */}
            <div className="absolute -top-6 -right-6 w-32 h-32 bg-accent/20 rounded-full blur-3xl -z-10" />
            <div className="absolute -bottom-6 -left-6 w-40 h-40 bg-[hsl(220_80%_60%)]/20 rounded-full blur-3xl -z-10" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
