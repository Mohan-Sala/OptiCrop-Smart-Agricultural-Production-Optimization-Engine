import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/opticrop/AppShell";

export const Route = createFileRoute("/app")({
  component: AppShell,
});
