import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { AnalysisResponse } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';

export function AnalysesPage() {
  const [cases, setCases] = useState<AnalysisResponse[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getAdminCases();
      setCases(res.items);
      setDataSource(res.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analyses');
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
        title="Analyses"
        description="Diagnostic cases from GET /api/v1/admin/cases"
        actions={<DataSourceBadge source={dataSource} />}
      />
      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && cases.length === 0 ? (
          <EmptyState title="No analyses yet" detail="Run farmer diagnoses to populate this table." />
        ) : null}
        {!loading && !error && cases.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3">ID</th>
                  <th className="p-3">Crop</th>
                  <th className="p-3">Disease</th>
                  <th className="p-3">Risk</th>
                  <th className="p-3">Validation</th>
                  <th className="p-3">Location</th>
                  <th className="p-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-stone-50">
                    <td className="p-3 font-mono font-bold text-green-900">{c.id}</td>
                    <td className="p-3 font-semibold">{c.crop}</td>
                    <td className="p-3">{c.disease?.disease || '—'}</td>
                    <td className="p-3">{c.advisory?.overall_risk || '—'}</td>
                    <td className="p-3">{c.validation_status || '—'}</td>
                    <td className="p-3 text-stone-500">
                      {[c.location?.district, c.location?.state].filter(Boolean).join(', ') || '—'}
                    </td>
                    <td className="p-3 text-stone-500">
                      {c.created_at ? new Date(c.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </div>
  );
}
