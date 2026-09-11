import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import type { HotspotGeoJSON } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';

export function HotspotsPage() {
  const [hotspots, setHotspots] = useState<HotspotGeoJSON | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHotspots();
      setHotspots(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load hotspots');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const features = hotspots?.features || [];

  return (
    <div>
      <PageHeader
        title="Hotspots"
        description="Outbreak features from GET /api/v1/admin/hotspots"
        actions={
          <>
            <DataSourceBadge source={hotspots?.data_source} />
            <Link
              to="/admin/map"
              className="rounded-lg bg-green-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-800"
            >
              Open GIS map
            </Link>
          </>
        }
      />
      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && features.length === 0 ? (
          <EmptyState title="No hotspot features" detail="Hotspots appear when geospatial cases exist." />
        ) : null}
        {!loading && !error && features.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3">District</th>
                  <th className="p-3">State</th>
                  <th className="p-3">Crop</th>
                  <th className="p-3">Disease</th>
                  <th className="p-3">Risk</th>
                  <th className="p-3 text-right">Cases</th>
                  <th className="p-3 text-right">Farms</th>
                  <th className="p-3 text-right">Trend %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {features.map((f) => (
                  <tr key={f.properties.id} className="hover:bg-stone-50">
                    <td className="p-3 font-semibold text-stone-900">{f.properties.district}</td>
                    <td className="p-3">{f.properties.state}</td>
                    <td className="p-3">{f.properties.crop}</td>
                    <td className="p-3">{f.properties.disease}</td>
                    <td className="p-3">{f.properties.risk_level}</td>
                    <td className="p-3 text-right font-mono">{f.properties.case_count}</td>
                    <td className="p-3 text-right font-mono">{f.properties.farm_count}</td>
                    <td className="p-3 text-right font-mono">{f.properties.trend_pct}</td>
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
