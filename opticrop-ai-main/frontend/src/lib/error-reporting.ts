export function reportError(error: unknown, context: Record<string, unknown> = {}) {
  console.error("Captured Error:", error, "Context:", context);
}
