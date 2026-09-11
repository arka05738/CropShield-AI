import type { AnalysisResponse, PestAdminCase, User } from '../types';

export type CaseKind = 'disease' | 'pest';

export interface UnifiedCaseRow {
  id: string;
  kind: CaseKind;
  farmerLabel: string;
  farmerId?: string;
  crop: string;
  finding: string;
  confidence: number | null;
  severity: string;
  date: string;
  model: string;
  pestCount?: number | null;
  disease?: string | null;
  rawDisease?: AnalysisResponse;
  rawPest?: PestAdminCase;
}

export function farmerLabel(users: User[], userId?: string | null): string {
  if (!userId) return 'Unknown farmer';
  const u = users.find((x) => x.id === userId);
  if (!u) return userId.slice(0, 12);
  return u.full_name || u.email || userId.slice(0, 12);
}

export function diseaseToRow(c: AnalysisResponse, users: User[]): UnifiedCaseRow {
  const model =
    (typeof c.model === 'string' ? c.model : null) ||
    (c.disease as { model_name?: string } | null)?.model_name ||
    (c.inference_meta?.model_id as string | undefined) ||
    'Not available';
  const risk = c.advisory?.overall_risk || 'Not available';
  return {
    id: c.id,
    kind: 'disease',
    farmerLabel: farmerLabel(users, c.user_id),
    farmerId: c.user_id,
    crop: c.crop || '—',
    finding: c.disease?.disease || '—',
    confidence: c.disease?.confidence ?? null,
    severity: risk,
    date: c.created_at || '',
    model: String(model),
    disease: c.disease?.disease ?? null,
    rawDisease: c,
  };
}

export function pestToRow(c: PestAdminCase, users: User[]): UnifiedCaseRow {
  return {
    id: c.id,
    kind: 'pest',
    farmerLabel: farmerLabel(users, c.user_id),
    farmerId: c.user_id,
    crop: c.crop || '—',
    finding: c.pest || c.raw_label || '—',
    confidence: c.confidence ?? null,
    severity: c.severity || 'Not available',
    date: c.timestamp || c.created_at || '',
    model: c.model || c.model_id || 'Not available',
    pestCount: c.count ?? null,
    rawPest: c,
  };
}

export function formatConfidence(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return 'Not available';
  const pct = value <= 1 ? value * 100 : value;
  return `${pct.toFixed(1)}%`;
}

export function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

export function isHighRiskSeverity(severity: string): boolean {
  const s = severity.toLowerCase();
  return s.includes('high') || s.includes('critical') || s.includes('severe');
}
