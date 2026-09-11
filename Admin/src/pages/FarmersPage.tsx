import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import type { AnalysisResponse, PestAdminCase, User } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';
import { formatDate } from '../lib/cases';

export function FarmersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [diseaseCases, setDiseaseCases] = useState<AnalysisResponse[]>([]);
  const [pestCases, setPestCases] = useState<PestAdminCase[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [usersRes, casesRes, pestsRes] = await Promise.all([
        api.getUsers(),
        api.getAdminCases(),
        api.getPests(),
      ]);
      setUsers(usersRes.items);
      setDiseaseCases(casesRes.items);
      setPestCases(pestsRes.cases || []);
      setDataSource(usersRes.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load farmers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const farmers = useMemo(() => users.filter((u) => u.role === 'FARMER'), [users]);

  const activity = useMemo(() => {
    const byUser = new Map<string, { disease: number; pest: number; last?: string }>();
    for (const c of diseaseCases) {
      const uid = c.user_id || '';
      if (!uid) continue;
      const cur = byUser.get(uid) || { disease: 0, pest: 0 };
      cur.disease += 1;
      if (!cur.last || (c.created_at && c.created_at > cur.last)) cur.last = c.created_at;
      byUser.set(uid, cur);
    }
    for (const c of pestCases) {
      const uid = c.user_id || '';
      if (!uid) continue;
      const cur = byUser.get(uid) || { disease: 0, pest: 0 };
      cur.pest += 1;
      const ts = c.timestamp || c.created_at;
      if (ts && (!cur.last || ts > cur.last)) cur.last = ts;
      byUser.set(uid, cur);
    }
    return byUser;
  }, [diseaseCases, pestCases]);

  const recentAnalyses = useMemo(() => {
    const items = [
      ...diseaseCases.map((c) => ({
        id: c.id,
        type: 'disease' as const,
        userId: c.user_id,
        label: c.disease?.disease || c.crop,
        at: c.created_at,
      })),
      ...pestCases.map((c) => ({
        id: c.id,
        type: 'pest' as const,
        userId: c.user_id,
        label: c.pest || c.crop,
        at: c.timestamp || c.created_at || '',
      })),
    ]
      .sort((a, b) => String(b.at).localeCompare(String(a.at)))
      .slice(0, 15);
    return items;
  }, [diseaseCases, pestCases]);

  return (
    <div>
      <PageHeader
        title="Farmers"
        description="Farmer accounts from GET /admin/users. Passwords and tokens are never shown."
        actions={<DataSourceBadge source={dataSource} />}
      />

      {loading ? <LoadingState label="Loading farmers…" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}

      {!loading && !error ? (
        <>
          <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="panel rounded-xl p-4">
              <p className="text-xs text-stone-500">Total farmers</p>
              <p className="mt-1 font-[family-name:var(--font-heading)] text-3xl font-semibold">
                {farmers.length.toLocaleString()}
              </p>
            </div>
            <div className="panel rounded-xl p-4">
              <p className="text-xs text-stone-500">Disease analyses (all)</p>
              <p className="mt-1 font-[family-name:var(--font-heading)] text-3xl font-semibold">
                {diseaseCases.length.toLocaleString()}
              </p>
            </div>
            <div className="panel rounded-xl p-4">
              <p className="text-xs text-stone-500">Pest OD cases (all)</p>
              <p className="mt-1 font-[family-name:var(--font-heading)] text-3xl font-semibold">
                {pestCases.length.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="panel mb-4 overflow-hidden rounded-xl">
            {farmers.length === 0 ? (
              <EmptyState title="No farmer accounts" detail="No users with role FARMER in the admin users API." />
            ) : (
              <div className="admin-table-wrap">
                <table className="w-full text-left text-xs text-stone-700">
                  <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                    <tr>
                      <th className="p-3">Name</th>
                      <th className="p-3">Email</th>
                      <th className="p-3">Location</th>
                      <th className="p-3">Disease analyses</th>
                      <th className="p-3">Pest analyses</th>
                      <th className="p-3">Last activity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100">
                    {farmers.map((f) => {
                      const act = activity.get(f.id);
                      return (
                        <tr key={f.id} className="hover:bg-stone-50">
                          <td className="p-3 font-semibold text-stone-900">{f.full_name}</td>
                          <td className="p-3 font-mono text-stone-600">{f.email}</td>
                          <td className="p-3 text-stone-500">
                            {[f.district, f.state].filter(Boolean).join(', ') || '—'}
                          </td>
                          <td className="p-3">{act?.disease ?? 0}</td>
                          <td className="p-3">{act?.pest ?? 0}</td>
                          <td className="p-3 text-stone-500">{formatDate(act?.last)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <section className="panel rounded-xl p-5">
            <h2 className="text-sm font-semibold text-stone-900">Recent analyses</h2>
            <p className="mb-3 text-xs text-stone-500">Across disease and pest history</p>
            {recentAnalyses.length === 0 ? (
              <EmptyState title="No recent analyses" />
            ) : (
              <ul className="divide-y divide-stone-100 text-xs">
                {recentAnalyses.map((a) => {
                  const farmer = users.find((u) => u.id === a.userId);
                  return (
                    <li key={`${a.type}-${a.id}`} className="flex flex-wrap items-center justify-between gap-2 py-2.5">
                      <span>
                        <span className="font-semibold capitalize text-stone-800">{a.type}</span>
                        {' · '}
                        {a.label || a.id}
                        {' · '}
                        <span className="text-stone-500">{farmer?.full_name || a.userId || 'Unknown'}</span>
                      </span>
                      <span className="text-stone-500">{formatDate(a.at)}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}
