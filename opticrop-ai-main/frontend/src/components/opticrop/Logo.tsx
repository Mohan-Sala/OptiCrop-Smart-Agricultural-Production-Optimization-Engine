import { Sprout } from "lucide-react";
import { cn } from "@/lib/utils";

export function Logo({ className, textClassName }: { className?: string; textClassName?: string }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-[var(--shadow-soft)]">
        <Sprout className="h-5 w-5" />
      </span>
      <span className={cn("font-display text-lg font-700 tracking-tight", textClassName)}>
        OptiCrop<span className="text-primary"> AI</span>
      </span>
    </span>
  );
}
