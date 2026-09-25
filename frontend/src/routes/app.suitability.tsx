import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Leaf, CheckCircle2, Loader2, AlertCircle, Sparkles, BarChart3, Info } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { EnvForm } from "@/components/opticrop/EnvForm";
import { defaultInput, crops as defaultCrops, IDEAL_CROP_CONDITIONS, type PredictionInput } from "@/lib/agronomy";
import { api, SinglePredictionResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export const Route = createFileRoute("/app/suitability")({
  component: Suitability,
});

function Suitability() {
  const [crop, setCrop] = useState<string>("Wheat");
  const [availableCrops, setAvailableCrops] = useState<string[]>([...defaultCrops]);
  const [benchmarks, setBenchmarks] = useState<Record<string, PredictionInput>>(IDEAL_CROP_CONDITIONS);
  const [datasetName, setDatasetName] = useState<string>("");
  const [input, setInput] = useState<PredictionInput>(IDEAL_CROP_CONDITIONS["Wheat"] || defaultInput);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SinglePredictionResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Dynamically load active model classes and crop benchmarks from the uploaded CSV
  useEffect(() => {
    let mounted = true;
    async function loadDynamicInsights() {
      try {
        const insights = await api.models.getInsights();
        if (!mounted) return;

        if (insights.classes && insights.classes.length > 0) {
          setAvailableCrops(insights.classes);
          // If current crop is not in classes, switch to first class
          if (!insights.classes.includes(crop)) {
            setCrop(insights.classes[0]);
          }
        }

        if (insights.crop_benchmarks && Object.keys(insights.crop_benchmarks).length > 0) {
          const merged: Record<string, PredictionInput> = { ...IDEAL_CROP_CONDITIONS };
          for (const [cName, bm] of Object.entries(insights.crop_benchmarks)) {
            merged[cName] = {
              n: bm.n ?? defaultInput.n,
              p: bm.p ?? defaultInput.p,
              k: bm.k ?? defaultInput.k,
              temperature: bm.temperature ?? defaultInput.temperature,
              humidity: bm.humidity ?? defaultInput.humidity,
              ph: bm.ph ?? defaultInput.ph,
              rainfall: bm.rainfall ?? defaultInput.rainfall,
            };
          }
          setBenchmarks(merged);
        }

        if (insights.dataset?.name) {
          setDatasetName(insights.dataset.name);
        }
      } catch (err) {
        console.warn("Could not load dynamic model insights:", err);
      }
    }

    loadDynamicInsights();
    return () => {
      mounted = false;
    };
  }, []);

  const handleCropChange = (newCrop: string) => {
    setCrop(newCrop);
    setResult(null);
    setErrorMessage(null);
  };

  const loadCropBenchmarks = () => {
    const ideal = benchmarks[crop] || IDEAL_CROP_CONDITIONS[crop];
    if (ideal) {
      setInput({ ...ideal });
      setResult(null);
      toast.info(`Loaded ideal growing conditions for ${crop} from active dataset.`);
    } else {
      toast.info(`Using standard baseline for ${crop}.`);
    }
  };

  const check = async () => {
    setLoading(true);
    setResult(null);
    setErrorMessage(null);

    try {
      const res = await api.predictions.predict({
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
      setResult(res);
      toast.success("Suitability evaluation completed across all dataset crops.");
    } catch (err: any) {
      const msg = err?.message || "Failed to evaluate suitability.";
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const topCrop = result?.predictions?.[0] ? String(result.predictions[0]) : null;
  const confidence =
    result?.confidence_scores && result.confidence_scores.length > 0
      ? Math.round(result.confidence_scores[0] * 100)
      : null;

  // Extract multi-crop probabilities map from prediction response
  const rawProbMap: Record<string, number> =
    (Array.isArray(result?.probabilities) ? result.probabilities[0] : null) ||
    result?.prediction_metadata?.probabilities?.[0] ||
    (typeof result?.probabilities === "object" && !Array.isArray(result.probabilities) ? (result.probabilities as any) : null) ||
    {};

  // Build ranked array of all crops from the uploaded CSV
  const rankedCrops = Object.entries(rawProbMap)
    .map(([cName, prob]) => ({
      name: cName,
      percentage: Math.round(Number(prob) * 100),
      rawProb: Number(prob),
    }))
    .sort((a, b) => b.rawProb - a.rawProb);

  // Probability score for the selected target crop
  const targetCropScore =
    rawProbMap[crop] !== undefined
      ? Math.round(Number(rawProbMap[crop]) * 100)
      : topCrop && topCrop.toLowerCase() === crop.toLowerCase() && confidence !== null
      ? confidence
      : 0;

  const isSelectedCropTop = topCrop && topCrop.toLowerCase() === crop.toLowerCase();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Crop Suitability Checker"
        description="Evaluate environmental suitability for a target crop and compare all crop options in your active dataset."
      />

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left Form: Target Crop & Sliders */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-3">
          <div className="mb-5 space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-sm font-semibold">Target Crop to Evaluate</Label>
                {datasetName && (
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Options loaded from active dataset: <span className="font-medium text-foreground">{datasetName}</span>
                  </p>
                )}
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 px-2.5 text-xs text-primary border-primary/30 hover:bg-primary/10"
                onClick={loadCropBenchmarks}
              >
                <Sparkles className="mr-1.5 h-3.5 w-3.5" /> Fill {crop} Ideal Values
              </Button>
            </div>

            <Select value={crop} onValueChange={handleCropChange}>
              <SelectTrigger className="h-11 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="max-h-72">
                {availableCrops.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="rounded-lg bg-muted/40 p-2.5 text-[11px] text-muted-foreground flex items-start gap-2">
              <Info className="h-3.5 w-3.5 mt-0.5 text-primary shrink-0" />
              <span>
                <strong>How it works:</strong> Click <em>"Fill {crop} Ideal Values"</em> to load {crop}&apos;s baseline growing conditions from your CSV, then adjust sliders to test your field&apos;s real-world conditions.
              </span>
            </div>
          </div>

          <EnvForm value={input} onChange={setInput} />

          <Button variant="hero" size="lg" className="mt-6 w-full" onClick={check} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" /> Evaluating All Crops...
              </>
            ) : (
              <>
                <Leaf className="h-4 w-4 mr-2" /> Check Suitability
              </>
            )}
          </Button>
        </Card>

        {/* Right Card: Multi-Crop Evaluation & Suitability Result */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-2 flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-border/60">
            <h2 className="font-display text-lg font-600">Suitability Result</h2>
            {rankedCrops.length > 0 && (
              <Badge variant="outline" className="text-xs font-normal">
                {rankedCrops.length} crops evaluated
              </Badge>
            )}
          </div>

          {loading ? (
            <div className="flex flex-1 h-80 items-center justify-center">
              <span className="animate-ai-pulse grid h-16 w-16 place-items-center rounded-full bg-primary/15 text-primary">
                <Leaf className="h-8 w-8" />
              </span>
            </div>
          ) : errorMessage ? (
            <div className="mt-4">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Model Required</AlertTitle>
                <AlertDescription className="mt-2 text-xs leading-relaxed">
                  {errorMessage}
                  <div className="mt-2 text-muted-foreground">
                    Suitability checks require an active, trained ML model deployed in your project.
                  </div>
                </AlertDescription>
              </Alert>
            </div>
          ) : result && topCrop ? (
            <div className="mt-4 space-y-6 flex-1">
              {/* Primary Comparison Header */}
              <div className="rounded-xl border border-border/60 bg-muted/30 p-4 text-center">
                <p className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                  {crop} vs. Model Optimum
                </p>
                <div
                  className={cn(
                    "mt-2 flex items-center justify-center gap-2 font-display text-2xl font-800",
                    isSelectedCropTop ? "text-primary" : "text-amber-500"
                  )}
                >
                  <CheckCircle2 className="h-6 w-6" />
                  {isSelectedCropTop ? "Optimal Match" : `Model Prefers ${topCrop}`}
                </div>

                <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
                  {isSelectedCropTop
                    ? `Your trained model confirms ${crop} is the #1 recommended crop for these soil and climate parameters.`
                    : `Under these conditions, ${topCrop} (${confidence}%) ranks higher than your target crop ${crop} (${targetCropScore}%).`}
                </p>
              </div>

              {/* Target Crop Meter */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-foreground flex items-center gap-1.5">
                    <Leaf className="h-3.5 w-3.5 text-primary" /> {crop} Suitability Score
                  </span>
                  <Badge
                    variant={isSelectedCropTop ? "default" : targetCropScore > 20 ? "secondary" : "outline"}
                    className="font-mono text-xs"
                  >
                    {targetCropScore}% match
                  </Badge>
                </div>
                <Progress
                  value={targetCropScore}
                  className={cn(
                    "h-2.5",
                    isSelectedCropTop ? "[&>div]:bg-primary" : "[&>div]:bg-amber-500"
                  )}
                />
              </div>

              {/* All Crops Comparative Breakdown */}
              {rankedCrops.length > 0 && (
                <div className="space-y-3 pt-2 border-t border-border/60">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                      <BarChart3 className="h-3.5 w-3.5 text-primary" /> Comparative Crop Breakdown
                    </p>
                    <span className="text-[11px] text-muted-foreground">All CSV Components</span>
                  </div>

                  <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                    {rankedCrops.map((rc) => {
                      const isTarget = rc.name.toLowerCase() === crop.toLowerCase();
                      const isTop = rc.name.toLowerCase() === topCrop.toLowerCase();

                      return (
                        <div
                          key={rc.name}
                          className={cn(
                            "rounded-lg p-2.5 border text-xs transition-colors",
                            isTarget
                              ? "bg-primary/10 border-primary/40 font-semibold"
                              : isTop
                              ? "bg-amber-500/10 border-amber-500/30"
                              : "bg-background/50 border-border/50 text-muted-foreground"
                          )}
                        >
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="flex items-center gap-1.5 text-foreground">
                              {rc.name}
                              {isTarget && (
                                <Badge variant="default" className="h-4 text-[10px] px-1.5">
                                  Target
                                </Badge>
                              )}
                              {isTop && !isTarget && (
                                <Badge variant="secondary" className="h-4 text-[10px] px-1.5 text-amber-600 bg-amber-100 dark:bg-amber-950">
                                  Top Pick
                                </Badge>
                              )}
                            </span>
                            <span className="font-mono font-semibold text-foreground">
                              {rc.percentage}%
                            </span>
                          </div>
                          <Progress
                            value={rc.percentage}
                            className={cn(
                              "h-1.5",
                              isTarget
                                ? "[&>div]:bg-primary"
                                : isTop
                                ? "[&>div]:bg-amber-500"
                                : "[&>div]:bg-muted-foreground/40"
                            )}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-1 h-80 flex-col items-center justify-center gap-3 text-center">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-muted text-muted-foreground">
                <Leaf className="h-8 w-8" />
              </span>
              <p className="text-sm font-medium text-foreground">Ready to evaluate crop suitability</p>
              <p className="text-xs text-muted-foreground max-w-xs">
                Select any crop available in your uploaded CSV, populate or adjust environmental parameters, and click Check Suitability.
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
