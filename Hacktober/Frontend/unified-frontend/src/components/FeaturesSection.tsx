import { Clock, Shield, FileText, BarChart3 } from "lucide-react";
// We no longer need the Card component
// import { Card } from "@/components/ui/card";

// Import the BentoGrid components
import { BentoGrid, BentoGridItem } from "@/components/ui/bento-grid";

// We update the features array to include classNames for the bento layout
// and pass icons as JSX elements instead of component references.
const features = [
  {
    title: "Real-Time Analysis",
    description:
      "Instant verification of content as it appears. Get truthfulness scores in seconds, not hours.",
    className: "md:col-span-2", // This item will span 2 columns on medium screens
    icon: <Clock className="w-8 h-8 text-white" />,
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80", // Analytics dashboard
  },
  {
    title: "Source Verification",
    description:
      "Cross-reference multiple trusted sources automatically. Verify the origin and authenticity of information.",
    className: "md:col-span-1",
    icon: <Shield className="w-8 h-8 text-white" />,
    image: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&q=80", // Security/Shield
  },
  {
    title: "Multi-Format Support",
    description:
      "Analyze text, images, videos, and audio. Our AI understands context across all media types.",
    className: "md:col-span-1",
    icon: <FileText className="w-8 h-8 text-white" />,
    image: "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=800&q=80", // Documents/Media
  },
  {

    title: "Detailed Verdict Reports",
    description:
      "Comprehensive analysis with confidence scores, source citations, and reasoning breakdown.",
    className: "md:col-span-2", // This item will span 2 columns on medium screens
    icon: <BarChart3 className="w-8 h-8 text-white" />,
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80", // Data/Reports
  },
];

// Enhanced component for bento grid item header with images
const FeatureHeader = ({
  className,
  image,
  icon,
}: {
  className?: string;
  image?: string;
  icon?: React.ReactNode;
}) => (
  <div
    className={`flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-[hsl(220_80%_60%)] to-[hsl(262_83%_58%)] overflow-hidden relative ${className}`}
  >
    {image && (
      <img 
        src={image} 
        alt="Feature illustration" 
        className="w-full h-full object-cover opacity-20"
      />
    )}
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="p-4 bg-white/10 rounded-full backdrop-blur-sm">
        {icon}
      </div>
    </div>
  </div>
);

const FeaturesSection = () => {
  return (
    <section className="py-24 px-6 bg-background">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold">
            Powerful Features for{" "}
            <span className="bg-gradient-to-r from-[hsl(220_80%_40%)] to-[hsl(262_83%_58%)] bg-clip-text text-transparent">
              Truth Seekers
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Built for journalists, researchers, and anyone who values accurate
            information.
          </p>
        </div>

        {/* Replace the old grid div with the BentoGrid component */}
        {/* We use md:grid-cols-3 for a 2x1 top row and 1x2 bottom row layout */}
        <BentoGrid className="max-w-5xl mx-auto md:grid-cols-3">
          {features.map((feature, index) => (
            <BentoGridItem
              key={index}
              title={feature.title}
              description={feature.description}
              // BentoGridItem often accepts a 'header' prop for a visual
              header={<FeatureHeader image={feature.image} icon={feature.icon} />}
              icon={feature.icon}
              className={feature.className}
            />
          ))}
        </BentoGrid>
      </div>
    </section>
  );
};

export default FeaturesSection;