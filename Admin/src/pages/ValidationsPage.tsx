import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ExpertValidationCase } from '../types';
import { ValidationQueue } from '../components/admin/ValidationQueue';
import { ErrorState, LoadingState, PageHeader } from '../components/ui/States';

export function ValidationsPage() {
  const [queue, setQueue] = useState<ExpertValidationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getValidationQueue();
      setQueue(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load validation queue');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const onReview = async (
    id: string,
    review: { status: string; confirmed_disease?: string; expert_notes: string }
  ) => {
    await api.reviewValidationCase(id, review);
    await load();
  };

  return (
    <div>
      <PageHeader
        title="Validations"
        description="Expert review queue from GET /api/v1/validation/queue"
      />
      {loading ? <LoadingState /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error ? <ValidationQueue queue={queue} onReview={onReview} /> : null}
    </div>
  );
}
