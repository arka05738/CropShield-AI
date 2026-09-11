import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  FlaskConical,
  Leaf,
  Bug,
  AlertTriangle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import type { AdminAnalytics, AnalysisResponse, PestAdminCase, User } from '../types';
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
} from '../lib/cases';

const CHART_COLORS = ['#14532d', '#166534', '#15803d', '#3f6212', '#365314', '#4d7c0f', '#65a30d', '#84cc16'];

export function DashboardPage() {
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [diseaseCases, setDiseaseCases] = useState<AnalysisResponse[]>([]);
  const [pestCases, setPestCases] = useState<PestAdminCase[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [dataSource, setDataSource] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [stats, casesRes, pestsRes, usersRes] = await Promise.all([
        api.getAdminAnalytics(),
        api.getAdminCases(),
        api.getPests(),
        api.getUsers(),
      ]);
      setAnalytics(stats);
      setDiseaseCases(casesRes.items);
      setPestCases(pestsRes.cases || []);
      setUsers(usersRes.items);
      setDataSource(stats.data_source || casesRes.data_source);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const highRiskCount = useMemo(() => {
    const diseaseHigh = diseaseCases.filter((c) =>
      isHighRiskSeverity(c.advisory?.overall_risk || '')
    ).length;
    const pestHigh = pestCases.filter((c) => isHighRiskSeverity(c.severity || '')).length;
    return diseaseHigh + pestHigh;
  }, [diseaseCases, pestCases]);

  const cropDistribution = useMemo(() => {
    const map = new Map<string, number>();
    for (const c of diseaseCases) {
      const crop = (c.crop || 'Unknown').trim() || 'Unknown';
      map.set(crop, (map.get(crop) || 0) + 1);
    }
    for (const c of pestCases) {
      const crop = (c.crop || 'Unknown').trim() || 'Unknown';
      map.set(crop, (map.get(crop) || 0) + 1);
    }
    return Array.from(map.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 12);
  }, [diseaseCases, pestCases]);

  const recentRows = useMemo(() => {
    const rows = [
      ...diseaseCases.map((c) => diseaseToRow(c, users)),
      ...pestCases.map((c) => pestToRow(c, users)),
    ];
    return rows
      .sort((a, b) => String(b.date).localeCompare(String(a.date)))
      .slice(0, 12);
  }, [diseaseCases, pestCases, users]);

  const timelinePeriod = useMemo(() => {
    const t = analytics?.timeline_trends || [];
    if (t.length === 0) return 'No period data';
    return `${t[0].date} → ${t[t.length - 1].date} (daily buckets from disease analyses)`;
  }, [analytics]);

  if (loading) return <LoadingState label="Loading dashboard…" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!analytics) return <ErrorState message="No analytics data" onRetry={load} />;

  const farmerCount = users.filter((u) => u.role === 'FARMER').length;
  const cards = [
    {
      label: 'Total analyses',
      value: analytics.total_analyses,
      to: '/admin/cases',
      icon: FlaskConical,
      note: 'Disease diagnoses',
    },
    {
      label: 'Disease cases',
      value: analytics.disease_cases,
      to: '/admin/disease-cases',
      icon: Leaf,
      note: 'Non-healthy disease labels',
    },
    {
      label: 'Pest cases',
      value: analytics.pest_cases,
      to: '/admin/pest-cases',
      icon: Bug,
      note: 'Pest OD + legacy embeds',
    },
    {
      label: 'High-risk / high severity',
      value: highRiskCount,
      to: '/admin/cases',
      icon: AlertTriangle,
      note: 'From advisory risk + pest severity',
    },
    {
      label: 'Active farmers',
      value: farmerCount || analytics.total_farmers,
      to: '/admin/farmers',
      icon: Users,
      note: 'Accounts with role FARMER',
    },
  ];

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Operational overview from live admin APIs. No fabricated metrics."
        actions={<DataSourceBadge source={dataSource} />}
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {cards.map((card) => (
          <Link
            key={card.label}
            to={card.to}
            className="panel group rounded-xl p-5 transition-colors hover:border-green-400 focus-visible:ring-2 focus-visible:ring-green-700"
          >
            <div className="flex items-center justify-between text-xs text-stone-500">
              <span>{card.label}</span>
              <card.icon className="h-4 w-4 text-green-800" aria-hidden />
            </div>
            <p className="mt-2 font-[family-name:var(--font-heading)] text-3xl font-semibold text-stone-900">
              {Number(card.value).toLocaleString()}
            </p>
            <p className="mt-1 text-[11px] text-stone-500">{card.note}</p>
          </Link>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section className="panel rounded-xl p-5" aria-labelledby="disease-dist-heading">
          <h2 id="disease-dist-heading" className="text-sm font-semibold text-stone-900">
            Disease distribution
          </h2>
          <p className="text-xs text-stone-500">From GET /admin/analytics · recorded disease labels</p>
          {(analytics.disease_distribution || []).length === 0 ? (
            <EmptyState title="No disease distribution yet" detail="Run disease diagnoses to populate." />
          ) : (
            <div className="mt-3 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analytics.disease_distribution}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {analytics.disease_distribution.map((entry, i) => (
                      <Cell key={entry.name} fill={entry.color || CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="panel rounded-xl p-5" aria-labelledby="pest-dist-heading">
          <h2 id="pest-dist-heading" className="text-sm font-semibold text-stone-900">
            Pest distribution
          </h2>
          <p className="text-xs text-stone-500">From GET /admin/analytics · pest OD + legacy embeds</p>
          {(analytics.pest_distribution || []).length === 0 ? (
            <EmptyState title="No pest distribution yet" detail="Run pest detections to populate." />
          ) : (
            <div className="mt-3 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.pest_distribution.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d7e0d8" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={70} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#166534" radius={[4, 4, 0, 0]} name="Detections" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="panel rounded-xl p-5" aria-labelledby="crop-dist-heading">
          <h2 id="crop-dist-heading" className="text-sm font-semibold text-stone-900">
            Crop distribution
          </h2>
          <p className="text-xs text-stone-500">Derived from disease cases + pest OD cases currently loaded</p>
          {cropDistribution.length === 0 ? (
            <EmptyState title="No crop distribution yet" />
          ) : (
            <div className="mt-3 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cropDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d7e0d8" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#14532d" radius={[4, 4, 0, 0]} name="Cases" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="panel rounded-xl p-5" aria-labelledby="trend-heading">
          <h2 id="trend-heading" className="text-sm font-semibold text-stone-900">
            Analysis trend over time
          </h2>
          <p className="text-xs text-stone-500">Period: {timelinePeriod}</p>
          {(analytics.timeline_trends || []).length === 0 ? (
            <EmptyState title="No timeline data yet" />
          ) : (
            <div className="mt-3 h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics.timeline_trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#d7e0d8" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="cases" stroke="#14532d" strokeWidth={2} name="Disease analyses" />
                  <Line type="monotone" dataKey="critical" stroke="#b45309" strokeWidth={2} name="High/Critical risk" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
      </div>

      <section className="panel mt-6 rounded-xl p-5" aria-labelledby="recent-heading">
        <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
          <div>
            <h2 id="recent-heading" className="text-sm font-semibold text-stone-900">
              Recent cases
            </h2>
            <p className="text-xs text-stone-500">Disease + pest OD, newest first</p>
          </div>
          <Link to="/admin/cases" className="text-xs font-semibold text-green-900 hover:underline">
            View all cases →
          </Link>
        </div>
        {recentRows.length === 0 ? (
          <EmptyState title="No cases yet" detail="Farmer diagnoses and pest detections will appear here." />
        ) : (
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
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {recentRows.map((r) => (
                    <tr key={`${r.kind}-${r.id}`} className="hover:bg-stone-50">
                      <td className="p-3">
                        <Link
                          to={`/admin/cases/${r.kind}/${r.id}`}
                          className="font-semibold text-green-900 hover:underline"
                        >
                          {r.farmerLabel}
                        </Link>
                      </td>
                      <td className="p-3">{r.crop}</td>
                      <td className="p-3 capitalize">{r.kind}</td>
                      <td className="p-3">
                        {r.finding}
                        {r.kind === 'pest' && r.pestCount != null ? (
                          <span className="ml-1 text-stone-500">(count {r.pestCount})</span>
                        ) : null}
                      </td>
                      <td className="p-3">{formatConfidence(r.confidence)}</td>
                      <td className="p-3">{r.severity}</td>
                      <td className="p-3 text-stone-500">{formatDate(r.date)}</td>
                      <td className="p-3 font-mono text-[10px] text-stone-600">{r.model}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <ul className="space-y-3 md:hidden">
              {recentRows.map((r) => (
                <li key={`${r.kind}-${r.id}`} className="rounded-lg border border-stone-200 bg-stone-50 p-3">
                  <Link to={`/admin/cases/${r.kind}/${r.id}`} className="font-semibold text-green-900">
                    {r.farmerLabel} · {r.finding}
                  </Link>
                  <p className="mt-1 text-xs text-stone-600">
                    {r.crop} · {r.kind} · AI confidence {formatConfidence(r.confidence)}
                  </p>
                  <p className="text-xs text-stone-500">{formatDate(r.date)}</p>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <p className="mt-4 text-[11px] text-stone-500">
        Expert validation confirmation rate (reviewed cases):{' '}
        <span className="font-semibold text-stone-700">{analytics.validation_accuracy_rate}%</span>
        {' — '}labeled as expert-review agreement, not model accuracy.
      </p>
    </div>
  );
}
