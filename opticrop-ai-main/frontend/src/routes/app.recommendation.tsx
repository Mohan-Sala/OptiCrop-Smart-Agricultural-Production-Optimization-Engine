import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Sprout, Sparkles, Loader2, Brain } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Cell,
} from "recharts";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { EnvForm } from "@/components/opticrop/EnvForm";
import { ChartCard } from "@/components/opticrop/ChartCard";
import { defaultInput, featureImportance, type PredictionInput } from "@/lib/mock-data";

export const Route = createFileRoute("/app/recommendation")({
  component: Recommendation,
});

function Recommendation() {
  const [input, setInput] = useState<PredictionInput>(defaultInput);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const predict = () => {
    setLoading(true);
    setDone(false);
    setTimeout(() => {
      setLoading(false);
      setDone(true);
    }, 1600);
  };

  const npkData = [
    { name: "Nitrogen", value: input.n, fill: "var(--color-chart-1)" },
    { name: "Phosphorus", value: input.p, fill: "var(--color-chart-2)" },
    { name: "Potassium", value: input.k, fill: "var(--color-chart-3)" },
  ];
  const radarData = [
    { metric: "Temp", value: (input.temperature / 50) * 100 },
    { metric: "Humidity", value: input.humidity },
    { metric: "Rainfall", value: (input.rainfall / 400) * 100 },
    { metric: "pH", value: (input.ph / 14) * 100 },
    { metric: "N", value: (input.n / 200) * 100 },
  ];

  return (
    <div>
      <PageHeader
        title="Crop Recommendation"
        description="Enter your soil and climate parameters to get an AI crop recommendation."
      />

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Form */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-3">
          <h2 className="font-display text-lg font-600">Environmental Parameters</h2>
          <p className="mb-5 text-sm text-muted-foreground">Adjust sliders or type exact values.</p>
          <EnvForm value={input} onChange={setInput} />
          <Button variant="hero" size="lg" className="mt-6 w-full" onClick={predict} disabled={loading}>
            {loading ? (<><Loader2 className="h-4 w-4 animate-spin" /> AI Analyzing…</>) : (<><Sprout className="h-4 w-4" /> Predict Crop</>)}
          </Button>
        </Card>

        {/* Result */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-2">
          <h2 className="font-display text-lg font-600">Prediction Result</h2>
          {loading ? (
            <div className="flex h-64 flex-col items-center justify-center gap-4">
              <span className="animate-ai-pulse grid h-16 w-16 place-items-center rounded-full bg-primary/15 text-primary">
                <Brain className="h-8 w-8" />
              </span>
              <p className="text-sm text-muted-foreground">Running ensemble models…</p>
            </div>
          ) : done ? (
            <div className="mt-4 space-y-5">
              <div className="rounded-[20px] bg-primary/8 p-5 text-center">
                <p className="text-sm text-muted-foreground">Recommended Crop</p>
                <p className="mt-1 flex items-center justify-center gap-2 font-display text-4xl font-800 text-primary">
                  <Sprout className="h-8 w-8" /> Rice
                </p>
                <Badge variant="secondary" className="mt-3 rounded-full">High Confidence</Badge>
              </div>
              <div>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Confidence Score</span>
                  <span className="font-700 text-primary">96.4%</span>
                </div>
                <Progress value={96.4} className="h-2.5" />
              </div>
              <div className="rounded-xl border border-border/60 bg-muted/40 p-4">
                <p className="flex items-center gap-2 text-sm font-600"><Sparkles className="h-4 w-4 text-primary" /> Why this crop?</p>
                <p className="mt-2 text-sm text-muted-foreground">
                  Based on the given soil nutrients and environmental conditions, Rice is the most suitable crop.
                  High rainfall and moderate temperature with balanced NPK levels create ideal growing conditions.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-muted text-muted-foreground">
                <Sprout className="h-8 w-8" />
              </span>
              <p className="text-sm text-muted-foreground">Run a prediction to see your recommended crop here.</p>
            </div>
          )}
        </Card>
      </div>

      {/* Visualization */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <ChartCard title="NPK Levels" description="Current nutrient input">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={npkData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {npkData.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Climate Radar" description="Normalized conditions">
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="var(--color-border)" />
              <PolarAngleAxis dataKey="metric" fontSize={12} />
              <PolarRadiusAxis tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="var(--color-chart-1)" fill="var(--color-chart-1)" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Feature Importance" description="Model decision drivers">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={featureImportance} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="feature" tickLine={false} axisLine={false} fontSize={12} width={80} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="value" radius={[0, 8, 8, 0]} fill="var(--color-chart-2)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

export const tooltipStyle = {
  borderRadius: 12,
  border: "1px solid var(--color-border)",
  background: "var(--color-popover)",
  color: "var(--color-popover-foreground)",
  fontSize: 12,
} as const;
