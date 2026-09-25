// Agronomic form types, initial form values, and supported crop definitions.

export type PredictionInput = {
  n: number;
  p: number;
  k: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
};

export const defaultInput: PredictionInput = {
  n: 90,
  p: 42,
  k: 43,
  temperature: 25,
  humidity: 82,
  ph: 6.5,
  rainfall: 200,
};

export const crops = [
  "Rice",
  "Wheat",
  "Maize",
  "Cotton",
  "Sugarcane",
  "Coffee",
  "Banana",
  "Mango",
  "Coconut",
  "Chickpea",
  "Lentil",
  "Soybean",
] as const;

export const IDEAL_CROP_CONDITIONS: Record<string, PredictionInput> = {
  Rice: { n: 90.0, p: 44.0, k: 38.0, temperature: 24.5, humidity: 84.5, ph: 6.1, rainfall: 216.6 },
  Wheat: { n: 25.4, p: 61.0, k: 28.1, temperature: 19.2, humidity: 61.3, ph: 6.7, rainfall: 72.1 },
  Maize: { n: 72.7, p: 45.3, k: 23.7, temperature: 26.0, humidity: 66.5, ph: 6.3, rainfall: 88.0 },
  Cotton: { n: 120.6, p: 47.9, k: 19.8, temperature: 25.4, humidity: 80.5, ph: 7.2, rainfall: 81.2 },
  Sugarcane: { n: 114.7, p: 25.8, k: 27.2, temperature: 28.7, humidity: 83.5, ph: 6.7, rainfall: 201.0 },
  Coffee: { n: 98.1, p: 26.6, k: 31.2, temperature: 25.1, humidity: 57.3, ph: 6.7, rainfall: 172.2 },
  Banana: { n: 112.3, p: 81.8, k: 52.2, temperature: 27.2, humidity: 80.8, ph: 6.2, rainfall: 104.4 },
  Mango: { n: 28.0, p: 27.0, k: 31.0, temperature: 31.5, humidity: 50.0, ph: 5.5, rainfall: 99.0 },
  Coconut: { n: 30.6, p: 18.6, k: 30.7, temperature: 27.2, humidity: 96.2, ph: 6.0, rainfall: 192.9 },
  Chickpea: { n: 33.4, p: 67.9, k: 79.8, temperature: 19.2, humidity: 19.0, ph: 7.8, rainfall: 81.9 },
  Lentil: { n: 28.0, p: 64.9, k: 22.4, temperature: 21.0, humidity: 66.6, ph: 7.1, rainfall: 54.4 },
  Soybean: { n: 34.6, p: 73.0, k: 42.2, temperature: 23.5, humidity: 69.6, ph: 6.6, rainfall: 80.4 },
};
