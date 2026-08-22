import { siteConfig } from "./site-config";
import type {
  ApiErrorBody,
  DiseaseRecord,
  HealthResponse,
  ModelInfoResponse,
  PredictionResponse,
} from "./types";

export class ApiError extends Error {
  status: number;
  errorCode: string;

  constructor(status: number, body: Partial<ApiErrorBody> | null) {
    super(body?.detail ?? "The server returned an unexpected error.");
    this.status = status;
    this.errorCode = body?.error ?? "unknown_error";
  }
}

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: Partial<ApiErrorBody> | null = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    throw new ApiError(response.status, body);
  }
  return response.json() as Promise<T>;
}

function apiUrl(path: string): string {
  return `${siteConfig.apiBaseUrl}${path}`;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(apiUrl("/health"), { cache: "no-store" });
  return parseJsonOrThrow<HealthResponse>(response);
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  const response = await fetch(apiUrl("/model-info"), { cache: "no-store" });
  return parseJsonOrThrow<ModelInfoResponse>(response);
}

/** Never throws -- used on pages that must render even if the backend/model is unavailable. */
export async function getModelInfoSafe(): Promise<ModelInfoResponse | null> {
  try {
    return await getModelInfo();
  } catch {
    return null;
  }
}

/** Never throws -- used on pages that must render even if the backend is unavailable. */
export async function getDiseasesSafe(): Promise<DiseaseRecord[]> {
  try {
    return await getDiseases();
  } catch {
    return [];
  }
}

export async function getDiseases(): Promise<DiseaseRecord[]> {
  const response = await fetch(apiUrl("/diseases"), { cache: "no-store" });
  return parseJsonOrThrow<DiseaseRecord[]>(response);
}

export async function getDisease(diseaseId: string): Promise<DiseaseRecord> {
  const response = await fetch(apiUrl(`/diseases/${encodeURIComponent(diseaseId)}`), {
    cache: "no-store",
  });
  return parseJsonOrThrow<DiseaseRecord>(response);
}

export interface PredictOptions {
  topK?: number;
  includeGradcam?: boolean;
}

export async function predict(
  file: File,
  { topK = 5, includeGradcam = true }: PredictOptions = {},
): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("top_k", String(topK));
  formData.append("include_gradcam", String(includeGradcam));

  const response = await fetch(apiUrl("/predict"), {
    method: "POST",
    body: formData,
  });
  return parseJsonOrThrow<PredictionResponse>(response);
}
