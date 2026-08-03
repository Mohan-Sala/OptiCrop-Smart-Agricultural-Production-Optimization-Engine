// Static mock data powering the OptiCrop AI UI (frontend-only demo).

export const kpis = [
  { label: "Model Accuracy", value: "98.6%", sub: "Random Forest", trend: "+1.2%" },
  { label: "Supported Crops", value: "22", sub: "crop classes", trend: "stable" },
  { label: "Dataset Size", value: "10,245", sub: "labeled samples", trend: "+430" },
  { label: "Prediction Speed", value: "42ms", sub: "avg latency", trend: "-6ms" },
];

export const recentPredictions = [
  { time: "May 14, 2024 · 10:32", input: "N:90 P:42 K:43 · 25°C · 82% · pH 6.5", crop: "Rice", conf: 96.4 },
  { time: "May 14, 2024 · 09:58", input: "N:60 P:55 K:44 · 21°C · 60% · pH 6.7", crop: "Wheat", conf: 92.1 },
  { time: "May 13, 2024 · 18:14", input: "N:74 P:35 K:40 · 27°C · 65% · pH 6.9", crop: "Maize", conf: 92.7 },
  { time: "May 13, 2024 · 15:02", input: "N:118 P:24 K:30 · 24°C · 71% · pH 6.2", crop: "Cotton", conf: 95.0 },
  { time: "May 12, 2024 · 11:47", input: "N:80 P:60 K:75 · 26°C · 74% · pH 6.4", crop: "Sugarcane", conf: 94.2 },
];

export const cropDistribution = [
  { name: "Rice", value: 24, fill: "var(--color-chart-1)" },
  { name: "Wheat", value: 18, fill: "var(--color-chart-2)" },
  { name: "Maize", value: 16, fill: "var(--color-chart-3)" },
  { name: "Cotton", value: 14, fill: "var(--color-chart-4)" },
  { name: "Others", value: 28, fill: "var(--color-chart-5)" },
];

export const rainfallScatter = Array.from({ length: 40 }, (_, i) => ({
  rainfall: 40 + Math.round(Math.random() * 260),
  yield: 30 + Math.round(Math.random() * 60 + i * 0.3),
}));

export const tempDistribution = [
  { t: "10°", v: 4 }, { t: "15°", v: 12 }, { t: "20°", v: 28 },
  { t: "25°", v: 42 }, { t: "30°", v: 30 }, { t: "35°", v: 14 }, { t: "40°", v: 5 },
];

export const phImpact = [
  { ph: "4.5", score: 32 }, { ph: "5.5", score: 55 }, { ph: "6.0", score: 78 },
  { ph: "6.5", score: 94 }, { ph: "7.0", score: 88 }, { ph: "7.5", score: 66 }, { ph: "8.0", score: 40 },
];

export const modelComparison = [
  { model: "Random Forest", accuracy: 98.6, precision: 0.98, recall: 0.98, f1: 0.98, best: true },
  { model: "KNN", accuracy: 95.2, precision: 0.95, recall: 0.95, f1: 0.95, best: false },
  { model: "Decision Tree", accuracy: 93.1, precision: 0.93, recall: 0.9, f1: 0.9, best: false },
  { model: "Logistic Regression", accuracy: 91.4, precision: 0.91, recall: 0.91, f1: 0.9, best: false },
];

export const featureImportance = [
  { feature: "Rainfall", value: 0.28 },
  { feature: "Humidity", value: 0.22 },
  { feature: "Temperature", value: 0.16 },
  { feature: "Nitrogen", value: 0.13 },
  { feature: "Potassium", value: 0.11 },
  { feature: "Phosphorus", value: 0.06 },
  { feature: "pH", value: 0.04 },
];

export const crops = [
  "Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Coffee",
  "Banana", "Mango", "Coconut", "Chickpea", "Lentil", "Soybean",
];

export type PredictionInput = {
  n: number; p: number; k: number;
  temperature: number; humidity: number; ph: number; rainfall: number;
};

export const defaultInput: PredictionInput = {
  n: 90, p: 42, k: 43, temperature: 25, humidity: 82, ph: 6.5, rainfall: 200,
};
