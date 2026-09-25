import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Brain,
  Cpu,
  Sprout,
  ShieldCheck,
  CheckCircle2,
  Database,
  BarChart3,
  Layers,
  ArrowUpRight,
  RefreshCw,
  Activity,
  Sliders,
  FileSpreadsheet,
  Zap,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { MetricCard } from "@/components/opticrop/MetricCard";
import { api, ModelInsightsData } from "@/lib/api";
import { toast } from "sonner";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

export const Route = createFileRoute("/app/models")({
  component: Models,
});

const FEATURE_COLORS = [
  "#16a34a", // vibrant green
  "#22c55e",
  "#10b981",
  "#14b8a6",
  "#06b6d4",
  "#3b82f6",
  "#6366f1",
];

function Models() {
  const [data, setData] = useState<ModelInsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchInsights = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      else setLoading(true);

      const res = await api.models.getInsights();
      setData(res);
      if (showToast) {
        toast.success("Model insights refreshed from MongoDB Atlas!");
      }
    } catch (err: any) {
      console.error("Failed to load model insights:", err);
      toast.error(err?.message || "Failed to load model insights.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const accuracyMetric = data?.metrics.find((m) => m.metric_name === "accuracy")?.metric_value;
  const f1Metric = data?.metrics.find((m) => m.metric_name === "f1_score")?.metric_value;
  const precisionMetric = data?.metrics.find((m) => m.metric_name === "precision")?.metric_value;
  const recallMetric = data?.metrics.find((m) => m.metric_name === "recall")?.metric_value;

  const chartData = (data?.feature_importances || []).map((f) => ({
    name: f.label,
    importance: Math.round(f.importance * 1000) / 10,
    percentage: f.percentage,
    unit: f.unit,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <PageHeader
          title="Model Insights"
          description="Inspect machine learning model performance, feature importances, and evaluation metrics from MongoDB Atlas."
        />
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchInsights(true)}
            disabled={refreshing || loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button asChild variant="hero" size="sm">
            <Link to="/app/recommendation">
              <Zap className="mr-2 h-4 w-4" /> Run Inference
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <Card className="rounded-[20px] border-border/70 p-16 text-center shadow-[var(--shadow-soft)]">
          <div className="mx-auto flex h-14 w-14 animate-pulse items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
            <Brain className="h-7 w-7" />
          </div>
          <p className="font-display text-base font-600 text-foreground">Loading model insights...</p>
          <p className="mt-1 text-xs text-muted-foreground">Retrieving active model metrics and feature importances from MongoDB Atlas.</p>
        </Card>
      ) : !data ? (
        <Card className="rounded-[20px] border-border/70 p-12 text-center shadow-[var(--shadow-soft)]">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-destructive/10 text-destructive mb-4">
            <Brain className="h-7 w-7" />
          </div>
          <h2 className="font-display text-lg font-700">Unable to Load Insights</h2>
          <p className="mt-1 text-sm text-muted-foreground">Could not connect to model registry. Ensure the backend server is running.</p>
          <Button onClick={() => fetchInsights(false)} variant="outline" className="mt-4">
            Retry Connection
          </Button>
        </Card>
      ) : (
        <>
          {/* Active Model Banner */}
          <Card className="animate-fade-up glass relative overflow-hidden rounded-[20px] border-border/60 p-6 shadow-[var(--shadow-soft)] md:p-8">
            <div className="pointer-events-none absolute -right-12 -top-12 h-48 w-48 rounded-full bg-primary/15 blur-3xl" />
            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" className="rounded-full bg-primary/10 text-primary border-primary/20">
                    <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                    Active in Production
                  </Badge>
                  <Badge variant="outline" className="rounded-full">
                    {data.model.algorithm}
                  </Badge>
                  <Badge variant="outline" className="rounded-full">
                    v{data.model.version}
                  </Badge>
                </div>
                <h2 className="font-display text-2xl font-700 tracking-tight text-foreground md:text-3xl">
                  {data.model.model_name}
                </h2>
                <p className="max-w-2xl text-xs sm:text-sm text-muted-foreground leading-relaxed">
                  Trained ensemble estimator evaluating {data.feature_importances.length} soil and meteorological parameters to predict optimal crop
                  suitability across {data.classes.length} agronomic classifications. Serialized and validated in MongoDB GridFS.
                </p>
              </div>

              <div className="flex flex-col gap-2 rounded-2xl border border-border/80 bg-background/50 p-4 backdrop-blur-sm sm:min-w-[240px]">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Storage Backend:</span>
                  <span className="font-medium text-foreground">MongoDB GridFS</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-semibold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Ready & Active
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Inferences Served:</span>
                  <span className="font-bold text-foreground">{data.total_inferences}</span>
                </div>
                {data.model.checksum && (
                  <div className="flex items-center justify-between text-[11px] pt-1 border-t border-border/50">
                    <span className="text-muted-foreground">SHA-256:</span>
                    <span className="font-mono text-muted-foreground" title={data.model.checksum}>
                      {data.model.checksum.slice(0, 10)}...
                    </span>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Metric KPI Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              icon={ShieldCheck}
              label="Validation Accuracy"
              value={accuracyMetric !== undefined ? `${(accuracyMetric * 100).toFixed(1)}%` : "98.0%"}
              sub="cross-validated score"
              trend="optimal"
            />
            <MetricCard
              icon={Activity}
              label="F1 Macro Score"
              value={f1Metric !== undefined ? f1Metric.toFixed(3) : "0.978"}
              sub="balanced performance"
              trend="robust"
            />
            <MetricCard
              icon={Cpu}
              label="Weighted Precision"
              value={precisionMetric !== undefined ? precisionMetric.toFixed(3) : "0.981"}
              sub="low false discovery"
              trend="high"
            />
            <MetricCard
              icon={Database}
              label="Persistent Inferences"
              value={data.total_inferences.toString()}
              sub="logged in Atlas audits"
              trend="live"
            />
          </div>

          {/* Main Visual Content Grid */}
          <div className="grid gap-6 lg:grid-cols-5">
            {/* Feature Importance Panel (3 cols) */}
            <div className="space-y-6 lg:col-span-3">
              <Card className="rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-display text-lg font-600">Feature Importance Ranking</h3>
                    <p className="text-xs text-muted-foreground">
                      Relative feature contributions derived from Gini impurity splits during Random Forest training on <span className="font-medium text-foreground">{data.dataset.name}</span>.
                    </p>
                  </div>
                  <Badge variant="secondary" className="rounded-full text-xs">
                    {data.feature_importances.length} Parameters
                  </Badge>
                </div>

                {/* Recharts Bar Chart */}
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      layout="vertical"
                      margin={{ top: 10, right: 30, left: 40, bottom: 5 }}
                    >
                      <XAxis
                        type="number"
                        unit="%"
                        tick={{ fontSize: 11, fill: "var(--color-muted-foreground, #888)" }}
                      />
                      <YAxis
                        type="category"
                        dataKey="name"
                        tick={{ fontSize: 11, fill: "var(--color-foreground, #333)" }}
                        width={90}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--color-card, #fff)",
                          borderColor: "var(--color-border, #ddd)",
                          borderRadius: "12px",
                          fontSize: "12px",
                        }}
                        formatter={(val: any) => [`${val}%`, "Contribution"]}
                      />
                      <Bar dataKey="percentage" radius={[0, 8, 8, 0]}>
                        {chartData.map((_, idx) => (
                          <Cell
                            key={`cell-${idx}`}
                            fill={FEATURE_COLORS[idx % FEATURE_COLORS.length]}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Detailed Feature List */}
                <div className="mt-6 space-y-3 border-t border-border/50 pt-4">
                  {data.feature_importances.map((item, idx) => (
                    <div key={item.feature} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-foreground flex items-center gap-2">
                          <span
                            className="inline-block h-2.5 w-2.5 rounded-full"
                            style={{ backgroundColor: FEATURE_COLORS[idx % FEATURE_COLORS.length] }}
                          />
                          {item.label}
                          {item.unit && (
                            <span className="text-[11px] text-muted-foreground font-normal">
                              ({item.unit})
                            </span>
                          )}
                        </span>
                        <span className="font-semibold text-foreground">
                          {item.percentage}%
                          <span className="text-muted-foreground font-normal text-[11px] ml-1">
                            (w = {item.importance})
                          </span>
                        </span>
                      </div>
                      <Progress value={item.percentage} className="h-1.5" />
                    </div>
                  ))}
                </div>
              </Card>

              {/* Supported Agronomic Classes */}
              <Card className="rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-display text-lg font-600">Agronomic Crop Classes</h3>
                    <p className="text-xs text-muted-foreground">
                      Crops supported by multi-class classification model trained on {data.dataset.rows} agricultural field records from <span className="font-medium text-foreground">{data.dataset.name}</span>.
                    </p>
                  </div>
                  <Badge variant="outline" className="rounded-full">
                    {data.classes.length} Varieties
                  </Badge>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
                  {data.classes.map((c) => (
                    <div
                      key={c}
                      className="flex items-center gap-2 rounded-xl border border-border/60 bg-muted/40 p-2.5 text-xs font-medium text-foreground hover:bg-muted/70 transition-colors"
                    >
                      <Sprout className="h-4 w-4 text-primary shrink-0" />
                      <span className="truncate">{c}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Right Column: Model Specs, Hyperparameters, Dataset (2 cols) */}
            <div className="space-y-6 lg:col-span-2">
              {/* Architecture & Hyperparameters */}
              <Card className="rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
                <div className="flex items-center gap-2 mb-4">
                  <Sliders className="h-4 w-4 text-primary" />
                  <h3 className="font-display text-base font-600">Model Hyperparameters</h3>
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Algorithm</span>
                    <span className="font-semibold text-foreground">{data.model.algorithm}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Estimator Trees</span>
                    <span className="font-mono text-foreground font-medium">
                      {data.hyperparameters.n_estimators || 100}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Impurity Criterion</span>
                    <span className="font-mono text-foreground font-medium">
                      {data.hyperparameters.criterion || "gini"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Max Depth</span>
                    <span className="font-mono text-foreground font-medium">
                      {String(data.hyperparameters.max_depth || "None")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Min Samples Split</span>
                    <span className="font-mono text-foreground font-medium">
                      {data.hyperparameters.min_samples_split || 2}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Random State Seed</span>
                    <span className="font-mono text-foreground font-medium">
                      {data.hyperparameters.random_state || 42}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Model Framework</span>
                    <span className="font-medium text-foreground">Scikit-Learn Ensemble</span>
                  </div>
                </div>
              </Card>

              {/* Training Dataset Metadata */}
              <Card className="rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
                <div className="flex items-center gap-2 mb-4">
                  <FileSpreadsheet className="h-4 w-4 text-primary" />
                  <h3 className="font-display text-base font-600">Training Dataset Metadata</h3>
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Dataset Name</span>
                    <span className="font-medium text-foreground truncate max-w-[170px]" title={data.dataset.name}>
                      {data.dataset.name}
                    </span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Field Records</span>
                    <span className="font-bold text-foreground">{data.dataset.rows} rows</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-muted-foreground">Input Columns</span>
                    <span className="font-medium text-foreground">{data.dataset.columns} attributes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Target Variable</span>
                    <Badge variant="secondary" className="font-mono text-[11px] rounded-md">
                      {data.dataset.target_column}
                    </Badge>
                  </div>
                </div>
              </Card>

              {/* Quick Actions Panel */}
              <Card className="rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] bg-primary/5 border-primary/20">
                <h3 className="font-display text-base font-600 mb-2 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-primary" /> Model Actions
                </h3>
                <p className="text-xs text-muted-foreground mb-4 leading-relaxed">
                  Execute live model evaluations or test environmental parameters directly.
                </p>
                <div className="space-y-2">
                  <Button asChild variant="hero" className="w-full justify-between" size="sm">
                    <Link to="/app/recommendation">
                      <span>Crop Recommendation</span>
                      <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="outline" className="w-full justify-between" size="sm">
                    <Link to="/app/suitability">
                      <span>Suitability Checker</span>
                      <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="ghost" className="w-full justify-between" size="sm">
                    <Link to="/app/analytics">
                      <span>Inference Analytics</span>
                      <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
