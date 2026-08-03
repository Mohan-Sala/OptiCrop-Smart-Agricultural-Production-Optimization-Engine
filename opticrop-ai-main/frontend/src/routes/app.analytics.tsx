import { createFileRoute } from "@tanstack/react-router";
import { Fragment } from "react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  AreaChart, Area, BarChart, Bar,
} from "recharts";
import { Database, Layers, ListChecks, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { MetricCard } from "@/components/opticrop/MetricCard";
import { ChartCard } from "@/components/opticrop/ChartCard";
import { tooltipStyle } from "@/routes/app.recommendation";
import {
  cropDistribution, rainfallScatter, tempDistribution, phImpact,
} from "@/lib/mock-data";

export const Route = createFileRoute("/app/analytics")({
  component: Analytics,
});

const heatCrops = ["Rice", "Wheat", "Maize", "Cotton"];
const heatFeatures = ["N", "P", "K", "Temp", "Rain"];
// correlation-ish values 0..1
const heat = [
  [0.9, 0.4, 0.6, 0.3, 0.95],
  [0.5, 0.7, 0.4, 0.6, 0.4],
  [0.7, 0.5, 0.8, 0.7, 0.5],
  [0.8, 0.3, 0.5, 0.8, 0.35],
];

function Analytics() {
  return (
    <div>
      <PageHeader title="Analytics & Research" description="Explore dataset patterns, correlations, and AI-generated insights." />

      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard icon={Database} label="Total Dataset Size" value="10,245" sub="labeled samples" />
        <MetricCard icon={Layers} label="Crop Types" value="22" sub="unique classes" />
        <MetricCard icon={ListChecks} label="Feature Count" value="7" sub="input parameters" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="Crop Distribution" description="Share of samples per crop">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={cropDistribution} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={3}>
                {cropDistribution.map((d, i) => <Cell key={i} fill={d.fill} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Correlation Heatmap" description="Crops vs environmental features">
          <div className="overflow-x-auto">
            <div className="min-w-[360px]">
              <div className="grid grid-cols-[80px_repeat(5,1fr)] gap-1 text-center text-xs">
                <div />
                {heatFeatures.map((f) => <div key={f} className="pb-1 font-600 text-muted-foreground">{f}</div>)}
                {heat.map((row, r) => (
                  <Fragment key={`row-${r}`}>
                    <div className="flex items-center justify-end pr-2 font-600 text-muted-foreground">{heatCrops[r]}</div>
                    {row.map((v, c) => (
                      <div key={`${r}-${c}`} className="grid aspect-square place-items-center rounded-lg font-500 text-foreground"
                        style={{ background: `color-mix(in oklab, var(--color-chart-1) ${Math.round(v * 100)}%, var(--color-muted))` }}>
                        {v.toFixed(2)}
                      </div>
                    ))}
                  </Fragment>
                ))}
              </div>
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Rainfall vs Yield" description="Scatter across samples">
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis type="number" dataKey="rainfall" name="Rainfall" unit="mm" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis type="number" dataKey="yield" name="Yield" tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
              <Scatter data={rainfallScatter} fill="var(--color-chart-2)" />
            </ScatterChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Temperature Distribution" description="Sample frequency by temperature">
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={tempDistribution}>
              <defs>
                <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-chart-3)" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="var(--color-chart-3)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="t" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="v" stroke="var(--color-chart-3)" fill="url(#tempGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="pH Impact Analysis" description="Suitability score by pH" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={phImpact}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="ph" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="score" radius={[8, 8, 0, 0]} fill="var(--color-chart-1)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <Card className="mt-6 rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
        <h2 className="flex items-center gap-2 font-display text-lg font-600"><Sparkles className="h-5 w-5 text-primary" /> AI-Generated Insights</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[
            "Rainfall shows the strongest correlation with crop suitability, driving 28% of model decisions.",
            "Rice thrives in high-humidity, high-rainfall zones — clusters clearly around 200mm+ rainfall.",
            "Neutral pH (6.0–7.0) yields peak suitability scores across most crop classes.",
            "Nitrogen and potassium balance is more predictive than phosphorus for cereal crops.",
          ].map((t, i) => (
            <div key={i} className="rounded-xl border border-border/60 bg-muted/40 p-4 text-sm text-muted-foreground">{t}</div>
          ))}
        </div>
      </Card>
    </div>
  );
}
