import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

const CTASection = () => {
  return (
    <section className="py-24 px-6 bg-background">
      <div className="container mx-auto max-w-4xl">
        <div className="relative rounded-3xl overflow-hidden p-12 md:p-16 text-center space-y-8">
          {/* Background gradient */}
          <div 
            className="absolute inset-0 -z-10"
            style={{ background: 'linear-gradient(135deg, hsl(220 80% 60%) 0%, hsl(262 83% 58%) 100%)' }}
          />
          
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
          
          <div className="relative z-10 space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm text-white text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>Start your free trial today</span>
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold text-white">
              Ready to Combat Misinformation?
            </h2>
            
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              Join thousands of journalists and researchers who trust SachAI 
              to keep information accurate and trustworthy.
            </p>
            
            <div className="flex flex-wrap gap-4 justify-center pt-4">
              <Button 
                size="lg" 
                className="bg-white text-[hsl(262_83%_58%)] hover:bg-white/90 hover:scale-105 transition-[var(--transition-bounce)] font-semibold shadow-xl group"
              >
                Create a Free Account
                <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-2 border-white/30 bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 hover:border-white/50"
              >
                Schedule a Demo
              </Button>
            </div>
            
            <p className="text-sm text-white/80">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
