import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { getApiBase, getStoredUser, TOKEN_KEY, USER_KEY } from '../lib/auth';
import type { User } from '../types';
import { ErrorState, LoadingState, PageHeader } from '../components/ui/States';

export function ProfilePage() {
  const navigate = useNavigate();
  const stored = getStoredUser();
  const [profile, setProfile] = useState<User | null>(stored);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const apiBase = getApiBase();
  const viteBase = (import.meta.env.VITE_API_BASE_URL || '').trim() || '(empty → relative /api/v1)';

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const me = await api.getProfile();
      setProfile(me);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const logout = () => {
    api.logout();
    navigate('/login', { replace: true });
  };

  return (
    <div>
      <PageHeader
        title="Profile"
        description="Signed-in operator identity and public API configuration."
      />

      {loading ? <LoadingState label="Loading profile…" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}

      {!loading && !error && profile ? (
        <div className="grid max-w-3xl gap-4">
          <section className="panel rounded-xl p-5">
            <h2 className="text-sm font-semibold text-stone-900">Operator</h2>
            <dl className="mt-3 grid gap-2 text-xs">
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">Name</dt>
                <dd className="font-semibold text-stone-900">{profile.full_name}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">Email</dt>
                <dd className="font-mono text-stone-800">{profile.email}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">Role</dt>
                <dd className="rounded border border-stone-200 bg-stone-50 px-2 py-0.5 font-semibold">
                  {profile.role}
                </dd>
              </div>
              <div className="flex justify-between gap-4 py-2">
                <dt className="text-stone-500">Location</dt>
                <dd className="text-stone-800">
                  {[profile.district, profile.state].filter(Boolean).join(', ') || '—'}
                </dd>
              </div>
            </dl>
            <button
              type="button"
              onClick={logout}
              className="mt-4 min-h-11 rounded-lg border border-stone-200 bg-white px-4 text-xs font-semibold text-stone-800 hover:bg-stone-50"
            >
              Sign out (clears JWT session)
            </button>
          </section>

          <section className="panel rounded-xl p-5">
            <h2 className="text-sm font-semibold text-stone-900">API & security</h2>
            <p className="mt-1 text-xs text-stone-500">
              Frontend uses only the public API base URL. No Mongo URI, HF token, or JWT secret is stored in source.
            </p>
            <dl className="mt-3 grid gap-2 text-xs">
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">Resolved API base</dt>
                <dd className="font-mono text-stone-800">{apiBase}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">VITE_API_BASE_URL</dt>
                <dd className="font-mono text-stone-800">{viteBase}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
                <dt className="text-stone-500">Dev proxy</dt>
                <dd className="text-right font-mono text-stone-800">
                  /api → http://127.0.0.1:8005
                  <br />
                  /uploads → http://127.0.0.1:8005
                </dd>
              </div>
              <div className="flex justify-between gap-4 py-2">
                <dt className="text-stone-500">Session keys</dt>
                <dd className="font-mono text-stone-800">
                  {TOKEN_KEY}, {USER_KEY}
                </dd>
              </div>
            </dl>
          </section>
        </div>
      ) : null}
    </div>
  );
}
