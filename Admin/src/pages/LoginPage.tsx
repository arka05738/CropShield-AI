import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Loader2 } from 'lucide-react';
import { api } from '../services/api';

const IS_DEV = import.meta.env.DEV;

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.login(email.trim(), password);
      navigate('/admin/dashboard', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <div
        className="pointer-events-none absolute inset-0 opacity-90"
        style={{
          background:
            'linear-gradient(135deg, #0f2419 0%, #14532d 42%, #292524 100%)',
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 20%, rgba(253,230,138,0.25), transparent 35%), radial-gradient(circle at 80% 70%, rgba(134,239,172,0.2), transparent 40%)',
        }}
      />

      <div className="relative w-full max-w-md panel rounded-2xl p-8">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-green-900 text-green-100">
            <Shield className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-2xl font-semibold text-stone-900">CropShield Admin</h1>
            <p className="text-sm text-stone-500">Operator & expert access only</p>
          </div>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-stone-500">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm text-stone-900 outline-none focus:border-green-700 focus:ring-2 focus:ring-green-700/20"
              required
              autoComplete="username"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-stone-500">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm text-stone-900 outline-none focus:border-green-700 focus:ring-2 focus:ring-green-700/20"
              required
              autoComplete="current-password"
            />
          </div>

          {error ? (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-900 py-2.5 text-sm font-semibold text-white hover:bg-green-800 disabled:opacity-60"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        {IS_DEV ? (
          <p className="mt-5 rounded-lg border border-stone-200 bg-stone-50 px-3 py-2 text-xs text-stone-500">
            Local dev only: demo accounts exist when backend has{' '}
            <span className="font-mono">SEED_DEMO_DATA=true</span> (never in production).
          </p>
        ) : null}
      </div>
    </div>
  );
}
