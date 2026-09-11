import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import type { AnalysisResponse, PestAdminCase, User } from '../types';
import {
  DataSourceBadge,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from '../components/ui/States';
import {
  diseaseToRow,
  formatConfidence,
  formatDate,
  isHighRiskSeverity,
  pestToRow,
  type CaseKind,
  type UnifiedCaseRow,
} from '../lib/cases';

type TypeFilter = 'all' | CaseKind;

export function CasesPage({ lockedType }: { lockedType?: CaseKind }) {
  const [diseaseCases, setDiseaseCases] = useState<AnalysisResponse[]>([]);
  const [pestCases, setPestCases] = useState<PestAdminCase[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [typeFilter, setTypeFilter] = useState<TypeFilter>(lockedType || 'all');
  const [cropFilter, setCropFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [casesRes, pestsRes, usersRes] = await Promise.all([
        api.getAdminCases(),
        api.getPests(),
        api.getUsers(),
      ]);
      setDiseaseCases(casesRes.items);
      setPestCases(pestsRes.cases || []);
      setUsers(usersRes.items);
      setDataSource(casesRes.data_source || pestsRes.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cases');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (lockedType) setTypeFilter(lockedType);
  }, [lockedType]);

  const allRows: UnifiedCaseRow[] = useMemo(() => {
    return [
      ...diseaseCases.map((c) => diseaseToRow(c, users)),
      ...pestCases.map((c) => pestToRow(c, users)),
    ].sort((a, b) => String(b.date).localeCompare(String(a.date)));
  }, [diseaseCases, pestCases, users]);

  const crops = useMemo(() => {
    const set = new Set(allRows.map((r) => r.crop).filter((c) => c && c !== '—'));
    return Array.from(set).sort();
  }, [allRows]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return allRows.filter((r) => {
      if (typeFilter !== 'all' && r.kind !== typeFilter) return false;
      if (cropFilter !== 'all' && r.crop !== cropFilter) return false;
      if (severityFilter === 'high' && !isHighRiskSeverity(r.severity)) return false;
      if (severityFilter === 'other' && isHighRiskSeverity(r.severity)) return false;
      if (dateFrom && r.date && r.date.slice(0, 10) < dateFrom) return false;
      if (dateTo && r.date && r.date.slice(0, 10) > dateTo) return false;
      if (q) {
        const hay = `${r.id} ${r.farmerLabel} ${r.farmerId || ''} ${r.finding}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [allRows, typeFilter, cropFilter, severityFilter, dateFrom, dateTo, search]);

  const title =
    lockedType === 'disease'
      ? 'Disease Cases'
      : lockedType === 'pest'
        ? 'Pest Cases'
        : 'Cases';

  return (
    <div>
      <PageHeader
        title={title}
        description="Live cases from GET /admin/cases and GET /admin/pests. Filters applied client-side on loaded data."
        actions={<DataSourceBadge source={dataSource} />}
      />

      <div className="panel mb-4 rounded-xl p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          {!lockedType ? (
            <label className="block text-xs">
              <span className="mb-1 block font-semibold text-stone-600">Type</span>
              <select
                className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
              >
                <option value="all">All</option>
                <option value="disease">Disease</option>
                <option value="pest">Pest</option>
              </select>
            </label>
          ) : null}
          <label className="block text-xs">
            <span className="mb-1 block font-semibold text-stone-600">Crop</span>
            <select
              className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
            >
              <option value="all">All crops</option>
              {crops.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs">
            <span className="mb-1 block font-semibold text-stone-600">Severity</span>
            <select
              className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">All</option>
              <option value="high">High / Critical / Severe</option>
              <option value="other">Other / Unknown</option>
            </select>
          </label>
          <label className="block text-xs">
            <span className="mb-1 block font-semibold text-stone-600">From</span>
            <input
              type="date"
              className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </label>
          <label className="block text-xs">
            <span className="mb-1 block font-semibold text-stone-600">To</span>
            <input
              type="date"
              className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </label>
          <label className="block text-xs sm:col-span-2 xl:col-span-1">
            <span className="mb-1 block font-semibold text-stone-600">Search</span>
            <input
              type="search"
              placeholder="Farmer or case ID"
              className="min-h-11 w-full rounded-lg border border-stone-200 bg-white px-3 text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
      </div>

      <div className="panel overflow-hidden rounded-xl">
        {loading ? <LoadingState label="Loading cases…" /> : null}
        {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && filtered.length === 0 ? (
          <EmptyState
            title="No cases match filters"
            detail={allRows.length === 0 ? 'No backend cases available yet.' : 'Try clearing filters.'}
          />
        ) : null}
        {!loading && !error && filtered.length > 0 ? (
          <>
            <div className="admin-table-wrap hidden md:block">
              <table className="w-full text-left text-xs text-stone-700">
                <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                  <tr>
                    <th className="p-3">Farmer</th>
                    <th className="p-3">Crop</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Disease / Pest</th>
                    <th className="p-3">AI confidence</th>
                    <th className="p-3">Severity</th>
                    <th className="p-3">Date</th>
                    <th className="p-3">Model</th>
                    <th className="p-3"> </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {filtered.map((r) => (
                    <tr key={`${r.kind}-${r.id}`} className="hover:bg-stone-50">
                      <td className="p-3 font-semibold text-stone-900">{r.farmerLabel}</td>
                      <td className="p-3">{r.crop}</td>
                      <td className="p-3 capitalize">{r.kind}</td>
                      <td className="p-3">
                        {r.finding}
                        {r.kind === 'pest' && r.pestCount != null ? (
                          <span className="ml-1 text-stone-500">· count {r.pestCount}</span>
                        ) : null}
                      </td>
                      <td className="p-3">{formatConfidence(r.confidence)}</td>
                      <td className="p-3">{r.severity}</td>
                      <td className="p-3 text-stone-500">{formatDate(r.date)}</td>
                      <td className="p-3 font-mono text-[10px]">{r.model}</td>
                      <td className="p-3 text-right">
                        <Link
                          to={`/admin/cases/${r.kind}/${r.id}`}
                          className="inline-flex min-h-9 items-center rounded-lg bg-green-900 px-3 text-[11px] font-semibold text-white hover:bg-green-800"
                        >
                          Open
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="space-y-3 p-3 md:hidden">
              {filtered.map((r) => (
                <li key={`${r.kind}-${r.id}`} className="rounded-lg border border-stone-200 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold text-stone-900">{r.farmerLabel}</p>
                      <p className="text-xs text-stone-600">
                        {r.crop} · {r.kind} · {r.finding}
                        {r.kind === 'pest' && r.pestCount != null ? ` · count ${r.pestCount}` : ''}
                      </p>
                      <p className="mt-1 text-[11px] text-stone-500">
                        AI confidence {formatConfidence(r.confidence)} · {r.severity}
                      </p>
                      <p className="text-[11px] text-stone-500">{formatDate(r.date)}</p>
                    </div>
                    <Link
                      to={`/admin/cases/${r.kind}/${r.id}`}
                      className="shrink-0 rounded-lg bg-green-900 px-3 py-2 text-[11px] font-semibold text-white"
                    >
                      Open
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
            <p className="border-t border-stone-100 px-3 py-2 text-[11px] text-stone-500">
              Showing {filtered.length} of {allRows.length} loaded cases
            </p>
          </>
        ) : null}
      </div>
    </div>
  );
}

export function DiseaseCasesPage() {
  return <CasesPage lockedType="disease" />;
}

export function PestCasesPage() {
  return <CasesPage lockedType="pest" />;
}
