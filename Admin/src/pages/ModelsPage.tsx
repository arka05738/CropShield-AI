import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { RegisteredModel } from '../types';
import { ModelRegistryAdmin } from '../components/admin/ModelRegistryAdmin';
import { ErrorState, LoadingState, PageHeader } from '../components/ui/States';

export function ModelsPage() {
  const [models, setModels] = useState<RegisteredModel[]>([]);
  const [note, setNote] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRegisteredModels();
      setModels(res.items);
      setNote(res.note);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load models');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div>
      <PageHeader
        title="Models"
        description="Disease and pest model registry from GET /api/v1/admin/models. Thresholds are filters, not accuracy."
      />
      {loading ? <LoadingState /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error ? (
        <ModelRegistryAdmin
          models={models}
          note={note}
          onUpdateThreshold={async (id, threshold) => {
            await api.updateModelThreshold(id, threshold);
            await load();
          }}
        />
      ) : null}
    </div>
  );
}
