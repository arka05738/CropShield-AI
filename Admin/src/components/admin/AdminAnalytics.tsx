import React, { useState } from 'react';
import type { AdminAnalytics as AdminAnalyticsType, AnalysisResponse } from '../../types';
import {
  Users,
  Sprout,
  Activity,
  AlertOctagon,
  CheckCircle,
  Download,
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
} from 'recharts';
import { DataSourceBadge, EmptyState, LoadingState } from '../ui/States';

interface AdminAnalyticsProps {
  analytics: AdminAnalyticsType | null;
  cases: AnalysisResponse[];
  loading?: boolean;
  error?: string | null;
  onSelectCase?: (analysis: AnalysisResponse) => void;
  onRetry?: () => void;
}

export const AdminAnalyticsView: React.FC<AdminAnalyticsProps> = ({
  analytics,
  cases,
  loading,
  error,
  onSelectCase,
}) => {
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv');

  if (loading) return <LoadingState label="Loading analytics from API…" />;
  if (error) {
    return (
      <div className="panel rounded-xl p-6 text-sm text-amber-900">
        {error}
      </div>
    );
  }
  if (!analytics) {
    return <EmptyState title="No analytics payload" detail="The analytics endpoint returned no data." />;
  }

  const handleExportData = () => {
    if (exportFormat === 'json') {
      const dataStr =
        'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(cases, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute(
        'download',
        `cropshield_cases_${new Date().toISOString().slice(0, 10)}.json`
      );
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      return;
    }

    const headers = [
      'ID',
      'Crop',
      'Disease',
      'Pathogen_Type',
      'Risk_Level',
      'Risk_Score',
      'Pests_Count',
      'District',
      'State',
      'Created_At',
    ];
    const rows = cases.map((c) => [
      c.id,
      c.crop,
      `"${c.disease?.disease || ''}"`,
      c.disease?.pathogen_type || '',
      c.advisory?.overall_risk || '',
      c.advisory?.risk_score ?? '',
      c.pests?.length ?? 0,
      c.location?.district || '',
      c.location?.state || '',
      c.created_at,
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', encodeURI(csvContent));
    downloadAnchor.setAttribute(
      'download',
      `cropshield_cases_${new Date().toISOString().slice(0, 10)}.csv`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const kpis = [
    {
      label: 'Enrolled farmers',
      value: analytics.total_farmers,
      icon: Users,
      tone: 'text-green-800',
    },
    {
      label: 'Registered farms',
      value: analytics.total_farms,
      icon: Sprout,
      tone: 'text-stone-700',
    },
    {
      label: 'Total analyses',
      value: analytics.total_analyses,
      icon: Activity,
      tone: 'text-stone-800',
    },
    {
      label: 'Disease cases',
      value: analytics.disease_cases,
      icon: AlertOctagon,
      tone: 'text-amber-800',
    },
    {
      label: 'High-risk areas',
      value: analytics.high_risk_areas,
      icon: AlertOctagon,
      tone: 'text-red-800',
    },
    {
      label: 'Expert-review agreement %',
      value: analytics.validation_accuracy_rate,
      icon: CheckCircle,
      tone: 'text-green-800',
    },
  ];

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="panel flex flex-col items-start justify-between gap-4 rounded-xl p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-lg border border-green-200 bg-green-50 p-1.5 text-green-800">
              <Activity className="h-4 w-4" />
            </span>
            <h2 className="text-xl font-semibold text-stone-900">Surveillance analytics</h2>
          </div>
          <p className="text-xs text-stone-500">
            Metrics computed from backend store — no fabricated growth percentages.
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <DataSourceBadge source={analytics.data_source} />
            {analytics.is_demo_inflated ? (
              <span className="rounded-md border border-amber-200 bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-amber-900">
                demo inflated
              </span>
            ) : null}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'csv' | 'json')}
            className="rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs text-stone-700"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
          <button
            type="button"
            onClick={handleExportData}
            disabled={cases.length === 0}
            className="flex items-center gap-1.5 rounded-lg bg-green-900 px-4 py-2 text-xs font-bold text-white hover:bg-green-800 disabled:opacity-50"
          >
            <Download className="h-4 w-4" /> Export cases
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="panel rounded-xl p-4">
            <div className="flex items-center justify-between text-xs text-stone-500">
              <span>{kpi.label}</span>
              <kpi.icon className={`h-4 w-4 ${kpi.tone}`} />
            </div>
            <p className={`mt-1 font-[family-name:var(--font-heading)] text-2xl font-semibold ${kpi.tone}`}>
              {Number(kpi.value).toLocaleString()}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="panel space-y-4 rounded-xl p-6 lg:col-span-6">
          <div>
            <h3 className="text-sm font-semibold text-stone-900">Disease distribution</h3>
            <p className="text-xs text-stone-500">From recorded analyses</p>
          </div>
          {analytics.disease_distribution.length === 0 ? (
            <EmptyState title="No disease distribution yet" />
          ) : (
            <>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analytics.disease_distribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="count"
                      nameKey="name"
                    >
                      {analytics.disease_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color || '#166534'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#fff',
                        borderColor: '#e7e5e4',
                        borderRadius: '0.75rem',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-3">
                {analytics.disease_distribution.map((d, i) => (
                  <div key={i} className="flex items-center gap-1.5 truncate">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ backgroundColor: d.color }}
                    />
                    <span className="truncate text-stone-600">
                      {d.name} ({d.count})
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="panel space-y-4 rounded-xl p-6 lg:col-span-6">
          <div>
            <h3 className="text-sm font-semibold text-stone-900">Regional case volume</h3>
            <p className="text-xs text-stone-500">Top jurisdictions from API</p>
          </div>
          {analytics.regional_cases.length === 0 ? (
            <EmptyState title="No regional cases yet" />
          ) : (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.regional_cases} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                  <XAxis type="number" stroke="#78716c" fontSize={11} />
                  <YAxis dataKey="region" type="category" stroke="#57534e" fontSize={11} width={120} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      borderColor: '#e7e5e4',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="cases" fill="#166534" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      <div className="panel space-y-4 rounded-xl p-6">
        <div>
          <h3 className="text-sm font-semibold text-stone-900">Timeline trends</h3>
          <p className="text-xs text-stone-500">Daily case volume from analysis timestamps</p>
        </div>
        {analytics.timeline_trends.length === 0 ? (
          <EmptyState title="No timeline data yet" />
        ) : (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics.timeline_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                <XAxis dataKey="date" stroke="#78716c" fontSize={11} />
                <YAxis stroke="#78716c" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    borderColor: '#e7e5e4',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                  }}
                />
                <Line type="monotone" dataKey="cases" stroke="#b91c1c" strokeWidth={2.5} name="Cases" />
                <Line type="monotone" dataKey="critical" stroke="#a16207" strokeWidth={2} name="Critical/High" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="panel space-y-4 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-stone-900">Recent analyses</h3>
          <span className="text-xs text-stone-500">{cases.length} records</span>
        </div>
        {cases.length === 0 ? (
          <EmptyState title="No analysis cases returned" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3">Case ID</th>
                  <th className="p-3">Crop</th>
                  <th className="p-3">Disease</th>
                  <th className="p-3">Pests</th>
                  <th className="p-3">Risk</th>
                  <th className="p-3">Location</th>
                  <th className="p-3">Created</th>
                  {onSelectCase ? <th className="p-3 text-right">Action</th> : null}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-stone-50">
                    <td className="p-3 font-mono font-bold text-green-900">{c.id}</td>
                    <td className="p-3 font-semibold text-stone-900">{c.crop}</td>
                    <td className="p-3">{c.disease?.disease || '—'}</td>
                    <td className="p-3">{c.pests?.length ? c.pests[0].name : 'None'}</td>
                    <td className="p-3">{c.advisory?.overall_risk || '—'}</td>
                    <td className="p-3 text-stone-500">
                      {[c.location?.district, c.location?.state].filter(Boolean).join(', ') || '—'}
                    </td>
                    <td className="p-3 text-stone-500">
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                    </td>
                    {onSelectCase ? (
                      <td className="p-3 text-right">
                        <button
                          type="button"
                          onClick={() => onSelectCase(c)}
                          className="rounded bg-stone-100 px-2.5 py-1 font-semibold text-stone-700 hover:bg-green-900 hover:text-white"
                        >
                          Inspect
                        </button>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
