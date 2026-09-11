import { getApiBase, getStoredUser, TOKEN_KEY, USER_KEY } from '../lib/auth';
import { PageHeader } from '../components/ui/States';

export function SettingsPage() {
  const user = getStoredUser();
  const apiBase = getApiBase();
  const viteBase = (import.meta.env.VITE_API_BASE_URL || '').trim() || '(empty → relative /api/v1)';
  const mode = import.meta.env.MODE;
  const dev = import.meta.env.DEV;

  return (
    <div>
      <PageHeader
        title="Settings"
        description="Environment and session information. No fake preference toggles."
      />

      <div className="grid max-w-3xl gap-4">
        <section className="panel rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-stone-900">API</h2>
          <dl className="grid gap-2 text-xs">
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">Resolved API base</dt>
              <dd className="font-mono text-stone-800">{apiBase}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">VITE_API_BASE_URL</dt>
              <dd className="font-mono text-stone-800">{viteBase}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">Vite mode</dt>
              <dd className="font-mono text-stone-800">{mode}{dev ? ' (dev)' : ''}</dd>
            </div>
            <div className="flex justify-between gap-4 py-2">
              <dt className="text-stone-500">Dev proxy targets</dt>
              <dd className="text-right font-mono text-stone-800">
                /api → http://127.0.0.1:8000
                <br />
                /uploads → http://127.0.0.1:8000
              </dd>
            </div>
          </dl>
        </section>

        <section className="panel rounded-xl p-5 space-y-3">
          <h2 className="text-sm font-semibold text-stone-900">Session persistence</h2>
          <p className="text-xs text-stone-500">
            Auth is stored in browser <code className="rounded bg-stone-100 px-1">localStorage</code> only.
            Clearing site data signs you out. Tokens are never embedded in source.
          </p>
          <dl className="grid gap-2 text-xs">
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">Token key</dt>
              <dd className="font-mono text-stone-800">{TOKEN_KEY}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">User key</dt>
              <dd className="font-mono text-stone-800">{USER_KEY}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-stone-100 py-2">
              <dt className="text-stone-500">Signed-in user</dt>
              <dd className="text-right text-stone-800">
                {user?.full_name || '—'}
                <br />
                <span className="font-mono text-[11px] text-stone-500">{user?.email}</span>
              </dd>
            </div>
            <div className="flex justify-between gap-4 py-2">
              <dt className="text-stone-500">Role</dt>
              <dd className="rounded-md border border-stone-200 bg-stone-50 px-2.5 py-1 text-[11px] font-semibold text-stone-700">
                {user?.role || '—'}
              </dd>
            </div>
          </dl>
        </section>

        <section className="panel rounded-xl p-5 space-y-2">
          <h2 className="text-sm font-semibold text-stone-900">Allowed admin roles</h2>
          <p className="text-xs text-stone-500">
            Login rejects <code className="rounded bg-stone-100 px-1">FARMER</code>. Allowed:{' '}
            ADMIN, SUPER_ADMIN, EXPERT, EXTENSION_WORKER.
          </p>
        </section>
      </div>
    </div>
  );
}
