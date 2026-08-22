/**
 * Types mirror the FastAPI Pydantic response schemas in
 * backend/app/schemas/*.py exactly. Keep in sync with the backend contract --
 * the frontend must not invent fields the API doesn't return.
 */

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  version: string;
}

export interface PreprocessingInfo {
  image_size: [number, number];
  rescale: string;
  color_mode: string;
}

export interface ModelInfoResponse {
  model_name: string;
  model_version: string;
  framework: string;
  input_size: [number, number];
  num_classes: number;
  supported_classes: string[];
  target_layer: string;
  preprocessing: PreprocessingInfo;
  evaluation_accuracy: number | null;
  evaluation_macro_f1: number | null;
}

export interface TopKPrediction {
  rank: number;
  class_name: string;
  plant: string;
  disease: string;
  confidence: number;
}

export interface Visualization3D {
  target_layer: string;
  predicted_class_index: number;
  confidence: number;
  grid_size: [number, number];
  heightmap: number[][];
  texture_png_base64: string;
  colormap: string;
  is_biological_reconstruction: boolean;
  limitations: string;
}

export interface GradCAMResult {
  predicted_class_index: number;
  predicted_class: string | null;
  confidence: number;
  target_layer: string;
  heatmap_png_base64: string;
  overlay_png_base64: string;
  visualization_3d: Visualization3D;
  limitations: string;
}

export interface PredictionResponse {
  class_name: string;
  plant: string;
  disease: string;
  confidence: number;
  top_k: TopKPrediction[];
  gradcam: GradCAMResult | null;
}

export interface DiseaseRecord {
  id: string;
  plant: string;
  name: string;
  description?: string | null;
  symptoms?: string[] | null;
  causes?: string[] | null;
  prevention?: string[] | null;
  management?: string | string[] | null;
  severity?: string | null;
}

export interface ApiErrorBody {
  error: string;
  detail: string;
}
