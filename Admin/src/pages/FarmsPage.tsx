import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { FarmRecord } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';

export function FarmsPage() {
  const [farms, setFarms] = useState<FarmRecord[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getFarms();
      setFarms(res.items);
      setDataSource(res.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load farms');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const columns = farms.length
    ? Array.from(
        new Set(
          farms.flatMap((f) =>
            Object.keys(f).filter((k) => f[k] !== undefined && f[k] !== null && typeof f[k] !== 'object')
          )
        )
      )
    : ['id', 'name', 'crop', 'district', 'state'];

  return (
    <div>
      <PageHeader
        title="Farms"
        description="Farm records from GET /api/v1/admin/farms"
        actions={<DataSourceBadge source={dataSource} />}
      />
      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && farms.length === 0 ? (
          <EmptyState
            title="No farms registered"
            detail="The farms store is empty until farm records are created by the backend."
          />
        ) : null}
        {!loading && !error && farms.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  {columns.map((col) => (
                    <th key={col} className="p-3">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {farms.map((farm, idx) => (
                  <tr key={String(farm.id ?? idx)} className="hover:bg-stone-50">
                    {columns.map((col) => (
                      <td key={col} className="p-3">
                        {String(farm[col] ?? '—')}
                      </td>
                    ))}
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
