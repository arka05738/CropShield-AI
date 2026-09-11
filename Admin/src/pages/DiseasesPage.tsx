import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { NameCountItem } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';

export function DiseasesPage() {
  const [items, setItems] = useState<NameCountItem[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDiseases();
      setItems(res.items);
      setDataSource(res.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load diseases');
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
        title="Diseases"
        description="Aggregated disease labels from GET /api/v1/admin/diseases"
        actions={<DataSourceBadge source={dataSource} />}
      />
      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && items.length === 0 ? (
          <EmptyState title="No disease aggregations" detail="Counts appear after analyses exist." />
        ) : null}
        {!loading && !error && items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3">Disease</th>
                  <th className="p-3 text-right">Count</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {items.map((item) => (
                  <tr key={item.name} className="hover:bg-stone-50">
                    <td className="p-3 font-semibold text-stone-900">{item.name}</td>
                    <td className="p-3 text-right font-mono font-bold text-green-900">{item.count}</td>
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
