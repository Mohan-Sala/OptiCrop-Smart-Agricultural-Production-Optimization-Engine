import { Brain, Leaf, TrendingUp, Sparkles } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { Logo } from "@/components/opticrop/Logo";

export function AuthAside() {
  return (
    <div className="relative hidden overflow-hidden bg-primary/5 lg:flex lg:flex-col lg:justify-between lg:p-12">
      <div className="pointer-events-none absolute inset-0">
        <div className="animate-float absolute -left-16 top-10 h-72 w-72 rounded-full bg-primary/20 blur-3xl" />
        <div className="animate-float absolute bottom-10 right-0 h-72 w-72 rounded-full bg-secondary/20 blur-3xl" style={{ animationDelay: "3s" }} />
      </div>
      <Link to="/" className="relative"><Logo /></Link>

      <div className="relative">
        <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/70 px-4 py-1.5 text-sm font-medium text-primary">
          <Sparkles className="h-4 w-4" /> AI-Powered Agriculture
        </span>
        <h2 className="mt-6 max-w-md font-display text-4xl font-800 leading-tight tracking-tight">
          Grow smarter with <span className="text-primary">OptiCrop AI</span>
        </h2>
        <p className="mt-4 max-w-md text-muted-foreground">
          Turn soil and climate data into confident, sustainable crop decisions powered by machine learning.
        </p>
        <div className="mt-8 space-y-4">
          {[
            { icon: Brain, t: "98.6% model accuracy", d: "Ensemble ML predictions" },
            { icon: Leaf, t: "22+ supported crops", d: "Suitability scoring 0–100" },
            { icon: TrendingUp, t: "Data-driven insights", d: "Across 10k+ samples" },
          ].map((f) => (
            <div key={f.t} className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary">
                <f.icon className="h-5 w-5" />
              </span>
              <div>
                <p className="text-sm font-600">{f.t}</p>
                <p className="text-xs text-muted-foreground">{f.d}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <p className="relative text-sm text-muted-foreground">© 2026 OptiCrop AI</p>
    </div>
  );
}
