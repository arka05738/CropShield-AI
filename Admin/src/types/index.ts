export type UserRole = 'FARMER' | 'EXTENSION_WORKER' | 'EXPERT' | 'ADMIN' | 'SUPER_ADMIN';

export const ADMIN_ALLOWED_ROLES: UserRole[] = [
  'ADMIN',
  'SUPER_ADMIN',
  'EXPERT',
  'EXTENSION_WORKER',
];

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  state?: string;
  district?: string;
  created_at?: string;
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
  raw_label?: string | null;
  display_label?: string | null;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PestDetectionItem {
  name: string;
  scientific_name?: string;
  confidence: number;
  bbox: BoundingBox;
  severity: 'Low' | 'Moderate' | 'High' | 'Severe' | string;
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
}

export interface PesticideRecommendation {
  active_ingredient: string;
  chemical_name: string;
  exact_dose_per_liter: string;
  withholding_period_days: number;
  application_method: string;
  safety_warnings: string[];
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
  risk_score: number;
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
  status: 'completed' | 'rejected' | 'processing' | 'error' | 'model_unavailable' | string;
  image_url: string;
  crop_detected: boolean;
  crop: string;
  crop_confidence: number;
  disease: DiseasePrediction | null;
  pests: PestDetectionItem[];
  weather?: WeatherMetrics | null;
  advisory?: AdvisoryReport | null;
  location?: {
    latitude?: number;
    longitude?: number;
    district?: string;
    state?: string;
  };
  validation_status?: 'PENDING' | 'UNDER_REVIEW' | 'CONFIRMED' | 'CORRECTED' | 'REJECTED' | string;
  created_at: string;
  user_id?: string;
  inference_meta?: Record<string, unknown>;
  model?: Record<string, unknown> | string;
}

/** Pest OD case row from GET /admin/pests */
export interface PestAdminCase {
  id: string;
  record_type?: string;
  crop?: string | null;
  pest?: string | null;
  raw_label?: string | null;
  confidence?: number | null;
  count?: number | null;
  severity?: string | null;
  severity_label?: string | null;
  model?: string | null;
  timestamp?: string | null;
  image_url?: string;
  user_id?: string;
  detections?: Array<{
    pest?: string;
    raw_label?: string;
    confidence?: number;
    bbox?: { x1: number; y1: number; x2: number; y2: number };
  }>;
  image_width?: number;
  image_height?: number;
  advisory?: {
    guidance_available?: boolean;
    condition_summary?: string;
  };
  model_id?: string;
  model_meta?: Record<string, unknown> | null;
  created_at?: string;
  status?: string;
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
    coordinates: [number, number];
  };
  properties: HotspotFeatureProperties;
}

export interface HotspotGeoJSON {
  type: 'FeatureCollection';
  features: HotspotFeature[];
  data_source?: string;
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
  data_source?: string;
  is_demo_inflated?: boolean;
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
  supported_classes?: string[];
  supported_classes_count?: number;
  inference_mode?: string;
  model_id?: string;
  endpoint?: string;
  note?: string;
  crop_routing?: Record<string, unknown>;
  model_ids?: Record<string, string>;
  default_primary?: string;
  backup_not_integrated?: string;
  specialist_not_integrated?: string;
  [key: string]: unknown;
}

export interface FarmRecord {
  id?: string;
  name?: string;
  farmer_id?: string;
  farmer_name?: string;
  crop?: string;
  area_ha?: number;
  district?: string;
  state?: string;
  [key: string]: unknown;
}

export interface NameCountItem {
  name: string;
  count: number;
}

export interface PaginatedList<T> {
  items: T[];
  count: number;
  data_source?: string;
  note?: string;
  mock_pest_mode?: boolean;
  cases?: PestAdminCase[];
  pest_od_cases?: number;
  pest_model_id?: string | null;
  record_type?: string;
}
