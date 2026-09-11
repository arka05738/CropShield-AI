import type {
  AnalysisResponse,
  AdminAnalytics,
  ExpertValidationCase,
  FarmRecord,
  HotspotGeoJSON,
  KnowledgeDocument,
  NameCountItem,
  PaginatedList,
  RegisteredModel,
  User,
} from '../types';
import {
  clearAuthSession,
  getApiBase,
  getStoredToken,
  isAdminRole,
  setAuthSession,
} from '../lib/auth';

const API_BASE = () => getApiBase();

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseError(res: Response, fallback: string): Promise<never> {
  const err = await res.json().catch(() => ({} as { detail?: unknown }));
  const detail = err.detail;
  if (typeof detail === 'string') throw new Error(detail);
  if (Array.isArray(detail)) {
    throw new Error(
      detail
        .map((d) => (typeof d === 'object' && d && 'msg' in d ? String((d as { msg: string }).msg) : String(d)))
        .join('; ') || fallback
    );
  }
  throw new Error(fallback);
}

export const api = {
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE()}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) await parseError(res, 'Login failed');
    const data = await res.json();
    if (!isAdminRole(data.user?.role)) {
      clearAuthSession();
      throw new Error('Farmer accounts cannot access the Admin console. Use an ADMIN, SUPER_ADMIN, EXPERT, or EXTENSION_WORKER account.');
    }
    setAuthSession(data.access_token, data.user);
    return data;
  },

  logout(): void {
    clearAuthSession();
  },

  async getProfile(): Promise<User> {
    const res = await fetch(`${API_BASE()}/auth/me`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async getHotspots(filters?: {
    crop?: string;
    disease?: string;
    state?: string;
    min_risk?: string;
  }): Promise<HotspotGeoJSON> {
    const params = new URLSearchParams();
    if (filters?.crop && filters.crop !== 'all') params.append('crop', filters.crop);
    if (filters?.disease && filters.disease !== 'all') params.append('disease', filters.disease);
    if (filters?.state && filters.state !== 'all') params.append('state', filters.state);
    if (filters?.min_risk && filters.min_risk !== 'all') params.append('min_risk', filters.min_risk);

    const res = await fetch(`${API_BASE()}/admin/hotspots?${params.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch geospatial hotspots');
    return res.json();
  },

  async getAdminAnalytics(): Promise<AdminAnalytics> {
    const res = await fetch(`${API_BASE()}/admin/analytics`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load admin analytics');
    return res.json();
  },

  async getRegisteredModels(): Promise<PaginatedList<RegisteredModel>> {
    const res = await fetch(`${API_BASE()}/admin/models`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load model registry');
    const data = await res.json();
    if (Array.isArray(data)) {
      return { items: data, count: data.length };
    }
    return {
      items: data.models || [],
      count: data.count ?? (data.models || []).length,
      note: data.note,
    };
  },

  async updateModelThreshold(modelId: string, threshold: number): Promise<boolean> {
    const res = await fetch(
      `${API_BASE()}/admin/models/${modelId}/threshold?threshold=${threshold}`,
      { method: 'POST', headers: getAuthHeaders() }
    );
    return res.ok;
  },

  async getAdminCases(crop?: string): Promise<PaginatedList<AnalysisResponse>> {
    const params = new URLSearchParams();
    if (crop && crop !== 'all') params.append('crop', crop);
    const res = await fetch(`${API_BASE()}/admin/cases?${params.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load analyses');
    const data = await res.json();
    if (Array.isArray(data)) {
      return { items: data, count: data.length };
    }
    return {
      items: data.cases || [],
      count: data.count ?? (data.cases || []).length,
      data_source: data.data_source,
    };
  },

  async getUsers(): Promise<PaginatedList<User>> {
    const res = await fetch(`${API_BASE()}/admin/users`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load users');
    const data = await res.json();
    return {
      items: data.users || [],
      count: data.count ?? (data.users || []).length,
      data_source: data.data_source,
    };
  },

  async getFarms(): Promise<PaginatedList<FarmRecord>> {
    const res = await fetch(`${API_BASE()}/admin/farms`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load farms');
    const data = await res.json();
    return {
      items: data.farms || [],
      count: data.count ?? (data.farms || []).length,
      data_source: data.data_source,
    };
  },

  async getDiseases(): Promise<PaginatedList<NameCountItem>> {
    const res = await fetch(`${API_BASE()}/admin/diseases`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load diseases');
    const data = await res.json();
    return {
      items: data.diseases || [],
      count: (data.diseases || []).length,
      data_source: data.data_source,
    };
  },

  async getPests(): Promise<PaginatedList<NameCountItem>> {
    const res = await fetch(`${API_BASE()}/admin/pests`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load pests');
    const data = await res.json();
    return {
      items: data.pests || [],
      count: (data.pests || []).length,
      data_source: data.data_source,
      note: data.note,
      mock_pest_mode: data.mock_pest_mode,
      cases: data.cases || [],
      pest_od_cases: data.pest_od_cases,
      pest_model_id: data.pest_model_id,
      record_type: data.record_type,
    };
  },

  async getValidationQueue(status?: string): Promise<ExpertValidationCase[]> {
    const res = await fetch(`${API_BASE()}/validation/queue?status=${status || 'ALL'}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load validation queue');
    return res.json();
  },

  async reviewValidationCase(
    id: string,
    review: {
      status: string;
      confirmed_disease?: string;
      confirmed_pest?: string;
      expert_notes: string;
    }
  ): Promise<boolean> {
    const res = await fetch(`${API_BASE()}/validation/${id}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(review),
    });
    return res.ok;
  },

  async getKnowledgeDocs(): Promise<KnowledgeDocument[]> {
    const res = await fetch(`${API_BASE()}/knowledge`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to load knowledge documents');
    return res.json();
  },

  async getKnowledgeDocDetails(id: string): Promise<{ document: KnowledgeDocument; pop_record?: unknown }> {
    const res = await fetch(`${API_BASE()}/knowledge/${id}/details`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load document details');
    return res.json();
  },

  async uploadKnowledgeDoc(formData: FormData): Promise<KnowledgeDocument> {
    const res = await fetch(`${API_BASE()}/knowledge/upload`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    const data = await res.json();
    return data.document;
  },

  async deleteKnowledgeDoc(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE()}/knowledge/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return res.ok;
  },

  async reindexKnowledge(): Promise<boolean> {
    const res = await fetch(`${API_BASE()}/knowledge/reindex`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return res.ok;
  },
};
