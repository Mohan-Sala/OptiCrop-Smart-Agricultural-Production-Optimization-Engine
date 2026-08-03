import { createFileRoute } from "@tanstack/react-router";
import { Fragment } from "react";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid, Cell,
} from "recharts";
import { Trophy, Brain } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { ChartCard } from "@/components/opticrop/ChartCard";
import { tooltipStyle } from "@/routes/app.recommendation";
import { modelComparison, featureImportance } from "@/lib/mock-data";

export const Route = createFileRoute("/app/models")({
  component: Models,
});

// confusion matrix (rows = actual, cols = predicted)
const cmLabels = ["Rice", "Wheat", "Maize", "Cotton"];
const cm = [
  [48, 1, 1, 0],
  [0, 45, 2, 1],
  [1, 1, 47, 1],
  [0, 1, 0, 49],
];

function Models() {
  return (
    <div>
      <PageHeader title="Model Insights" description="Compare machine learning models, accuracy, and decision drivers." />

      <Card className="animate-fade-up mb-6 flex items-center gap-4 rounded-[20px] border-border/70 bg-primary/5 p-6 shadow-[var(--shadow-soft)]">
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-primary text-primary-foreground">
          <Trophy className="h-7 w-7" />
        </span>
        <div>
          <p className="text-sm text-muted-foreground">Best Performing Model</p>
          <p className="font-display text-2xl font-800 text-primary">Random Forest — 98.6%</p>
        </div>
        <Badge variant="secondary" className="ml-auto rounded-full">Deployed</Badge>
      </Card>

      <Card className="overflow-hidden rounded-[20px] border-border/70 shadow-[var(--shadow-soft)]">
        <div className="p-5"><h2 className="font-display text-lg font-600">Model Comparison</h2></div>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-border/60">
                <TableHead>Model</TableHead>
                <TableHead className="text-right">Accuracy</TableHead>
                <TableHead className="text-right">Precision</TableHead>
                <TableHead className="text-right">Recall</TableHead>
                <TableHead className="text-right">F1 Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {modelComparison.map((m) => (
                <TableRow key={m.model} className="border-border/60">
                  <TableCell className="font-600">
                    {m.model}{m.best && <Badge variant="secondary" className="ml-2 rounded-full"><Brain className="mr-1 h-3 w-3" /> Best</Badge>}
                  </TableCell>
                  <TableCell className="text-right font-600 text-primary">{m.accuracy}%</TableCell>
                  <TableCell className="text-right">{m.precision}</TableCell>
                  <TableCell className="text-right">{m.recall}</TableCell>
                  <TableCell className="text-right">{m.f1}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="Accuracy Comparison" description="Across all trained models">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={modelComparison}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="model" tickLine={false} axisLine={false} fontSize={11} interval={0} angle={-12} textAnchor="end" height={50} />
              <YAxis domain={[85, 100]} tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="accuracy" radius={[8, 8, 0, 0]}>
                {modelComparison.map((m, i) => <Cell key={i} fill={m.best ? "var(--color-chart-1)" : "var(--color-chart-2)"} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Feature Importance" description="Random Forest drivers">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={featureImportance} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="feature" tickLine={false} axisLine={false} fontSize={12} width={90} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="value" radius={[0, 8, 8, 0]} fill="var(--color-chart-1)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Confusion Matrix" description="Random Forest — actual vs predicted" className="mt-6">
        <div className="overflow-x-auto">
          <div className="min-w-[420px]">
            <div className="grid grid-cols-[90px_repeat(4,1fr)] gap-1 text-center text-sm">
              <div />
              {cmLabels.map((l) => <div key={l} className="pb-1 font-600 text-muted-foreground">{l}</div>)}
              {cm.map((row, r) => {
                const max = Math.max(...row);
                return (
                  <Fragment key={`cm-${r}`}>
                    <div className="flex items-center justify-end pr-2 font-600 text-muted-foreground">{cmLabels[r]}</div>
                    {row.map((v, c) => (
                      <div key={`${r}-${c}`} className="grid aspect-square place-items-center rounded-lg font-600"
                        style={{
                          background: `color-mix(in oklab, var(--color-chart-1) ${Math.round((v / max) * 100)}%, var(--color-muted))`,
                          color: v / max > 0.5 ? "var(--color-primary-foreground)" : "var(--color-foreground)",
                        }}>
                        {v}
                      </div>
                    ))}
                  </Fragment>
                );
              })}
            </div>
          </div>
        </div>
      </ChartCard>
    </div>
  );
}
