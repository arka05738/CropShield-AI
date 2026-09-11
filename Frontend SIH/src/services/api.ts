import { 
  AnalysisResponse, HotspotGeoJSON, AdminAnalytics, 
  ExpertValidationCase, KnowledgeDocument, RegisteredModel, 
  WeatherMetrics, User, PestDetectResponse, CropIdentifyResponse
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('cropshield_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function readError(res: Response, fallback: string): Promise<string> {
  const err = await res.json().catch(() => ({} as { detail?: unknown }));
  const detail = err.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === 'object' && d && 'msg' in d ? String((d as { msg: string }).msg) : String(d))).join('; ');
  }
  return fallback;
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      throw new Error(await readError(res, 'Login failed'));
    }
    const data = await res.json();
    localStorage.setItem('cropshield_token', data.access_token);
    localStorage.setItem('cropshield_user', JSON.stringify(data.user));
    return data;
  },

  async register(payload: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    state?: string;
    district?: string;
    role?: string;
  }): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, role: payload.role || 'FARMER' })
    });
    if (!res.ok) {
      throw new Error(await readError(res, 'Registration failed'));
    }
    const data = await res.json();
    localStorage.setItem('cropshield_token', data.access_token);
    localStorage.setItem('cropshield_user', JSON.stringify(data.user));
    return data;
  },

  async getProfile(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error('Failed to fetch profile');
    }
    return res.json();
  },

  logout() {
    localStorage.removeItem('cropshield_token');
    localStorage.removeItem('cropshield_user');
  },

  // Diagnosis / Analysis Pipeline
  async identifyCrop(file: File): Promise<CropIdentifyResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/crop/identify`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });
    if (!res.ok) {
      throw new Error(await readError(res, 'Crop auto-identification failed'));
    }
    return res.json();
  },

  async runDiagnosis(formData: FormData): Promise<AnalysisResponse | { status: 'rejected'; message: string; suggestions?: string[] }> {
    const res = await fetch(`${API_BASE}/diagnose`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });
    if (!res.ok) {
      throw new Error(await readError(res, 'Diagnostic scan failed'));
    }
    return res.json();
  },

  async detectPests(formData: FormData): Promise<PestDetectResponse> {
    const res = await fetch(`${API_BASE}/pests/detect`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });
    if (!res.ok) {
      throw new Error(await readError(res, 'Pest detection failed'));
    }
    return res.json();
  },

  async getPestHistory(): Promise<PestDetectResponse[]> {
    const res = await fetch(`${API_BASE}/pests/history`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) return [];
    const data = await res.json();
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.items)) return data.items;
    return [];
  },

  async getPestById(id: string): Promise<PestDetectResponse> {
    const res = await fetch(`${API_BASE}/pests/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(await readError(res, 'Pest report not found'));
    return res.json();
  },

  async getHistory(crop?: string): Promise<AnalysisResponse[]> {
    const params = new URLSearchParams();
    if (crop && crop !== 'all') params.append('crop', crop);
    const res = await fetch(`${API_BASE}/analysis/history?${params.toString()}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getAnalysisById(id: string): Promise<AnalysisResponse> {
    const res = await fetch(`${API_BASE}/analysis/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Analysis report not found');
    return res.json();
  },

  // Expert Validation (farmer-initiated)
  async requestValidation(analysisId: string, farmerNotes?: string): Promise<{ validation_id: string }> {
    const res = await fetch(`${API_BASE}/validation/request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ analysis_id: analysisId, farmer_notes: farmerNotes })
    });
    if (!res.ok) throw new Error('Failed to request expert validation');
    return res.json();
  },

  // AI Assistant Chat
  async chatAssistant(message: string, cropContext?: string, language: string = 'en'): Promise<{ reply: string }> {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ message, crop_context: cropContext, language })
    });
    if (!res.ok) throw new Error('Copilot response error');
    return res.json();
  },

  // Weather
  async getWeather(latitude: number, longitude: number): Promise<WeatherMetrics> {
    const res = await fetch(
      `${API_BASE}/weather/current?latitude=${latitude}&longitude=${longitude}`,
      { headers: getAuthHeaders() }
    );
    if (!res.ok) throw new Error('Weather fetch failed');
    return res.json();
  },

  // Kept unused — admin portal owns these surfaces
  async getHotspots(filters?: { crop?: string; disease?: string; state?: string; min_risk?: string }): Promise<HotspotGeoJSON> {
    const params = new URLSearchParams();
    if (filters?.crop) params.append('crop', filters.crop);
    if (filters?.disease) params.append('disease', filters.disease);
    if (filters?.state) params.append('state', filters.state);
    if (filters?.min_risk) params.append('min_risk', filters.min_risk);
    const res = await fetch(`${API_BASE}/admin/hotspots?${params.toString()}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch geospatial hotspots');
    return res.json();
  },

  async getAdminAnalytics(): Promise<AdminAnalytics> {
    const res = await fetch(`${API_BASE}/admin/analytics`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to load admin analytics');
    return res.json();
  },

  async getRegisteredModels(): Promise<RegisteredModel[]> {
    const res = await fetch(`${API_BASE}/admin/models`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return res.json();
  },

  async updateModelThreshold(modelId: string, threshold: number): Promise<boolean> {
    const res = await fetch(`${API_BASE}/admin/models/${modelId}/threshold?threshold=${threshold}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.ok;
  },

  async getAdminCases(): Promise<AnalysisResponse[]> {
    const res = await fetch(`${API_BASE}/admin/cases`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getValidationQueue(status?: string): Promise<ExpertValidationCase[]> {
    const res = await fetch(`${API_BASE}/validation/queue?status=${status || 'ALL'}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return res.json();
  },

  async reviewValidationCase(
    id: string,
    review: { status: string; confirmed_disease?: string; confirmed_pest?: string; expert_notes: string }
  ): Promise<boolean> {
    const res = await fetch(`${API_BASE}/validation/${id}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(review)
    });
    return res.ok;
  },

  async getKnowledgeDocs(): Promise<KnowledgeDocument[]> {
    const res = await fetch(`${API_BASE}/knowledge`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getKnowledgeDocDetails(id: string): Promise<{ document: KnowledgeDocument; pop_record?: unknown }> {
    const res = await fetch(`${API_BASE}/knowledge/${id}/details`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to load document details');
    return res.json();
  },

  async uploadKnowledgeDoc(formData: FormData): Promise<KnowledgeDocument> {
    const res = await fetch(`${API_BASE}/knowledge/upload`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload document to ChromaDB');
    const data = await res.json();
    return data.document;
  },

  async deleteKnowledgeDoc(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/knowledge/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return res.ok;
  },

  async reindexKnowledge(): Promise<boolean> {
    const res = await fetch(`${API_BASE}/knowledge/reindex`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.ok;
  }
};
