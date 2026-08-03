import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { PredictionInput } from "@/lib/mock-data";

type FieldKey = keyof PredictionInput;

const fields: { key: FieldKey; label: string; unit: string; min: number; max: number; step: number }[] = [
  { key: "n", label: "Nitrogen (N)", unit: "mg/kg", min: 0, max: 200, step: 1 },
  { key: "p", label: "Phosphorous (P)", unit: "mg/kg", min: 0, max: 200, step: 1 },
  { key: "k", label: "Potassium (K)", unit: "mg/kg", min: 0, max: 200, step: 1 },
  { key: "temperature", label: "Temperature", unit: "°C", min: 0, max: 50, step: 0.5 },
  { key: "humidity", label: "Humidity", unit: "%", min: 0, max: 100, step: 1 },
  { key: "ph", label: "pH Level", unit: "pH", min: 0, max: 14, step: 0.1 },
  { key: "rainfall", label: "Rainfall", unit: "mm", min: 0, max: 400, step: 1 },
];

export function EnvForm({
  value,
  onChange,
}: {
  value: PredictionInput;
  onChange: (v: PredictionInput) => void;
}) {
  const set = (key: FieldKey, v: number) => onChange({ ...value, [key]: v });

  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {fields.map((f) => (
        <div key={f.key} className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-sm">{f.label}</Label>
            <div className="flex items-center gap-1">
              <Input
                type="number"
                value={value[f.key]}
                min={f.min}
                max={f.max}
                step={f.step}
                onChange={(e) => set(f.key, Number(e.target.value))}
                className="h-8 w-20 rounded-xl text-right"
              />
              <span className="w-10 text-xs text-muted-foreground">{f.unit}</span>
            </div>
          </div>
          <Slider
            value={[value[f.key]]}
            min={f.min}
            max={f.max}
            step={f.step}
            onValueChange={([v]) => set(f.key, v)}
          />
        </div>
      ))}
    </div>
  );
}
