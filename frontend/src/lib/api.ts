// Centralized typed API client communicating with OptiCrop AI FastAPI backend and MongoDB Atlas.

const TOKEN_KEY = "opticrop_access_token";
const REFRESH_TOKEN_KEY = "opticrop_refresh_token";

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  avatar_url?: string | null;
  role: string;
  bio?: string | null;
  location?: string | null;
  occupation?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface PredictionRunRecord {
  id: string;
  project_id: string;
  model_id: string;
  model_version: number;
  status: string;
  prediction_count: number;
  execution_time: number;
  prediction_timestamp: string;
  predictions?: any[] | null;
  confidence_scores?: number[] | null;
  features?: Array<Record<string, any>> | null;
  error_message?: string | null;
}

export interface SinglePredictionResponse {
  api_version: string;
  generated_at: string;
  prediction_id: string;
  model_id: string;
  model_version: number;
  prediction_timestamp: string;
  execution_time_ms: number;
  predictions: any[];
  confidence_scores?: number[] | null;
  probabilities?: Array<Record<string, number>> | Record<string, number> | null;
  prediction_metadata?: Record<string, any>;
}

export interface ModelInsightsData {
  model: {
    id: string;
    model_name: string;
    algorithm: string;
    version: string;
    status: string;
    is_active: boolean;
    storage_path: string;
    checksum?: string | null;
    created_at?: string | null;
    activated_at?: string | null;
  };
  metrics: Array<{
    metric_name: string;
    metric_value: number;
    label?: string;
  }>;
  hyperparameters: Record<string, any>;
  feature_importances: Array<{
    feature: string;
    label: string;
    unit: string;
    importance: number;
    percentage: number;
  }>;
  classes: string[];
  crop_benchmarks?: Record<string, Record<string, number>>;
  dataset: {
    name: string;
    rows: number;
    columns: number;
    target_column: string;
  };
  total_inferences: number;
}

export interface DatasetRecord {
  id: string;
  project_id: string;
  name: string;
  original_filename: string;
  stored_filename: string;
  storage_path: string;
  status: string;
  dataset_stage: string;
  rows: number;
  columns: number;
  size: number;
  uploaded_at: string;
  description?: string | null;
}

export interface DatasetPreviewData {
  dataset_id: string;
  shape: [number, number];
  columns: string[];
  dtypes: Record<string, string>;
  missing_values: Record<string, number>;
  memory_usage_bytes: number;
  data: Array<Record<string, any>>;
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredTokens(accessToken: string, refreshToken?: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

export function clearStoredTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "";
const BASE_URL = `${API_BASE}/api/v1`;

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle unauthorized / expired tokens
  if (response.status === 401) {
    clearStoredTokens();
    if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
      window.dispatchEvent(new CustomEvent("opticrop:unauthorized"));
    }
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    let errorMsg = `Request failed with status ${response.status}`;
    if (data) {
      if (typeof data.message === "string" && data.message) {
        if (Array.isArray(data.errors) && data.errors.length > 0 && data.errors[0]?.message) {
          errorMsg = `${data.message} (${data.errors.map((e: any) => e.message).join(", ")})`;
        } else {
          errorMsg = data.message;
        }
      } else if (typeof data.detail === "string" && data.detail) {
        errorMsg = data.detail;
      } else if (Array.isArray(data.detail) && data.detail.length > 0) {
        errorMsg = data.detail.map((d: any) => d.msg || JSON.stringify(d)).join("; ");
      } else if (Array.isArray(data.errors) && data.errors.length > 0 && data.errors[0]?.message) {
        errorMsg = data.errors[0].message;
      }
    }
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  auth: {
    async register(payload: { email: string; password: string; full_name: string }): Promise<UserProfile> {
      return request<UserProfile>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    async login(payload: { email: string; password: string; device_name?: string }): Promise<TokenResponse> {
      const res = await request<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: payload.email,
          password: payload.password,
          device_name: payload.device_name || "Web Browser",
        }),
      });
      setStoredTokens(res.access_token, res.refresh_token);
      return res;
    },

    async logout(): Promise<void> {
      const refreshToken = typeof window !== "undefined" ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;
      if (refreshToken) {
        try {
          await request("/auth/logout", {
            method: "POST",
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
        } catch {
          // ignore logout errors
        }
      }
      clearStoredTokens();
    },
  },

  profile: {
    async get(): Promise<UserProfile> {
      return request<UserProfile>("/profile");
    },

    async update(payload: Partial<UserProfile>): Promise<UserProfile> {
      return request<UserProfile>("/profile", {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    },

    async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
      return request<{ message: string }>("/profile/change-password", {
        method: "POST",
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });
    },
  },

  predictions: {
    async history(projectId?: string, pageSize: number = 50): Promise<PredictionRunRecord[]> {
      const params = new URLSearchParams();
      if (projectId) params.append("project_id", projectId);
      params.append("page_size", String(pageSize));
      return request<PredictionRunRecord[]>(`/predictions/history?${params.toString()}`);
    },

    async export(format: "csv" | "json", projectId?: string): Promise<{ filename: string; content: string }> {
      const url = projectId
        ? `/predictions/export/${format}?project_id=${encodeURIComponent(projectId)}`
        : `/predictions/export/${format}`;
      return request<{ filename: string; content: string }>(url);
    },

    async predict(payload: {
      features: Record<string, any>;
      projectId?: string;
      modelId?: string;
    }): Promise<SinglePredictionResponse> {
      return request<SinglePredictionResponse>("/predictions/", {
        method: "POST",
        body: JSON.stringify({
          project_id: payload.projectId || "00000000-0000-0000-0000-000000000000",
          model_id: payload.modelId,
          features: payload.features,
        }),
      });
    },
  },

  models: {
    async getInsights(projectId?: string): Promise<ModelInsightsData> {
      const url = projectId
        ? `/training/insights?project_id=${encodeURIComponent(projectId)}`
        : "/training/insights";
      return request<ModelInsightsData>(url);
    },
    async list(projectId?: string): Promise<any[]> {
      const url = projectId
        ? `/training/models?project_id=${encodeURIComponent(projectId)}`
        : "/training/models";
      return request<any[]>(url);
    },
  },

  datasets: {
    async list(projectId?: string): Promise<{ items: DatasetRecord[]; total: number }> {
      const url = projectId
        ? `/datasets/?project_id=${encodeURIComponent(projectId)}`
        : "/datasets/";
      return request<{ items: DatasetRecord[]; total: number }>(url);
    },

    async upload(file: File, description?: string): Promise<DatasetRecord> {
      const formData = new FormData();
      formData.append("file", file);
      if (description) {
        formData.append("description", description);
      }
      return request<DatasetRecord>("/datasets/", {
        method: "POST",
        body: formData,
      });
    },

    async preview(datasetId: string): Promise<DatasetPreviewData> {
      return request<DatasetPreviewData>(`/datasets/${datasetId}/preview`);
    },

    async delete(datasetId: string): Promise<void> {
      await request(`/datasets/${datasetId}`, {
        method: "DELETE",
      });
    },

    getDownloadUrl(datasetId: string): string {
      return `${BASE_URL}/datasets/${datasetId}/download`;
    },
  },

  health: {
    async check(): Promise<{ status: string; services?: Record<string, any> }> {
      return request<{ status: string; services?: Record<string, any> }>("/health");
    },
  },
};
