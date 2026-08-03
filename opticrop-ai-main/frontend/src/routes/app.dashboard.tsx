import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Sprout, Leaf, BarChart3, Target, Boxes, Database, Zap, ArrowRight, Activity,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MetricCard } from "@/components/opticrop/MetricCard";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { recentPredictions } from "@/lib/mock-data";
import { useAuth } from "../lib/auth";

export const Route = createFileRoute("/app/dashboard")({
  component: Dashboard,
});

const kpiCards = [
  { icon: Target, label: "Model Accuracy", value: "98.6%", sub: "Random Forest", trend: "+1.2%" },
  { icon: Boxes, label: "Supported Crops", value: "22", sub: "crop classes", trend: "stable" },
  { icon: Database, label: "Dataset Size", value: "10,245", sub: "labeled samples", trend: "+430" },
  { icon: Zap, label: "Prediction Speed", value: "42ms", sub: "avg latency", trend: "-6ms" },
];

const quickActions = [
  { to: "/app/recommendation", icon: Sprout, title: "Crop Recommendation", desc: "Predict the best crop for your field." },
  { to: "/app/suitability", icon: Leaf, title: "Suitability Checker", desc: "Check how well a crop fits conditions." },
  { to: "/app/analytics", icon: BarChart3, title: "Analytics", desc: "Explore dataset patterns & insights." },
] as const;

function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Hero banner */}
      <Card className="animate-fade-up glass relative overflow-hidden rounded-[20px] border-border/60 p-7 shadow-[var(--shadow-soft)] md:p-9">
        <div className="pointer-events-none absolute -right-10 -top-10 h-56 w-56 rounded-full bg-primary/15 blur-3xl" />
        <div className="relative">
          <Badge variant="secondary" className="rounded-full">
            <Activity className="mr-1 h-3.5 w-3.5" /> Systems running smoothly
          </Badge>
          <h1 className="mt-4 font-display text-3xl font-800 tracking-tight md:text-4xl">
            Welcome back, {user?.fullName || "John Doe"}! 🌱
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Here's what's happening with your farm today. Run a prediction or analyze your soil to get started.
          </p>
          
          <div className="mt-4 grid gap-2 sm:flex sm:gap-6 text-xs text-muted-foreground border-t border-border/40 pt-4 max-w-xl">
            <div><span className="font-600 text-foreground">Role:</span> {user?.role || "Farmer"}</div>
            {user?.location && <div><span className="font-600 text-foreground">Location:</span> {user.location}</div>}
            <div><span className="font-600 text-foreground">Registered:</span> {user?.registrationDate}</div>
            <div><span className="font-600 text-foreground">Last Login:</span> {user?.lastLogin}</div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild variant="hero"><Link to="/app/recommendation"><Sprout className="h-4 w-4" /> Predict Crop</Link></Button>
            <Button asChild variant="outline"><Link to="/app/suitability"><Leaf className="h-4 w-4" /> Analyze Soil</Link></Button>
          </div>
        </div>
      </Card>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map((k) => (
          <MetricCard key={k.label} {...k} />
        ))}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="mb-3 font-display text-lg font-600">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((a) => (
            <Link key={a.to} to={a.to}>
              <Card className="card-lift group flex h-full items-center gap-4 rounded-[20px] border-border/70 p-5 shadow-[var(--shadow-soft)]">
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary">
                  <a.icon className="h-6 w-6" />
                </span>
                <div className="flex-1">
                  <p className="font-display font-600">{a.title}</p>
                  <p className="text-sm text-muted-foreground">{a.desc}</p>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent predictions */}
      <Card className="overflow-hidden rounded-[20px] border-border/70 shadow-[var(--shadow-soft)]">
        <div className="flex items-center justify-between p-5">
          <h2 className="font-display text-lg font-600">Recent Predictions</h2>
          <Button asChild variant="ghost" size="sm"><Link to="/app/analytics">View all <ArrowRight className="h-4 w-4" /></Link></Button>
        </div>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-border/60">
                <TableHead>Timestamp</TableHead>
                <TableHead>Input Summary</TableHead>
                <TableHead>Predicted Crop</TableHead>
                <TableHead className="text-right">Confidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentPredictions.map((r, i) => (
                <TableRow key={i} className="border-border/60">
                  <TableCell className="whitespace-nowrap text-muted-foreground">{r.time}</TableCell>
                  <TableCell className="whitespace-nowrap font-mono text-xs">{r.input}</TableCell>
                  <TableCell><Badge variant="secondary" className="rounded-full">{r.crop}</Badge></TableCell>
                  <TableCell className="text-right font-600 text-primary">{r.conf}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
