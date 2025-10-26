import { ArrowLeft, AlertCircle, CheckCircle, Star, Share2 } from "lucide-react";
import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Progress } from "../ui/progress";
import { useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface ResultsSectionProps {
  data: any;
  onReset: () => void;
}

export function ResultsSection({ data, onReset }: ResultsSectionProps) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);

  // Prepare data for pie chart
  const pieData = [
    { name: 'Fake', value: data.confidence?.fake || data.confidence || 0, color: '#ef4444' },
    { name: 'Real', value: data.confidence?.real || (100 - (data.confidence || 0)), color: '#22c55e' }
  ];

  // WhatsApp share handler - Use backend's formatted message
  const handleWhatsAppShare = () => {
    // Check if backend provided WhatsApp share data
    if (data.whatsapp_share?.share_url) {
      // Use backend's pre-formatted URL with complete message
      window.open(data.whatsapp_share.share_url, '_blank');
    } else {
      // Fallback: Create message manually if backend data not available
      const message = encodeURIComponent(
        `🔍 SachAI Analysis Results\n\n` +
        `News: ${data.query || ""}\n\n` +
        `Verdict: ${data.prediction || (data.isFake ? "Fake News" : "Real News")}\n` +
        `Confidence: ${data.confidence?.fake || data.confidence}%\n\n` +
        `${data.description || data.explanation?.verdict || ""}\n\n` +
        `Checked with SachAI - Your trusted fact-checking companion`
      );
      window.open(`https://wa.me/?text=${message}`, '_blank');
    }
  };

return (
  <div className="py-12 relative z-20">
    {/* Back Button */}
    <Button
      onClick={onReset}
      variant="ghost"
      className="mb-8 text-muted-foreground hover:text-foreground"
    >
      <ArrowLeft className="mr-2" size={18} />
      Check another
    </Button>


      {/* Results Container */}
      <div className="space-y-8">
        {/* Query Display with Highlights */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <h2 className="text-xl mb-4 text-black">Analyzed Content</h2>
          <div className="text-lg leading-relaxed">
            {data.highlightedQuery.map((segment: any, index: number) => (
              <span
                key={index}
                className={
                  segment.isSuspicious
                    ? "bg-red-500/20 text-black px-1 rounded border-b-2 border-red-500/50"
                    : "text-foreground"
                }
              >
                {segment.text}
              </span>
            ))}
          </div>
        </Card>

        {/* Confidence Score with Pie Chart */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl mb-2 text-black">Credibility Score</h2>
                  <p className="text-sm text-black">
                    Based on AI analysis of content patterns and sources
                  </p>
                </div>
                <Button
                  onClick={handleWhatsAppShare}
                  className="bg-[#25D366] hover:bg-[#20BA5A] text-white gap-2"
                >
                  <Share2 size={18} />
                  Share on WhatsApp
                </Button>
              </div>
              
              {/* Pie Chart */}
              <div className="w-full h-64 mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="space-y-2 mt-4">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Accuracy Assessment</span>
              <span
                className={
                  data.isFake
                    ? "text-red-400"
                    : "text-green-400"
                }
              >
                {data.isFake ? "Likely False" : "Likely True"}
              </span>
            </div>
            <Progress
              value={data.confidence?.fake || data.confidence}
              className="h-2"
            />
          </div>
        </Card>

        {/* Explanation Card */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="flex items-start gap-3 mb-4">
            {data.isFake ? (
              <AlertCircle className="text-red-500 flex-shrink-0 mt-1" size={24} />
            ) : (
              <CheckCircle className="text-green-500 flex-shrink-0 mt-1" size={24} />
            )}
            <div>
              <h2 className="text-xl mb-2 text-muted-foreground">Analysis Result</h2>
              <p className="text-lg mb-4">
                Verdict: <span className={data.isFake ? "text-red-400" : "text-green-400"}>{data.explanation.verdict}</span>
              </p>
            </div>
          </div>

          <div className="space-y-3 pl-9">
            <p className="text-muted-foreground text-sm mb-3">Key indicators:</p>
            {data.explanation.reasons.map((reason: string, index: number) => (
              <div key={index} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                <p className="text-foreground">{reason}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Related Articles */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <h2 className="text-xl mb-4 text-muted-foreground">Related Articles</h2>
          <div className="space-y-3">
            {data.relatedArticles.map((article: any, index: number) => (
              <a
                key={index}
                href={article.url}
                className="block p-4 bg-accent/30 hover:bg-accent/50 rounded-xl border border-border hover:border-ring transition-all group"
              >
                <h3 className="text-foreground mb-2 group-hover:text-blue-400 transition-colors">
                  {article.title}
                </h3>
                <p className="text-sm text-muted-foreground">{article.source}</p>
              </a>
            ))}
          </div>
        </Card>

        {/* Feedback Module */}
        <Card className="bg-card/50 backdrop-blur-sm border-border p-6">
          <div className="text-center">
            <h2 className="text-xl mb-4 text-muted-foreground">How useful was this result?</h2>
            <div className="flex justify-center gap-2 mb-4">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoveredStar(star)}
                  onMouseLeave={() => setHoveredStar(0)}
                  className="transition-all transform hover:scale-110"
                >
                  <Star
                    size={32}
                    className={
                      star <= (hoveredStar || rating)
                        ? "fill-yellow-500 text-yellow-500"
                        : "text-muted-foreground"
                    }
                  />
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-sm text-muted-foreground">
                Thank you for your feedback!
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
