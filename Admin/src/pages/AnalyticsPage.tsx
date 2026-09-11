import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { AdminAnalytics, AnalysisResponse } from '../types';
import { AdminAnalyticsView } from '../components/admin/AdminAnalytics';
import { PageHeader } from '../components/ui/States';

export function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [cases, setCases] = useState<AnalysisResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [stats, caseRes] = await Promise.all([
        api.getAdminAnalytics(),
        api.getAdminCases(),
      ]);
      setAnalytics(stats);
      setCases(caseRes.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
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
        title="Analytics"
        description="Charts and KPIs from GET /api/v1/admin/analytics"
      />
      <AdminAnalyticsView
        analytics={analytics}
        cases={cases}
        loading={loading}
        error={error}
        onRetry={load}
      />
    </div>
  );
}
