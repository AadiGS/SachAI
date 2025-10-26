// Removed all icon imports

const benefits = [
  {
    title: "Built for Journalists",
    description:
      "Designed with newsrooms in mind. Verify sources and claims before publishing.",
  },
  {
    title: "Trusted by Researchers",
    description:
      "Academic institutions rely on our platform for fact-checking and citation verification.",
  },
  {
    title: "Industry-Leading Accuracy",
    description:
      "Our AI achieves 95%+ accuracy across multiple independent benchmarks.",
  },
  {
    title: "Continuous Improvement",
    description:
      "Machine learning models updated daily with the latest fact-checking data.",
  },
];

const WhyChooseSection = () => {
  return (
    // The main section now just provides padding and spacing
    <section className="py-24 px-6 bg-background">
      <div className="container mx-auto max-w-7xl">
        {/* 2. Replaced BackgroundGradient with a standard div to fix the error */}
        <div
          className="rounded-2xl bg-background border border-border" // Simple styling to replace the gradient component
        >
          {/* 3. An inner div to provide padding for the content */}
          <div className="p-8 md:p-12">
            {/* 4. The Title Area is INSIDE the container */}
            <div className="text-center mb-16 space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold">
                Why Choose{" "}
                <span className="bg-gradient-to-r from-[hsl(220_80%_40%)] to-[hsl(262_83%_58%)] bg-clip-text text-transparent">
                  SachAI
                </span>
              </h2>
              <p className="text-2xl text-foreground font-medium max-w-3xl mx-auto">
                Empower Journalists. Uphold Integrity.
              </p>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                In an age of information overload, trust matters more than ever.
                Our platform gives you the tools to separate truth from fiction.
              </p>
            </div>

            {/* 5. The Benefits Grid is also INSIDE the container */}
            <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
              {benefits.map((benefit, index) => (
                <div
                  key={index}
                  className="flex gap-6 p-8 rounded-2xl bg-gradient-to-b from-card to-[hsl(240_20%_99%)] border border-border hover:shadow-lg hover:scale-[1.02] transition-all duration-300 ease-in-out"
                >
                  {/* Icon removed */}
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold">
                      {benefit.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {benefit.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyChooseSection;


