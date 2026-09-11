import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { User } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getUsers();
      setUsers(res.items);
      setDataSource(res.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
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
        title="Users"
        description="Accounts from GET /api/v1/admin/users"
        actions={<DataSourceBadge source={dataSource} />}
      />
      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && users.length === 0 ? (
          <EmptyState title="No users found" detail="The users endpoint returned an empty list." />
        ) : null}
        {!loading && !error && users.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3">Name</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Role</th>
                  <th className="p-3">Location</th>
                  <th className="p-3">Phone</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-stone-50">
                    <td className="p-3 font-semibold text-stone-900">{u.full_name}</td>
                    <td className="p-3 font-mono text-stone-600">{u.email}</td>
                    <td className="p-3">
                      <span className="rounded border border-stone-200 bg-stone-50 px-2 py-0.5 text-[10px] font-bold">
                        {u.role}
                      </span>
                    </td>
                    <td className="p-3 text-stone-500">
                      {[u.district, u.state].filter(Boolean).join(', ') || '—'}
                    </td>
                    <td className="p-3 text-stone-500">{u.phone || '—'}</td>
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
