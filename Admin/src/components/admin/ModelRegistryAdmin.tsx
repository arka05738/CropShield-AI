import React, { useEffect, useState } from 'react';
import { Cpu, CheckCircle2 } from 'lucide-react';
import type { RegisteredModel } from '../../types';
import { EmptyState } from '../ui/States';

interface ModelRegistryAdminProps {
  models: RegisteredModel[];
  note?: string;
  onUpdateThreshold: (id: string, threshold: number) => Promise<void>;
}

function scopeText(model: RegisteredModel): string {
  if (model.crop_routing && typeof model.crop_routing === 'object') {
    const crops = Object.keys(model.crop_routing);
    if (crops.length) return `Crops: ${crops.join(', ')}`;
  }
  if (typeof model.supported_classes_count === 'number') {
    return `${model.supported_classes_count} pest classes (IP102 scope)`;
  }
  const classes = model.supported_classes || [];
  if (classes.length) {
    const shown = classes.slice(0, 8).join(', ');
    return classes.length > 8 ? `${shown} (+${classes.length - 8})` : shown;
  }
  return 'Not available';
}

export const ModelRegistryAdmin: React.FC<ModelRegistryAdminProps> = ({
  models,
  note,
  onUpdateThreshold,
}) => {
  const [thresholds, setThresholds] = useState<Record<string, number>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  useEffect(() => {
    setThresholds(models.reduce((acc, m) => ({ ...acc, [m.id]: m.threshold }), {}));
  }, [models]);

  const diseaseModels = models.filter(
    (m) =>
      m.id.includes('disease') ||
      String(m.task).toLowerCase().includes('disease') ||
      m.id.includes('crop_classifier') ||
      m.id.includes('gatekeeper')
  );
  const pestModels = models.filter(
    (m) => m.id.includes('pest') || String(m.task).toLowerCase().includes('pest')
  );
  const otherModels = models.filter(
    (m) => !diseaseModels.includes(m) && !pestModels.includes(m)
  );

  const handleSave = async (id: string) => {
    setSavingId(id);
    try {
      await onUpdateThreshold(id, thresholds[id]);
    } catch (err) {
      console.error(err);
    } finally {
      setSavingId(null);
    }
  };

  const renderCard = (model: RegisteredModel) => (
    <article
      key={model.id}
      className="panel flex flex-col justify-between space-y-4 rounded-xl p-5"
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="block text-[10px] font-bold uppercase tracking-wider text-green-800">
              {model.task}
            </span>
            <h3 className="mt-0.5 text-base font-semibold text-stone-900">{model.model_name}</h3>
            <p className="mt-1 font-mono text-[10px] text-stone-500">
              Registry ID: {model.id}
            </p>
          </div>
          <span className="rounded border border-green-200 bg-green-50 px-2 py-0.5 text-[10px] font-bold text-green-900">
            {model.status}
          </span>
        </div>

        <dl className="space-y-2 text-xs">
          <div className="flex justify-between gap-3">
            <dt className="text-stone-500">Provider</dt>
            <dd className="text-right font-medium text-stone-800">{model.provider}</dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-stone-500">Model ID</dt>
            <dd className="max-w-[60%] break-all text-right font-mono text-[10px] text-stone-800">
              {model.model_id || model.model_name || 'Not available'}
            </dd>
          </div>
          <div className="flex justify-between gap-3">
            <dt className="text-stone-500">Architecture / mode</dt>
            <dd className="text-right font-medium text-stone-800">
              {model.inference_mode || model.version || 'Not available'}
            </dd>
          </div>
          <div>
            <dt className="text-stone-500">Supported crop / pest scope</dt>
            <dd className="mt-1 text-stone-800">{scopeText(model)}</dd>
          </div>
          {model.endpoint ? (
            <div className="flex justify-between gap-3">
              <dt className="text-stone-500">Endpoint</dt>
              <dd className="font-mono text-[10px] text-stone-700">{String(model.endpoint)}</dd>
            </div>
          ) : null}
        </dl>

        {model.note ? (
          <p className="rounded-lg border border-amber-100 bg-amber-50/80 px-3 py-2 text-[11px] text-amber-950">
            {String(model.note)}
          </p>
        ) : null}

        {String(model.note || '').toLowerCase().includes('map') ? (
          <p className="text-[11px] font-semibold text-stone-600">
            Model-reported metric (not CropShield accuracy) — see registry note above.
          </p>
        ) : null}
      </div>

      <div className="space-y-2 border-t border-stone-100 pt-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-stone-500">Confidence threshold (filter)</span>
          <span className="font-mono font-bold text-green-900">
            {Math.round((thresholds[model.id] ?? model.threshold) * 100)}%
          </span>
        </div>
        <label className="sr-only" htmlFor={`threshold-${model.id}`}>
          Confidence threshold for {model.model_name}
        </label>
        <input
          id={`threshold-${model.id}`}
          type="range"
          min="0.30"
          max="0.95"
          step="0.05"
          value={thresholds[model.id] ?? model.threshold}
          onChange={(e) =>
            setThresholds((prev) => ({ ...prev, [model.id]: parseFloat(e.target.value) }))
          }
          className="w-full accent-green-800"
        />
        <button
          type="button"
          onClick={() => void handleSave(model.id)}
          disabled={savingId === model.id}
          className="min-h-10 w-full rounded-lg bg-green-900 text-xs font-semibold text-white hover:bg-green-800 disabled:opacity-60"
        >
          {savingId === model.id ? 'Saving…' : 'Save threshold metadata'}
        </button>
      </div>
    </article>
  );

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="panel flex flex-col items-start justify-between gap-3 rounded-xl p-6 sm:flex-row sm:items-center">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-lg border border-green-200 bg-green-50 p-1.5 text-green-800">
              <Cpu className="h-4 w-4" aria-hidden />
            </span>
            <h2 className="text-xl font-semibold text-stone-900">Model monitoring</h2>
          </div>
          <p className="text-xs text-stone-500">
            Configuration from GET /api/v1/admin/models. No invented accuracy metrics.
          </p>
          {note ? <p className="mt-2 text-[11px] text-amber-900">{note}</p> : null}
        </div>
        <span className="flex items-center gap-1.5 rounded-lg border border-green-200 bg-green-50 px-3 py-1.5 text-xs font-bold text-green-900">
          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
          {models.length} registered
        </span>
      </div>

      {models.length === 0 ? (
        <div className="panel rounded-xl">
          <EmptyState title="No models registered" detail="GET /api/v1/admin/models returned an empty list." />
        </div>
      ) : (
        <>
          {diseaseModels.length > 0 ? (
            <section>
              <h3 className="mb-3 text-sm font-semibold text-stone-900">Disease models</h3>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {diseaseModels.map(renderCard)}
              </div>
            </section>
          ) : null}
          {pestModels.length > 0 ? (
            <section>
              <h3 className="mb-3 text-sm font-semibold text-stone-900">Pest model</h3>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {pestModels.map(renderCard)}
              </div>
            </section>
          ) : null}
          {otherModels.length > 0 ? (
            <section>
              <h3 className="mb-3 text-sm font-semibold text-stone-900">Other registry entries</h3>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {otherModels.map(renderCard)}
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
};
