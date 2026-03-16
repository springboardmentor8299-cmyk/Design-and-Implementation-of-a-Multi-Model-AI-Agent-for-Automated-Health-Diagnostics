import { motion } from "framer-motion";
import { Recommendation } from "@/lib/bloodAnalysis";
import { Apple, Dumbbell, Heart, Stethoscope } from "lucide-react";

const categoryConfig = {
  diet: { icon: Apple, label: "Dietary" },
  exercise: { icon: Dumbbell, label: "Exercise" },
  lifestyle: { icon: Heart, label: "Lifestyle" },
  medical: { icon: Stethoscope, label: "Medical" },
};

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

const RecommendationsList = ({ recommendations }: RecommendationsListProps) => {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
      <h3 className="text-lg font-display font-semibold text-foreground mb-4">Personalized Recommendations</h3>
      <div className="space-y-3">
        {recommendations.map((rec, i) => {
          const config = categoryConfig[rec.category];
          const Icon = config.icon;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.05 }}
              className="bg-card rounded-lg p-4 shadow-card flex items-start gap-4 border border-border"
            >
              <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${
                rec.priority === "high" ? "bg-status-high-bg" : rec.priority === "moderate" ? "bg-status-low-bg" : "bg-muted"
              }`}>
                <Icon className={`w-4 h-4 ${
                  rec.priority === "high" ? "text-status-high" : rec.priority === "moderate" ? "text-status-low" : "text-muted-foreground"
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-card-foreground">{rec.text}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs bg-muted px-2 py-0.5 rounded text-muted-foreground">{config.label}</span>
                  <span className="text-xs text-muted-foreground">Based on: {rec.source}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default RecommendationsList;
