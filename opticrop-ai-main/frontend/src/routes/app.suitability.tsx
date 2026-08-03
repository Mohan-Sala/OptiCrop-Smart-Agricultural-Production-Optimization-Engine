import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Leaf, CheckCircle2, Loader2, Lightbulb } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { EnvForm } from "@/components/opticrop/EnvForm";
import { defaultInput, crops, type PredictionInput } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/suitability")({
  component: Suitability,
});

function Suitability() {
  const [crop, setCrop] = useState("Wheat");
  const [input, setInput] = useState<PredictionInput>(defaultInput);
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState<number | null>(null);

  const check = () => {
    setLoading(true);
    setScore(null);
    setTimeout(() => {
      setLoading(false);
      setScore(87);
    }, 1400);
  };

  const status = score == null ? null : score >= 75 ? "Highly Suitable" : score >= 45 ? "Moderately Suitable" : "Not Suitable";
  const statusTone = score == null ? "" : score >= 75 ? "text-primary" : score >= 45 ? "text-warning" : "text-destructive";

  return (
    <div>
      <PageHeader title="Crop Suitability Checker" description="Check if your environment suits a selected crop and get improvement tips." />

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-3">
          <div className="mb-5 space-y-2">
            <Label>Select Crop</Label>
            <Select value={crop} onValueChange={setCrop}>
              <SelectTrigger className="h-11 rounded-xl"><SelectValue /></SelectTrigger>
              <SelectContent>
                {crops.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <EnvForm value={input} onChange={setInput} />
          <Button variant="hero" size="lg" className="mt-6 w-full" onClick={check} disabled={loading}>
            {loading ? (<><Loader2 className="h-4 w-4 animate-spin" /> Checking…</>) : (<><Leaf className="h-4 w-4" /> Check Suitability</>)}
          </Button>
        </Card>

        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)] lg:col-span-2">
          <h2 className="font-display text-lg font-600">Suitability Result</h2>
          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <span className="animate-ai-pulse grid h-16 w-16 place-items-center rounded-full bg-primary/15 text-primary"><Leaf className="h-8 w-8" /></span>
            </div>
          ) : score != null ? (
            <div className="mt-4 space-y-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">{crop} suitability</p>
                <p className={cn("mt-1 flex items-center justify-center gap-2 font-display text-2xl font-800", statusTone)}>
                  <CheckCircle2 className="h-6 w-6" /> {status}
                </p>
              </div>
              <ScoreMeter score={score} />
              <div className="rounded-xl border border-border/60 bg-muted/40 p-4">
                <p className="flex items-center gap-2 text-sm font-600"><Lightbulb className="h-4 w-4 text-accent" /> Suggestions</p>
                <ul className="mt-2 space-y-1.5 text-sm text-muted-foreground">
                  <li>• Maintain current nitrogen levels.</li>
                  <li>• Increase phosphorus slightly for better yield.</li>
                  <li>• Ensure proper irrigation for consistent moisture.</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
              <span className="grid h-16 w-16 place-items-center rounded-full bg-muted text-muted-foreground"><Leaf className="h-8 w-8" /></span>
              <p className="text-sm text-muted-foreground">Select a crop and run the check to see suitability.</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

function ScoreMeter({ score }: { score: number }) {
  return (
    <div className="text-center">
      <div className="relative mx-auto h-3 w-full overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary transition-all duration-700" style={{ width: `${score}%` }} />
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>0</span>
        <Badge variant="secondary" className="rounded-full">Score {score}/100</Badge>
        <span>100</span>
      </div>
    </div>
  );
}
