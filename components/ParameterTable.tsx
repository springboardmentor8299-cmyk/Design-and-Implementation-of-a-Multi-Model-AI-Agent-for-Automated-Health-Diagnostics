import { motion } from "framer-motion";
import { BloodParameter } from "@/lib/bloodAnalysis";

interface ParameterTableProps {
  parameters: BloodParameter[];
}

const classColors: Record<string, { bg: string; text: string; label: string }> = {
  low: { bg: "bg-status-low-bg", text: "text-status-low", label: "Low" },
  normal: { bg: "bg-status-normal-bg", text: "text-status-normal", label: "Normal" },
  high: { bg: "bg-status-high-bg", text: "text-status-high", label: "High" },
};

const ParameterTable = ({ parameters }: ParameterTableProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-xl shadow-card overflow-hidden"
    >
      <div className="px-6 py-4 border-b border-border">
        <h3 className="text-lg font-display font-semibold text-card-foreground">
          Extracted Parameters
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-muted/50">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Parameter</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Reference Range</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Range Position</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {parameters.map((param, i) => {
              const colors = classColors[param.classification];
              const rangeWidth = param.referenceRange.high - param.referenceRange.low;
              const extendedLow = param.referenceRange.low - rangeWidth * 0.3;
              const extendedHigh = param.referenceRange.high + rangeWidth * 0.3;
              const totalRange = extendedHigh - extendedLow;
              const position = Math.max(0, Math.min(100, ((param.value - extendedLow) / totalRange) * 100));
              const normalStart = ((param.referenceRange.low - extendedLow) / totalRange) * 100;
              const normalEnd = ((param.referenceRange.high - extendedLow) / totalRange) * 100;

              return (
                <motion.tr
                  key={param.key}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="hover:bg-muted/30 transition-colors"
                >
                  <td className="px-6 py-4 text-sm font-medium text-card-foreground">{param.name}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`font-semibold ${colors.text}`}>
                      {param.value} <span className="font-normal text-muted-foreground">{param.unit}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">
                    {param.referenceRange.low} – {param.referenceRange.high} {param.unit}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                      {colors.label}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="w-32 h-3 bg-muted rounded-full relative overflow-hidden">
                      <div
                        className="absolute h-full bg-status-normal/20 rounded-full"
                        style={{ left: `${normalStart}%`, width: `${normalEnd - normalStart}%` }}
                      />
                      <div
                        className={`absolute w-2.5 h-2.5 rounded-full top-0.5 -ml-1.5 ${
                          param.classification === "normal" ? "bg-status-normal" : param.classification === "high" ? "bg-status-high" : "bg-status-low"
                        }`}
                        style={{ left: `${position}%` }}
                      />
                    </div>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default ParameterTable;
