import { motion } from "framer-motion";
import { ClinicalPattern, RiskScore } from "@/lib/bloodAnalysis";
import { AlertTriangle, Activity, Heart, Shield } from "lucide-react";

const severityStyles = {
  low: { badge: "bg-status-normal-bg text-status-normal", icon: Shield },
  moderate: { badge: "bg-status-low-bg text-status-low", icon: Activity },
  high: { badge: "bg-status-high-bg text-status-high", icon: AlertTriangle },
};

interface PatternCardsProps {
  patterns: ClinicalPattern[];
  riskScores: RiskScore[];
}

const PatternCards = ({ patterns, riskScores }: PatternCardsProps) => {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <h3 className="text-lg font-display font-semibold text-foreground mb-4">Clinical Patterns Detected</h3>
        {patterns.length === 0 ? (
          <div className="bg-card rounded-xl p-6 shadow-card text-center text-muted-foreground">
            No significant clinical patterns detected. All parameters appear within normal ranges.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {patterns.map((pattern, i) => {
              const style = severityStyles[pattern.severity];
              const Icon = style.icon;
              return (
                <motion.div
                  key={pattern.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 + i * 0.08 }}
                  className="bg-card rounded-xl p-5 shadow-card border border-border hover:shadow-elevated transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-5 h-5 ${pattern.severity === "high" ? "text-status-high" : pattern.severity === "moderate" ? "text-status-low" : "text-status-normal"}`} />
                      <h4 className="font-display font-semibold text-card-foreground text-sm">{pattern.name}</h4>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.badge}`}>
                      {pattern.severity}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{pattern.description}</p>
                  <p className="text-xs text-muted-foreground">{pattern.details}</p>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {pattern.parameters.map((p) => (
                      <span key={p} className="text-xs bg-muted px-2 py-0.5 rounded-md text-muted-foreground">{p}</span>
                    ))}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
        <h3 className="text-lg font-display font-semibold text-foreground mb-4">Risk Scores</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {riskScores.map((score, i) => {
            const style = severityStyles[score.severity];
            return (
              <motion.div
                key={score.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.08 }}
                className="bg-card rounded-xl p-5 shadow-card text-center"
              >
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">{score.name}</p>
                <p className={`text-3xl font-display font-bold ${score.severity === "high" ? "text-status-high" : score.severity === "moderate" ? "text-status-low" : "text-status-normal"}`}>
                  {score.value}
                </p>
                <span className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full font-medium ${style.badge}`}>
                  {score.interpretation}
                </span>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};

export default PatternCards;
