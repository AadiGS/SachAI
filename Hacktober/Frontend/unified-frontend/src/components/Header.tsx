import { Shield, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";

const Header = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-gradient-to-br from-[hsl(220_80%_60%)] to-[hsl(262_83%_58%)]">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-[hsl(220_80%_40%)] to-[hsl(262_83%_58%)] bg-clip-text text-transparent">
              SachAI
            </span>
          </div>
          
          <Link to="/verify">
            <Button 
              className="bg-gradient-to-r from-[hsl(220_80%_60%)] to-[hsl(262_83%_58%)] hover:opacity-90 text-white font-semibold px-6 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Try AI Detector
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
