import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { HotspotGeoJSON } from '../types';
import { AdminGisMap } from '../components/admin/AdminGisMap';
import { ErrorState, LoadingState, PageHeader } from '../components/ui/States';

export function MapPage() {
  const [hotspots, setHotspots] = useState<HotspotGeoJSON | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (filters?: {
    crop?: string;
    disease?: string;
    state?: string;
    min_risk?: string;
  }) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHotspots(filters);
      setHotspots(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load map data');
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
        title="GIS map"
        description="Leaflet map of outbreak hotspots from the admin GIS API."
      />
      {loading && !hotspots ? <LoadingState label="Loading map layers…" /> : null}
      {error && !hotspots ? <ErrorState message={error} onRetry={() => load()} /> : null}
      {hotspots || (!loading && !error) ? (
        <AdminGisMap
          hotspots={hotspots}
          dataSource={hotspots?.data_source}
          onFilterChange={(filters) => {
            void load(filters);
          }}
        />
      ) : null}
    </div>
  );
}
