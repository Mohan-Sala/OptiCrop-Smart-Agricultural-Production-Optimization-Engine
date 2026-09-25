import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Sprout, Sparkles, Loader2, Brain, AlertCircle } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Cell,
} from "recharts";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { EnvForm } from "@/components/opticrop/EnvForm";
import { ChartCard } from "@/components/opticrop/ChartCard";
import { defaultInput, type PredictionInput } from "@/lib/agronomy";
import { api, SinglePredictionResponse } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/app/recommendation")({
  component: Recommendation,
});

export const tooltipStyle = {
  backgroundColor: "var(--color-card)",
  borderColor: "var(--color-border)",
  borderRadius: "12px",
  boxShadow: "var(--shadow-lift)",
};

function Recommendation() {
  const [input, setInput] = useState<PredictionInput>(defaultInput);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SinglePredictionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const predict = async () => {
    setLoading(true);
    setResult(null);
    setErrorMessage(null);

    try {
      const response = await api.predictions.predict({
        features: {
          n: input.n,
          p: input.p,
          k: input.k,
          temperature: input.temperature,
          humidity: input.humidity,
          ph: input.ph,
          rainfall: input.rainfall,
        },
      });

      setResult(response);
      toast.success("Prediction completed and persisted to MongoDB Atlas!");
    } catch (err: any) {
      const msg = err?.message || "Failed to execute prediction.";
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
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

  const predictedCrop = result?.predictions?.[0] ? String(result.predictions[0]) : null;
  const confidence =
    result?.confidence_scores && result.confidence_scores.length > 0
      ? Math.round(result.confidence_scores[0] * 100)
      : null;

  return (
    <div>
      <PageHeader
        title="Crop Recommendation"
        description="Submit soil and climate parameters to execute real-time model inference persisted in MongoDB Atlas."
      />

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Form */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-3">
          <h2 className="font-display text-lg font-600">Environmental Parameters</h2>
          <p className="mb-5 text-sm text-muted-foreground">Adjust input parameters for model execution.</p>
          <EnvForm value={input} onChange={setInput} />
          <Button variant="hero" size="lg" className="mt-6 w-full" onClick={predict} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" /> Running MongoDB Inference...
              </>
            ) : (
              <>
                <Sprout className="h-4 w-4 mr-2" /> Predict Crop
              </>
            )}
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
              <p className="text-sm text-muted-foreground">Evaluating against trained model in MongoDB...</p>
            </div>
          ) : errorMessage ? (
            <div className="mt-4">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Prediction Engine Notice</AlertTitle>
                <AlertDescription className="mt-2 text-xs leading-relaxed">
                  {errorMessage}
                  <div className="mt-3">
                    <span className="text-muted-foreground">
                      OptiCrop AI requires an active, trained ML model deployed in your project to serve predictions.
                    </span>
                  </div>
                </AlertDescription>
              </Alert>
            </div>
          ) : result && predictedCrop ? (
            <div className="mt-4 space-y-5">
              <div className="rounded-[20px] bg-primary/8 p-5 text-center">
                <p className="text-sm text-muted-foreground">Recommended Crop</p>
                <p className="mt-1 flex items-center justify-center gap-2 font-display text-4xl font-800 text-primary">
                  <Sprout className="h-8 w-8" /> {predictedCrop}
                </p>
                <Badge variant="secondary" className="mt-3 rounded-full">
                  Persisted to MongoDB Atlas
                </Badge>
              </div>
              {confidence !== null && (
                <div>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Confidence Score</span>
                    <span className="font-700 text-primary">{confidence}%</span>
                  </div>
                  <Progress value={confidence} className="h-2.5" />
                </div>
              )}
              <div className="rounded-xl border border-border/60 bg-muted/40 p-4">
                <p className="flex items-center gap-2 text-sm font-600">
                  <Sparkles className="h-4 w-4 text-primary" /> Execution Audit
                </p>
                <p className="mt-1 font-mono text-xs text-muted-foreground">
                  Latency: {result.execution_time_ms.toFixed(1)}ms · Run ID: {result.prediction_id}
                </p>
              </div>
            </div>
          ) : (
            <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-muted text-muted-foreground">
                <Sprout className="h-8 w-8" />
              </span>
              <p className="text-sm text-muted-foreground">
                Submit environmental parameters to run inference against your trained model.
              </p>
            </div>
          )}
        </Card>
      </div>

      {/* Visualization */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="NPK Levels" description="Current nutrient input parameters">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={npkData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-muted)" }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {npkData.map((d, i) => (
                  <Cell key={i} fill={d.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Climate Radar" description="Normalized environmental conditions">
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="var(--color-border)" />
              <PolarAngleAxis dataKey="metric" fontSize={12} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="var(--color-primary)" fill="var(--color-primary)" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
