import { HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

const HelpButton = () => {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            size="icon"
            className="w-14 h-14 rounded-full shadow-[var(--shadow-lg)] bg-gradient-to-br from-[hsl(220_80%_60%)] to-[hsl(262_83%_58%)] hover:scale-110 transition-[var(--transition-bounce)]"
          >
            <HelpCircle className="w-6 h-6 text-white" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-64 mr-6 mb-2" align="end">
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">How can we help?</h3>
            <div className="space-y-2">
              <a 
                href="#" 
                className="block text-sm text-muted-foreground hover:text-foreground transition-colors py-1"
              >
                📚 Help Center
              </a>
              <a 
                href="#" 
                className="block text-sm text-muted-foreground hover:text-foreground transition-colors py-1"
              >
                💬 Contact Support
              </a>
              <a 
                href="#" 
                className="block text-sm text-muted-foreground hover:text-foreground transition-colors py-1"
              >
                💡 Suggest a Feature
              </a>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};

export default HelpButton;
