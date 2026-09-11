export type UserRole = 'FARMER' | 'EXTENSION_WORKER' | 'EXPERT' | 'ADMIN' | 'SUPER_ADMIN';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  state?: string;
  district?: string;
}

export interface GatekeeperResult {
  is_crop: boolean;
  confidence: number;
  message: string;
  suggestions?: string[];
}

export interface DiseasePrediction {
  disease: string | null;
  pathogen_type: 'Fungal' | 'Bacterial' | 'Viral' | 'Physiological' | 'Healthy' | string;
  confidence: number | null;
  description: string;
  inference_mode?: string;
  model_name?: string;
  note?: string;
  raw_label?: string | null;
  display_label?: string | null;
  model_provider?: string | null;
  model_architecture?: string | null;
}

export interface BoundingBox {
  x: number; // 0.0 to 1.0 normalized (legacy diagnose-embedded pests)
  y: number;
  width: number;
  height: number;
}

/** Pixel-space bbox from POST /pests/detect */
export interface PestPixelBBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface PestDetectionItem {
  name: string;
  scientific_name?: string;
  confidence: number;
  bbox: BoundingBox;
  severity: 'Low' | 'Moderate' | 'High' | 'Severe' | string;
  is_mock?: boolean;
  inference_mode?: string;
  note?: string;
}

export interface PestObjectDetectionItem {
  pest: string;
  raw_label: string;
  confidence: number;
  bbox: PestPixelBBox;
  class_id?: number | null;
}

export interface PestModelMeta {
  provider: string;
  model_id: string;
  architecture?: string | null;
  inference_mode: string;
  confidence_threshold: number;
  load_seconds?: number | null;
  inference_ms?: number | null;
}

export interface PestAdvisoryBrief {
  condition_summary: string;
  guidance_available: boolean;
  immediate_action?: string;
  pesticide_recommendation?: PesticideRecommendation | null;
  sources?: SourceReference[];
  disclaimer?: string;
}

export interface PestDetectResponse {
  id: string;
  status: 'pests_detected' | 'no_pest_detected' | 'error' | string;
  image_url: string;
  crop_hint?: string | null;
  crop?: string | null;
  detections: PestObjectDetectionItem[];
  count: number;
  image_width: number;
  image_height: number;
  severity: string;
  severity_label: string;
  model: PestModelMeta;
  advisory?: PestAdvisoryBrief | null;
  created_at: string;
  inference_meta?: InferenceMeta;
  /** Present on persisted history records */
  pest?: string | null;
  raw_label?: string | null;
  confidence?: number | null;
  bbox?: PestPixelBBox | null;
}

export interface WeatherMetrics {
  temperature: number;
  relative_humidity: number;
  precipitation: number;
  wind_speed: number;
  cloud_cover?: number;
  risk_level: 'Low' | 'Moderate' | 'High' | 'Critical' | string;
  risk_factor: string;
  is_cached?: boolean;
  is_unavailable?: boolean;
  source?: string;
}

export interface PesticideRecommendation {
  active_ingredient: string;
  chemical_name: string;
  exact_dose_per_liter: string;
  withholding_period_days: number;
  application_method: string;
  safety_warnings: string[];
  guidance_available?: boolean;
  unavailable_reason?: string;
}

export interface InferenceMeta {
  crop_inference_mode?: string;
  disease_inference_mode?: string;
  pest_inference_mode?: string;
  pest_mock_enabled?: boolean;
  rag_grounded?: boolean;
  guidance_available?: boolean;
  [key: string]: unknown;
}

export interface FertilizerAdjustment {
  n_ratio: string;
  p_ratio: string;
  k_ratio: string;
  micronutrients: string[];
  instructions: string;
}

export interface IPMStrategy {
  cultural: string[];
  biological: string[];
  mechanical: string[];
  chemical: string[];
}

export interface MonitoringPlan {
  day_1: string;
  day_3: string;
  day_7: string;
  day_14: string;
}

export interface SourceReference {
  title: string;
  authority: string;
  document_type: string;
  page_number?: number;
}

export interface AdvisoryReport {
  condition_summary: string;
  overall_risk: 'Healthy' | 'Low Risk' | 'Moderate Risk' | 'High Risk' | 'Critical' | string;
  risk_score: number; // 0 - 100
  risk_explanation: string;
  immediate_action: string;
  pesticide_recommendation: PesticideRecommendation;
  fertilizer_adjustments: FertilizerAdjustment;
  ipm: IPMStrategy;
  monitoring: MonitoringPlan;
  weather_impact_advisory: string;
  sources: SourceReference[];
  disclaimer: string;
}

export interface AnalysisResponse {
  id: string;
  status: 'completed' | 'rejected' | 'processing' | 'error' | 'model_unavailable';
  image_url: string;
  crop_detected: boolean;
  crop: string;
  crop_confidence: number;
  disease: DiseasePrediction;
  pests: PestDetectionItem[];
  weather?: WeatherMetrics | null;
  advisory: AdvisoryReport | null;
  location: {
    latitude: number;
    longitude: number;
    district?: string;
    state?: string;
  };
  validation_status: 'PENDING' | 'UNDER_REVIEW' | 'CONFIRMED' | 'CORRECTED' | 'REJECTED';
  created_at: string;
  inference_meta?: InferenceMeta;
}

export interface HotspotFeatureProperties {
  id: string;
  district: string;
  state: string;
  crop: string;
  disease: string;
  pest?: string;
  risk_level: string;
  case_count: number;
  farm_count: number;
  trend_pct: number;
  intensity: number;
}

export interface HotspotFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  properties: HotspotFeatureProperties;
}

export interface HotspotGeoJSON {
  type: 'FeatureCollection';
  features: HotspotFeature[];
}

export interface AdminAnalytics {
  total_farmers: number;
  total_farms: number;
  total_analyses: number;
  disease_cases: number;
  pest_cases: number;
  high_risk_areas: number;
  pending_expert_reviews: number;
  validation_accuracy_rate: number;
  disease_distribution: Array<{ name: string; count: number; category: string; color: string }>;
  pest_distribution: Array<{ name: string; count: number; color: string }>;
  regional_cases: Array<{ region: string; cases: number; risk: string }>;
  timeline_trends: Array<{ date: string; cases: number; resolved: number; critical: number }>;
}

export interface ExpertValidationCase {
  id: string;
  analysis_id: string;
  farmer_name: string;
  farmer_email: string;
  farmer_phone: string;
  farmer_notes: string;
  district: string;
  state: string;
  crop: string;
  ai_predicted_disease: string;
  ai_confidence: number;
  ai_risk_level: string;
  image_url: string;
  status: 'PENDING' | 'UNDER_REVIEW' | 'CONFIRMED' | 'CORRECTED' | 'REJECTED';
  created_at: string;
  reviewer_id?: string;
  reviewed_at?: string;
  confirmed_disease?: string;
  expert_notes?: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  source: string;
  authority: string;
  crop: string;
  sector?: string;
  topic: string;
  language: string;
  uploaded_date: string;
  indexed_chunks: number;
  status: 'INDEXED' | 'PROCESSING' | 'FAILED';
  file_type: string;
}

export interface RegisteredModel {
  id: string;
  task: string;
  model_name: string;
  provider: string;
  version: string;
  threshold: number;
  status: string;
  supported_classes: string[];
}
