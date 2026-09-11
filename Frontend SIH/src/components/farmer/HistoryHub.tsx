import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnalysisResponse, PestDetectResponse } from '../../types';
import { useFarmerApp } from '../../context/FarmerAppContext';
import { SUPPORTED_CROPS, formatAiConfidence } from '../../lib/crops';
import { handleImageError } from '../../lib/imageFallback';

type Tab = 'all' | 'disease' | 'pest';

type Row = {
  id: string;
  kind: 'disease' | 'pest';
  crop: string;
  title: string;
  confidence: number | null | undefined;
  status: string;
  date: string;
  image: string;
};

export const HistoryHub: React.FC = () => {
  const navigate = useNavigate();
  const { analyses, pestAnalyses } = useFarmerApp();
  const [tab, setTab] = useState<Tab>('all');
  const [crop, setCrop] = useState('all');
  const [status, setStatus] = useState('all');

  const rows: Row[] = useMemo(() => {
    const d: Row[] = analyses.map((a: AnalysisResponse) => ({
      id: a.id,
      kind: 'disease',
      crop: a.crop || '—',
      title: a.disease?.disease || a.disease?.display_label || 'Disease scan',
      confidence: a.disease?.confidence,
      status: a.status,
      date: a.created_at,
      image: a.image_url,
    }));
    const p: Row[] = pestAnalyses.map((x: PestDetectResponse) => ({
      id: x.id,
      kind: 'pest',
      crop: x.crop_hint || x.crop || '—',
      title: x.pest || x.raw_label || (x.count ? `${x.count} pest detection(s)` : 'No pest detected'),
      confidence: x.confidence ?? x.detections?.[0]?.confidence,
      status: x.status,
      date: x.created_at,
      image: x.image_url,
    }));
    return [...d, ...p].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [analyses, pestAnalyses]);

  const filtered = rows.filter((r) => {
    if (tab !== 'all' && r.kind !== tab) return false;
    if (crop !== 'all' && r.crop.toLowerCase() !== crop.toLowerCase()) return false;
    if (status !== 'all' && r.status !== status) return false;
    return true;
  });

  const statuses = Array.from(new Set(rows.map((r) => r.status))).filter(Boolean);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl sm:text-3xl font-bold" style={{ fontFamily: 'var(--font-heading)' }}>
          History
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--cs-muted)' }}>
          Disease and pest analyses from your account only.
        </p>
      </header>

      <div className="flex gap-2 flex-wrap" role="tablist" aria-label="History type">
        {(['all', 'disease', 'pest'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            role="tab"
            aria-selected={tab === t}
            className="cs-btn min-h-[44px] px-4 text-sm"
            style={
              tab === t
                ? { background: 'var(--cs-primary)', color: '#fff' }
                : { background: 'var(--cs-surface)', border: '1px solid var(--cs-border)', color: 'var(--cs-ink-soft)' }
            }
            onClick={() => setTab(t)}
          >
            {t === 'all' ? 'All' : t === 'disease' ? 'Disease' : 'Pest'}
          </button>
        ))}
      </div>

      <div className="grid sm:grid-cols-2 gap-3">
        <div>
          <label className="cs-label" htmlFor="hist-crop">
            Crop
          </label>
          <select id="hist-crop" className="cs-input" value={crop} onChange={(e) => setCrop(e.target.value)}>
            <option value="all">All crops</option>
            {SUPPORTED_CROPS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="cs-label" htmlFor="hist-status">
            Status
          </label>
          <select id="hist-status" className="cs-input" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">All statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="cs-surface p-8 text-center">
          <p className="font-semibold">
            {tab === 'pest' ? 'No pest detections yet' : tab === 'disease' ? 'No analyses yet' : 'No analyses yet'}
          </p>
          <p className="text-sm mt-1" style={{ color: 'var(--cs-muted)' }}>
            Results appear here after you run a scan.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {filtered.map((item) => (
            <li key={`${item.kind}-${item.id}`}>
              <button
                type="button"
                className="cs-surface w-full p-3 flex gap-3 text-left"
                onClick={() =>
                  navigate(
                    item.kind === 'disease' ? `/farmer/reports/${item.id}` : `/farmer/pest-reports/${item.id}`
                  )
                }
              >
                <img
                  src={item.image}
                  alt=""
                  onError={handleImageError}
                  className="w-16 h-16 rounded-lg object-cover bg-[var(--cs-bg-accent)] shrink-0"
                />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap gap-2">
                    <span className="cs-chip" style={{ background: 'var(--cs-primary-soft)', color: 'var(--cs-primary)' }}>
                      {item.crop}
                    </span>
                    <span className="cs-chip" style={{ background: 'var(--cs-bg-accent)', color: 'var(--cs-ink-soft)' }}>
                      {item.kind}
                    </span>
                  </div>
                  <p className="font-bold truncate mt-1">{item.title}</p>
                  <p className="text-xs" style={{ color: 'var(--cs-muted)' }}>
                    AI confidence {formatAiConfidence(item.confidence)} · {item.status} ·{' '}
                    {new Date(item.date).toLocaleString()}
                  </p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
