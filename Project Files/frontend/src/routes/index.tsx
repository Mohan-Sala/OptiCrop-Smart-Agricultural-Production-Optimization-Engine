import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Sprout, CloudSun, Brain, LineChart, BarChart3, Leaf, ArrowRight,
  Database, Server, GitBranch, CheckCircle2, Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/opticrop/Logo";

export const Route = createFileRoute("/")({
  component: Landing,
});

const features = [
  { icon: Sprout, title: "Smart Crop Recommendation", desc: "ML models suggest the optimal crop from soil nutrients and climate signals." },
  { icon: CloudSun, title: "Soil & Climate Analysis", desc: "Interpret N-P-K, temperature, humidity, pH and rainfall in real time." },
  { icon: Leaf, title: "Crop Suitability Engine", desc: "Score how well a specific crop matches your field environment 0–100." },
  { icon: LineChart, title: "Data-driven Insights", desc: "Correlation, distribution and trend analytics across 10k+ samples." },
  { icon: Brain, title: "AI-powered Predictions", desc: "Ensemble learning delivers 98.6% accuracy with confidence scoring." },
  { icon: BarChart3, title: "Model Transparency", desc: "Feature importance and confusion matrices explain every decision." },
];

const steps = [
  { n: "01", title: "Input Soil Data", desc: "Enter nutrient levels and climate parameters through guided forms.", icon: Database },
  { n: "02", title: "AI Model Processing", desc: "Ensemble ML models analyze patterns against the trained dataset.", icon: Brain },
  { n: "03", title: "Crop Recommendation", desc: "Receive ranked crops with confidence scores and explanations.", icon: CheckCircle2 },
];

const tech = [
  { title: "Machine Learning Models", desc: "KNN · Random Forest · Decision Tree · Logistic Regression", icon: Brain },
  { title: "Flask Backend", desc: "Lightweight Python API serving predictions in ~42ms.", icon: Server },
  { title: "Data Pipeline", desc: "Cleaning → feature engineering → training → evaluation.", icon: GitBranch },
];

