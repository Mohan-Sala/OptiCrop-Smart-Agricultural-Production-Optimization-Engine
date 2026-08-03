import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function MetricCard({
  icon: Icon,
  label,
  value,
  sub,
  trend,
  className,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  sub?: string;
  trend?: string;
  className?: string;
}) {
  return (
    <Card className={cn("card-lift rounded-[20px] border-border/70 p-5 shadow-[var(--shadow-soft)]", className)}>
      <div className="flex items-start justify-between">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-primary/10 text-primary">
          <Icon className="h-5 w-5" />
        </div>
        {trend && (
          <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
            {trend}
          </span>
        )}
      </div>
      <p className="mt-4 font-display text-3xl font-700 tracking-tight">{value}</p>
      <p className="mt-1 text-sm font-medium text-foreground">{label}</p>
      {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
    </Card>
  );
}
