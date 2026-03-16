import { BloodParameter } from "@/lib/bloodAnalysis";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";

interface ParameterChartProps {
  parameters: BloodParameter[];
}

const classColor: Record<string, string> = {
  low: "hsl(38, 92%, 50%)",
  normal: "hsl(152, 60%, 42%)",
  high: "hsl(0, 72%, 51%)",
};

const ParameterChart = ({ parameters }: ParameterChartProps) => {
  const data = parameters.map((p) => ({
    name: p.name.replace(/\s*\(.*\)/, "").slice(0, 12),
    value: p.value,
    low: p.referenceRange.low,
    high: p.referenceRange.high,
    classification: p.classification,
  }));

  return (
    <div className="bg-card rounded-xl shadow-card p-6">
      <h3 className="text-lg font-display font-semibold text-card-foreground mb-4">Parameter Overview</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <XAxis
              dataKey="name"
              tick={{ fontSize: 10, fill: "hsl(215, 15%, 50%)" }}
              axisLine={false}
              tickLine={false}
              angle={-25}
              textAnchor="end"
              height={60}
            />
            <YAxis tick={{ fontSize: 10, fill: "hsl(215, 15%, 50%)" }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                background: "hsl(0, 0%, 100%)",
                border: "1px solid hsl(210, 20%, 90%)",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              formatter={(value: number, name: string, props: any) => {
                const item = props.payload;
                return [`${value} (Range: ${item.low}–${item.high})`, item.name];
              }}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={32}>
              {data.map((entry, index) => (
                <Cell key={index} fill={classColor[entry.classification]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ParameterChart;