function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <header className="sticky top-0 z-50 glass border-b border-border/60">
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5">
          <Logo />
          <div className="hidden items-center gap-7 text-sm font-medium text-muted-foreground md:flex">
            <a href="#features" className="transition-colors hover:text-foreground">Features</a>
            <a href="#how" className="transition-colors hover:text-foreground">How It Works</a>
            <a href="#tech" className="transition-colors hover:text-foreground">Technology</a>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm"><Link to="/login">Login</Link></Button>
            <Button asChild size="sm"><Link to="/register">Register</Link></Button>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="animate-float absolute -left-20 top-10 h-72 w-72 rounded-full bg-primary/15 blur-3xl" />
          <div className="animate-float absolute right-0 top-40 h-80 w-80 rounded-full bg-secondary/15 blur-3xl" style={{ animationDelay: "2s" }} />
          <div className="animate-float absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-accent/20 blur-3xl" style={{ animationDelay: "4s" }} />
        </div>
        <div className="relative mx-auto max-w-7xl px-5 pb-24 pt-20 text-center">
          <span className="animate-fade-up inline-flex items-center gap-2 rounded-full border border-border/70 bg-card/70 px-4 py-1.5 text-sm font-medium text-primary shadow-[var(--shadow-soft)]">
            <Sparkles className="h-4 w-4" /> AI-Powered Agriculture
          </span>
          <h1 className="animate-fade-up mx-auto mt-6 max-w-4xl font-display text-5xl font-800 leading-[1.05] tracking-tight md:text-6xl" style={{ animationDelay: "0.05s" }}>
            AI-Powered Agricultural <span className="text-primary">Intelligence</span> System
          </h1>
          <p className="animate-fade-up mx-auto mt-6 max-w-2xl text-lg text-muted-foreground" style={{ animationDelay: "0.1s" }}>
            OptiCrop uses advanced machine learning to analyze soil and climate conditions,
            recommending the best crops for maximum yield and long-term sustainability.
          </p>
          <div className="animate-fade-up mt-9 flex flex-wrap items-center justify-center gap-3" style={{ animationDelay: "0.15s" }}>
            <Button asChild variant="hero" size="lg"><Link to="/register">Get Started <ArrowRight className="h-4 w-4" /></Link></Button>
            <Button asChild variant="outline" size="lg"><a href="#features">View Features</a></Button>
          </div>

          <div className="animate-fade-up mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-4 md:grid-cols-4" style={{ animationDelay: "0.2s" }}>
            {[
              { v: "22+", l: "Crops Supported" }, { v: "98.6%", l: "Model Accuracy" },
              { v: "10K+", l: "Predictions Made" }, { v: "7", l: "Parameters Used" },
            ].map((s) => (
              <Card key={s.l} className="rounded-[20px] border-border/70 p-5 shadow-[var(--shadow-soft)]">
                <p className="font-display text-3xl font-700 text-primary">{s.v}</p>
                <p className="mt-1 text-sm text-muted-foreground">{s.l}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-7xl px-5 py-24">
        <SectionHead eyebrow="Capabilities" title="Everything you need to optimize crops" desc="A complete intelligence toolkit built for modern precision agriculture." />
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <Card key={f.title} className="card-lift rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary">
                <f.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-5 font-display text-lg font-600">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="border-y border-border/60 bg-muted/40 py-24">
        <div className="mx-auto max-w-7xl px-5">
          <SectionHead eyebrow="Workflow" title="How OptiCrop works" desc="Three simple steps from raw field data to actionable crop guidance." />
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {steps.map((s) => (
              <Card key={s.n} className="relative rounded-[20px] border-border/70 p-7 shadow-[var(--shadow-soft)]">
                <span className="font-display text-5xl font-800 text-primary/15">{s.n}</span>
                <div className="mt-3 grid h-11 w-11 place-items-center rounded-xl bg-primary/10 text-primary">
                  <s.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 font-display text-lg font-600">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="tech" className="mx-auto max-w-7xl px-5 py-24">
        <SectionHead eyebrow="Technology" title="Built on a robust ML stack" desc="Production-grade models and pipeline engineered for reliable predictions." />
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {tech.map((t) => (
            <Card key={t.title} className="card-lift rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-secondary/10 text-secondary">
                <t.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-5 font-display text-lg font-600">{t.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{t.desc}</p>
            </Card>
          ))}
        </div>

        <Card className="mt-10 overflow-hidden rounded-[20px] border-border/70 shadow-[var(--shadow-soft)]">
          <div className="grid items-center gap-8 p-8 md:grid-cols-2 md:p-12">
            <div>
              <h3 className="font-display text-2xl font-700">Ready to grow smarter?</h3>
              <p className="mt-3 text-muted-foreground">Join OptiCrop and turn your field data into confident, sustainable crop decisions.</p>
              <Button asChild variant="hero" size="lg" className="mt-6"><Link to="/register">Get Started Free <ArrowRight className="h-4 w-4" /></Link></Button>
            </div>
            <div className="flex flex-wrap gap-3 md:justify-end">
              {["KNN", "Random Forest", "Decision Tree", "Logistic Regression"].map((m) => (
                <span key={m} className="rounded-full border border-border/70 bg-muted px-4 py-2 text-sm font-medium">{m}</span>
              ))}
            </div>
          </div>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/60 bg-muted/40">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-12 md:grid-cols-4">
          <div className="md:col-span-2">
            <Logo />
            <p className="mt-4 max-w-sm text-sm text-muted-foreground">
              OptiCrop AI is a smart agricultural production optimization engine using machine
              learning to recommend crops and analyze soil & climate conditions sustainably.
            </p>
          </div>
          <div>
            <p className="font-display text-sm font-600">Product</p>
            <div className="mt-3 space-y-2 text-sm text-muted-foreground">
              <a href="#features" className="block hover:text-foreground">Features</a>
              <a href="#how" className="block hover:text-foreground">How It Works</a>
              <a href="#tech" className="block hover:text-foreground">Technology</a>
            </div>
          </div>
          <div>
            <p className="font-display text-sm font-600">Account</p>
            <div className="mt-3 space-y-2 text-sm text-muted-foreground">
              <Link to="/login" className="block hover:text-foreground">Login</Link>
              <Link to="/register" className="block hover:text-foreground">Register</Link>
              <Link to="/app/dashboard" className="block hover:text-foreground">Dashboard</Link>
            </div>
          </div>
        </div>
        <div className="border-t border-border/60 py-5 text-center text-sm text-muted-foreground">
          © 2026 OptiCrop AI. Smart Agricultural Production Optimization Engine.
        </div>
      </footer>
    </div>
  );
}

function SectionHead({ eyebrow, title, desc }: { eyebrow: string; title: string; desc: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <span className="text-sm font-600 uppercase tracking-wider text-primary">{eyebrow}</span>
      <h2 className="mt-3 font-display text-3xl font-700 tracking-tight md:text-4xl">{title}</h2>
      <p className="mt-3 text-muted-foreground">{desc}</p>
    </div>
  );
}
