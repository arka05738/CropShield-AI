import React from 'react';
import { Database, AlertCircle, Inbox, Loader2 } from 'lucide-react';

export function DataSourceBadge({ source }: { source?: string | null }) {
  if (!source) return null;
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-stone-200 bg-stone-50 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-stone-600">
      <Database className="h-3 w-3 text-green-800" />
      data_source: {source}
    </span>
  );
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20 text-stone-500">
      <Loader2 className="h-7 w-7 animate-spin text-green-800" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <Inbox className="h-8 w-8 text-stone-300" />
      <p className="text-sm font-semibold text-stone-700">{title}</p>
      {detail ? <p className="max-w-md text-xs text-stone-500">{detail}</p> : null}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const safe =
    /traceback|fastapi|starlette|pydantic|file \"|line \d+/i.test(message)
      ? 'API unavailable or returned an error. Retry, or check that the CropShield backend is running.'
      : message;
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center" role="alert">
      <AlertCircle className="h-8 w-8 text-amber-700" aria-hidden />
      <p className="text-sm font-semibold text-stone-800">{safe}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="min-h-10 rounded-lg bg-green-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-800"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export function UnauthorizedState() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center" role="alert">
      <AlertCircle className="h-8 w-8 text-amber-700" aria-hidden />
      <p className="text-sm font-semibold text-stone-800">Unauthorized</p>
      <p className="max-w-md text-xs text-stone-500">
        Farmer accounts cannot access the Admin console. Sign in with an ADMIN, SUPER_ADMIN, EXPERT, or
        EXTENSION_WORKER account.
      </p>
      <a
        href="#/login"
        onClick={(e) => {
          e.preventDefault();
          window.location.assign('/login');
        }}
        className="min-h-10 rounded-lg bg-green-900 px-4 py-2 text-xs font-semibold text-white hover:bg-green-800"
      >
        Go to login
      </a>
    </div>
  );
}

export function ApiUnavailableState({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      message="API unavailable. Confirm the CropShield backend is reachable (dev proxy → :8005)."
      onRetry={onRetry}
    />
  );
}

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-stone-900">{title}</h1>
        {description ? <p className="mt-1 text-sm text-stone-500">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
