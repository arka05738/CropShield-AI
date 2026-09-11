import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../services/api';
import type { AnalysisResponse, PestAdminCase, User } from '../types';
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';
import { farmerLabel, formatConfidence, formatDate } from '../lib/cases';
import { handleImageError } from '../lib/imageFallback';

function assetUrl(path?: string | null): string | null {
  if (!path) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return path.startsWith('/') ? path : `/${path}`;
}

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="border-b border-stone-100 py-2.5 sm:grid sm:grid-cols-3 sm:gap-3">
      <dt className="text-xs font-semibold text-stone-500">{label}</dt>
      <dd className="mt-0.5 text-sm text-stone-900 sm:col-span-2 sm:mt-0">{value}</dd>
    </div>
  );
}

export function CaseDetailPage() {
  const { kind, id } = useParams<{ kind: string; id: string }>();
  const [disease, setDisease] = useState<AnalysisResponse | null>(null);
  const [pest, setPest] = useState<PestAdminCase | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!kind || !id) return;
    setLoading(true);
    setError(null);
    try {
      const usersRes = await api.getUsers();
      setUsers(usersRes.items);
      if (kind === 'disease') {
        const res = await api.getAdminCases();
        const found = res.items.find((c) => c.id === id) || null;
        setDisease(found);
        setPest(null);
        if (!found) setError('Disease case not found');
      } else if (kind === 'pest') {
        const res = await api.getPests();
        const found = (res.cases || []).find((c) => c.id === id) || null;
        setPest(found);
        setDisease(null);
        if (!found) setError('Pest case not found');
      } else {
        setError('Unknown case type');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  }, [kind, id]);

  useEffect(() => {
    void load();
  }, [load]);

  const pestBoxes = useMemo(() => {
    if (!pest?.detections?.length || !pest.image_width || !pest.image_height) return [];
    return pest.detections
      .map((d) => {
        const b = d.bbox;
        if (!b) return null;
        const w = pest.image_width || 1;
        const h = pest.image_height || 1;
        return {
          left: `${(b.x1 / w) * 100}%`,
          top: `${(b.y1 / h) * 100}%`,
          width: `${((b.x2 - b.x1) / w) * 100}%`,
          height: `${((b.y2 - b.y1) / h) * 100}%`,
          label: d.pest || d.raw_label || 'pest',
          conf: d.confidence,
        };
      })
      .filter(Boolean) as Array<{
      left: string;
      top: string;
      width: string;
      height: string;
      label: string;
      conf?: number;
    }>;
  }, [pest]);

  if (loading) return <LoadingState label="Loading case…" />;
  if (error && !disease && !pest) return <ErrorState message={error} onRetry={load} />;

  if (kind === 'disease' && disease) {
    const img = assetUrl(disease.image_url);
    const model =
      disease.disease?.model_name ||
      (typeof disease.model === 'string' ? disease.model : null) ||
      (disease.inference_meta?.model_id as string | undefined) ||
      'Not available';
    const rag =
      disease.advisory?.sources?.length
        ? `Grounded (${disease.advisory.sources.length} sources)`
        : disease.advisory
          ? 'Advisory present — check sources field'
          : 'Not available';
    const recStatus = disease.advisory?.immediate_action
      ? 'Recommendation generated'
      : 'Not available';

    return (
      <div>
        <PageHeader
          title="Disease case detail"
          description={`Case ${disease.id}`}
          actions={
            <Link to="/admin/disease-cases" className="text-xs font-semibold text-green-900 hover:underline">
              ← Back to disease cases
            </Link>
          }
        />
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel overflow-hidden rounded-xl">
            {img ? (
              <img src={img} alt={`Disease case ${disease.id}`} onError={handleImageError} className="max-h-[420px] w-full object-contain bg-stone-100" />
            ) : (
              <EmptyState title="No image available" />
            )}
            <p className="border-t border-stone-100 px-3 py-2 text-[11px] text-amber-800">
              AI outputs below are model predictions — not verified field diagnoses.
            </p>
          </div>
          <dl className="panel rounded-xl p-5">
            <Field label="Farmer" value={farmerLabel(users, disease.user_id)} />
            <Field label="Crop" value={disease.crop || '—'} />
            <Field label="Disease (AI)" value={disease.disease?.disease || '—'} />
            <Field label="AI confidence" value={formatConfidence(disease.disease?.confidence)} />
            <Field label="Model" value={<span className="font-mono text-xs">{String(model)}</span>} />
            <Field label="RAG status" value={rag} />
            <Field label="Recommendation status" value={recStatus} />
            <Field label="Risk (advisory)" value={disease.advisory?.overall_risk || 'Not available'} />
            <Field label="Validation" value={disease.validation_status || 'Not available'} />
            <Field label="Timestamp" value={formatDate(disease.created_at)} />
          </dl>
        </div>
      </div>
    );
  }

  if (kind === 'pest' && pest) {
    const img = assetUrl(pest.image_url);
    return (
      <div>
        <PageHeader
          title="Pest case detail"
          description={`Case ${pest.id}`}
          actions={
            <Link to="/admin/pest-cases" className="text-xs font-semibold text-green-900 hover:underline">
              ← Back to pest cases
            </Link>
          }
        />
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel overflow-hidden rounded-xl">
            {img ? (
              <div className="relative bg-stone-100">
                <img
                  src={img}
                  alt={`Pest case ${pest.id}`}
                  onError={handleImageError}
                  className="max-h-[420px] w-full object-contain"
                />
                {pestBoxes.map((box, i) => (
                  <div
                    key={i}
                    className="pointer-events-none absolute border-2 border-amber-500"
                    style={{ left: box.left, top: box.top, width: box.width, height: box.height }}
                    title={`${box.label} ${formatConfidence(box.conf)}`}
                  />
                ))}
              </div>
            ) : (
              <EmptyState title="No image available" />
            )}
            <p className="border-t border-stone-100 px-3 py-2 text-[11px] text-amber-800">
              Bounding boxes and labels are AI detections — preliminary, not accuracy claims.
            </p>
          </div>
          <dl className="panel rounded-xl p-5">
            <Field label="Farmer" value={farmerLabel(users, pest.user_id)} />
            <Field label="Crop" value={pest.crop || '—'} />
            <Field
              label="Detected pests (AI)"
              value={
                pest.detections?.length
                  ? pest.detections
                      .map((d) => `${d.pest || d.raw_label || 'pest'} (${formatConfidence(d.confidence)})`)
                      .join(', ')
                  : pest.pest || '—'
              }
            />
            <Field label="AI confidence (primary)" value={formatConfidence(pest.confidence)} />
            <Field label="Count" value={pest.count != null ? String(pest.count) : 'Not available'} />
            <Field label="Preliminary severity" value={pest.severity || 'Not available'} />
            <Field label="Model" value={<span className="font-mono text-xs">{pest.model || pest.model_id || 'Not available'}</span>} />
            <Field
              label="RAG status"
              value={
                pest.advisory?.guidance_available
                  ? 'Guidance available'
                  : pest.advisory
                    ? 'No grounded guidance'
                    : 'Not available'
              }
            />
            <Field label="Timestamp" value={formatDate(pest.timestamp || pest.created_at)} />
          </dl>
        </div>
      </div>
    );
  }

  return <EmptyState title="Case unavailable" detail="The requested case could not be loaded." />;
}
