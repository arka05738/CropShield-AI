import React, { useState } from 'react';
import {
  BookOpen,
  Upload,
  Trash2,
  RefreshCw,
  FileText,
  CheckCircle2,
  Search,
  Eye,
  Database,
  Layers,
  X,
  Clock,
  Sprout,
  Bug,
  FlaskConical,
  AlertTriangle,
} from 'lucide-react';
import type { KnowledgeDocument } from '../../types';
import { api } from '../../services/api';
import { EmptyState } from '../ui/States';

interface KnowledgeBaseAdminProps {
  documents: KnowledgeDocument[];
  onUpload: (formData: FormData) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onReindex: () => Promise<void>;
}

const SECTORS = [
  'All Sectors',
  'Cereals & Grains',
  'Pulses & Oilseeds',
  'Vegetables & Spices',
  'Fruits & Plantation',
  'Commercial & Cash Crops',
];

const AVAILABLE_CROPS = [
  'Tomato', 'Rice', 'Cotton', 'Potato', 'Wheat',
  'Maize', 'Chilli', 'Soybean', 'Sugarcane', 'Groundnut',
  'Chickpea', 'Mustard', 'Onion', 'Banana', 'Mango',
  'Apple', 'Grapes', 'Pomegranate', 'Tea', 'Coffee',
];

type PopRecord = {
  condition_summary?: string;
  authority?: string;
  page_number?: number;
  pesticide?: {
    active_ingredient?: string;
    chemical_name?: string;
    exact_dose_per_liter?: string;
    application_method?: string;
    withholding_period_days?: number;
    safety_warnings?: string[];
  };
  fertilizer?: {
    n_ratio?: string;
    p_ratio?: string;
    k_ratio?: string;
    instructions?: string;
  };
  ipm?: {
    biological?: string[];
    cultural?: string[];
    mechanical?: string[];
    chemical?: string[];
  };
  monitoring?: {
    day_1?: string;
    day_3?: string;
    day_7?: string;
    day_14?: string;
  };
};

export const KnowledgeBaseAdmin: React.FC<KnowledgeBaseAdminProps> = ({
  documents,
  onUpload,
  onDelete,
  onReindex,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('All Sectors');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);
  const [reindexSuccessMessage, setReindexSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inspectDoc, setInspectDoc] = useState<KnowledgeDocument | null>(null);
  const [inspectPopRecord, setInspectPopRecord] = useState<PopRecord | null>(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [title, setTitle] = useState('');
  const [authority, setAuthority] = useState('ICAR / State Agricultural University');
  const [crop, setCrop] = useState('Tomato');
  const [sector, setSector] = useState('Vegetables & Spices');
  const [topic, setTopic] = useState('Integrated Crop Protection');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.authority.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.topic.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesSector =
      selectedSector === 'All Sectors' ||
      doc.sector === selectedSector ||
      (selectedSector === 'Cereals & Grains' && ['Rice', 'Wheat', 'Maize'].includes(doc.crop)) ||
      (selectedSector === 'Pulses & Oilseeds' &&
        ['Chickpea', 'Soybean', 'Groundnut', 'Mustard'].includes(doc.crop)) ||
      (selectedSector === 'Vegetables & Spices' &&
        ['Tomato', 'Potato', 'Chilli', 'Onion'].includes(doc.crop)) ||
      (selectedSector === 'Fruits & Plantation' &&
        ['Banana', 'Mango', 'Apple', 'Grapes', 'Pomegranate'].includes(doc.crop)) ||
      (selectedSector === 'Commercial & Cash Crops' &&
        ['Cotton', 'Sugarcane', 'Tea', 'Coffee'].includes(doc.crop));

    return matchesSearch && matchesSector;
  });

  const totalChunks = documents.reduce((sum, d) => sum + (d.indexed_chunks || 0), 0);

  const handleReindex = async () => {
    setIsReindexing(true);
    setReindexSuccessMessage(null);
    try {
      await onReindex();
      setReindexSuccessMessage('Re-index request completed.');
      setTimeout(() => setReindexSuccessMessage(null), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsReindexing(false);
    }
  };

  const handleInspect = async (doc: KnowledgeDocument) => {
    setInspectDoc(doc);
    setIsLoadingDetails(true);
    try {
      const res = await api.getKnowledgeDocDetails(doc.id);
      setInspectPopRecord((res.pop_record as PopRecord) || null);
    } catch (err) {
      console.error('Failed to load document details', err);
      setInspectPopRecord(null);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !title) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      fd.append('file', selectedFile);
      fd.append('title', title);
      fd.append('authority', authority);
      fd.append('crop', crop);
      fd.append('sector', sector);
      fd.append('topic', topic);
      await onUpload(fd);
      setIsUploadModalOpen(false);
      setTitle('');
      setSelectedFile(null);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="panel flex flex-col items-start justify-between gap-4 rounded-xl p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-lg border border-green-200 bg-green-50 p-1.5 text-green-800">
              <BookOpen className="h-5 w-5" />
            </span>
            <h2 className="text-xl font-semibold text-stone-900">Knowledge base</h2>
          </div>
          <p className="max-w-2xl text-xs text-stone-500">
            Indexed agricultural manuals and POP documents from the knowledge API.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReindex}
            disabled={isReindexing}
            className="flex items-center gap-1.5 rounded-lg border border-stone-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-stone-700 hover:bg-stone-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isReindexing ? 'animate-spin text-green-800' : ''}`} />
            {isReindexing ? 'Re-indexing…' : 'Re-index'}
          </button>
          <button
            type="button"
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-1.5 rounded-lg bg-green-900 px-4 py-2.5 text-xs font-bold text-white hover:bg-green-800"
          >
            <Upload className="h-4 w-4" />
            Upload document
          </button>
        </div>
      </div>

      {reindexSuccessMessage ? (
        <div className="flex items-center justify-between rounded-xl border border-green-200 bg-green-50 p-3.5 text-xs text-green-900">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{reindexSuccessMessage}</span>
          </div>
          <button type="button" onClick={() => setReindexSuccessMessage(null)}>✕</button>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        <div className="panel flex items-center gap-3 rounded-xl p-3.5">
          <div className="rounded-lg border border-green-200 bg-green-50 p-2.5 text-green-800">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase text-stone-500">Documents</p>
            <p className="font-mono text-lg font-bold text-stone-900">{documents.length}</p>
          </div>
        </div>
        <div className="panel flex items-center gap-3 rounded-xl p-3.5">
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-2.5 text-amber-800">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase text-stone-500">Indexed chunks</p>
            <p className="font-mono text-lg font-bold text-stone-900">{totalChunks}</p>
          </div>
        </div>
        <div className="panel flex items-center gap-3 rounded-xl p-3.5">
          <div className="rounded-lg border border-stone-200 bg-stone-50 p-2.5 text-stone-700">
            <Database className="h-4 w-4" />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase text-stone-500">Endpoint</p>
            <p className="text-sm font-bold text-stone-800">/api/v1/knowledge</p>
          </div>
        </div>
      </div>

      <div className="panel space-y-3 rounded-xl p-3">
        <div className="flex items-center gap-2">
          <Search className="ml-2 h-4 w-4 shrink-0 text-stone-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by crop, title, authority, or topic…"
            className="flex-1 bg-transparent text-xs text-stone-800 outline-none placeholder:text-stone-400"
          />
        </div>
        <div className="flex flex-wrap gap-1.5 border-t border-stone-100 pt-2">
          {SECTORS.map((sec) => (
            <button
              key={sec}
              type="button"
              onClick={() => setSelectedSector(sec)}
              className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
                selectedSector === sec
                  ? 'bg-green-900 text-white'
                  : 'border border-stone-200 bg-white text-stone-500 hover:text-stone-800'
              }`}
            >
              {sec}
            </button>
          ))}
        </div>
      </div>

      <div className="panel overflow-hidden rounded-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-stone-700">
            <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
              <tr>
                <th className="p-3.5">Title</th>
                <th className="p-3.5">Authority</th>
                <th className="p-3.5">Crop</th>
                <th className="p-3.5">Topic</th>
                <th className="p-3.5">Chunks</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7}>
                    <EmptyState title="No documents match filters" />
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-stone-50">
                    <td className="p-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="shrink-0 rounded-lg border border-green-200 bg-green-50 p-2 text-green-800">
                          <FileText className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="max-w-sm truncate font-bold text-stone-900">{doc.title}</p>
                          <span className="font-mono text-[10px] text-stone-400">
                            {doc.file_type} • {doc.language}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="p-3.5">
                      <p className="max-w-xs truncate font-medium text-stone-800">{doc.authority}</p>
                      <p className="truncate text-[10px] text-stone-400">{doc.source}</p>
                    </td>
                    <td className="p-3.5">
                      <span className="rounded border border-green-200 bg-green-50 px-2.5 py-0.5 font-bold text-green-900">
                        {doc.crop}
                      </span>
                    </td>
                    <td className="max-w-xs p-3.5 truncate text-stone-600">{doc.topic}</td>
                    <td className="p-3.5 font-mono font-bold text-stone-800">{doc.indexed_chunks}</td>
                    <td className="p-3.5">
                      <span className="inline-flex items-center gap-1 rounded border border-green-200 bg-green-50 px-2 py-0.5 text-[10px] font-bold text-green-900">
                        <CheckCircle2 className="h-3 w-3" /> {doc.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          onClick={() => handleInspect(doc)}
                          className="flex items-center gap-1 rounded-lg p-1.5 text-[11px] font-semibold text-green-900 hover:bg-green-50"
                        >
                          <Eye className="h-3.5 w-3.5" /> Inspect
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(doc.id)}
                          className="rounded-lg p-1.5 text-stone-400 hover:bg-red-50 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {inspectDoc ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/50 p-4 backdrop-blur-sm">
          <div className="panel max-h-[90vh] w-full max-w-3xl space-y-5 overflow-y-auto rounded-xl p-6">
            <div className="flex items-start justify-between border-b border-stone-200 pb-4">
              <div className="flex items-center gap-3">
                <div className="rounded-xl border border-green-200 bg-green-50 p-2.5 text-green-800">
                  <Sprout className="h-6 w-6" />
                </div>
                <div>
                  <span className="rounded border border-green-200 bg-green-50 px-2 py-0.5 text-[10px] font-bold text-green-900">
                    {inspectDoc.crop}
                  </span>
                  <h3 className="mt-0.5 text-lg font-semibold text-stone-900">{inspectDoc.title}</h3>
                </div>
              </div>
              <button type="button" onClick={() => setInspectDoc(null)} className="rounded-lg p-1.5 text-stone-400 hover:bg-stone-100 hover:text-stone-800">
                <X className="h-5 w-5" />
              </button>
            </div>

            {isLoadingDetails ? (
              <div className="flex flex-col items-center gap-2 py-12 text-stone-500">
                <RefreshCw className="h-6 w-6 animate-spin text-green-800" />
                <p className="text-xs">Loading document details…</p>
              </div>
            ) : inspectPopRecord ? (
              <div className="space-y-4 text-xs">
                <div className="rounded-xl border border-stone-200 bg-stone-50 p-3.5">
                  <div className="mb-1 flex items-center gap-2 font-semibold text-stone-700">
                    <Bug className="h-4 w-4 text-amber-700" />
                    Condition summary
                  </div>
                  <p className="leading-relaxed text-stone-600">
                    {inspectPopRecord.condition_summary || '—'}
                  </p>
                </div>

                {inspectPopRecord.pesticide ? (
                  <div className="space-y-3 rounded-xl border border-green-200 bg-green-50/60 p-4">
                    <div className="flex items-center gap-2 font-bold text-green-900">
                      <FlaskConical className="h-4 w-4" />
                      Chemical formulation
                    </div>
                    <div className="grid grid-cols-1 gap-3 rounded-lg border border-stone-200 bg-white p-3 sm:grid-cols-2">
                      <div>
                        <p className="text-[10px] font-semibold uppercase text-stone-500">Active ingredient</p>
                        <p className="text-xs font-bold text-stone-900">
                          {inspectPopRecord.pesticide.active_ingredient || '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-[10px] font-semibold uppercase text-stone-500">Dose</p>
                        <p className="font-mono text-sm font-bold text-green-900">
                          {inspectPopRecord.pesticide.exact_dose_per_liter || '—'}
                        </p>
                      </div>
                    </div>
                    {(inspectPopRecord.pesticide.safety_warnings || []).length > 0 ? (
                      <div className="space-y-1">
                        <p className="flex items-center gap-1 text-[10px] font-bold uppercase text-amber-800">
                          <AlertTriangle className="h-3 w-3" /> Safety warnings
                        </p>
                        <ul className="list-inside list-disc space-y-0.5 text-[11px] text-stone-600">
                          {inspectPopRecord.pesticide.safety_warnings!.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    ) : null}
                  </div>
                ) : null}

                {inspectPopRecord.monitoring ? (
                  <div className="space-y-2 rounded-xl border border-stone-200 bg-stone-50 p-3.5">
                    <p className="flex items-center gap-1.5 font-bold text-stone-800">
                      <Clock className="h-3.5 w-3.5 text-amber-700" />
                      Monitoring roadmap
                    </p>
                    <div className="grid grid-cols-2 gap-2 text-[10px] sm:grid-cols-4">
                      {(['day_1', 'day_3', 'day_7', 'day_14'] as const).map((key) => (
                        <div key={key} className="rounded border border-stone-200 bg-white p-2">
                          <span className="block font-bold text-green-900">{key.replace('_', ' ')}</span>
                          <span className="text-stone-600">{inspectPopRecord.monitoring?.[key] || '—'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="rounded-xl border border-stone-200 bg-stone-50 p-4 text-xs text-stone-500">
                Document chunked into {inspectDoc.indexed_chunks} vector chunks. No structured POP record attached.
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setInspectDoc(null)}
                className="rounded-xl bg-stone-100 px-5 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {isUploadModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/50 p-4 backdrop-blur-sm">
          <div className="panel w-full max-w-lg space-y-4 rounded-xl p-6">
            <div className="flex items-center justify-between border-b border-stone-200 pb-3">
              <h3 className="text-base font-semibold text-stone-900">Upload document</h3>
              <button type="button" onClick={() => setIsUploadModalOpen(false)} className="text-stone-400 hover:text-stone-800">
                ✕
              </button>
            </div>
            <form onSubmit={handleUploadSubmit} className="space-y-3">
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-600">Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full rounded-xl border border-stone-200 p-2.5 text-xs"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs font-semibold text-stone-600">Crop</label>
                  <select
                    value={crop}
                    onChange={(e) => setCrop(e.target.value)}
                    className="w-full rounded-xl border border-stone-200 p-2.5 text-xs"
                  >
                    {AVAILABLE_CROPS.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold text-stone-600">Sector</label>
                  <select
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    className="w-full rounded-xl border border-stone-200 p-2.5 text-xs"
                  >
                    {SECTORS.filter((s) => s !== 'All Sectors').map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-600">Authority</label>
                <input
                  type="text"
                  value={authority}
                  onChange={(e) => setAuthority(e.target.value)}
                  className="w-full rounded-xl border border-stone-200 p-2.5 text-xs"
                  required
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-600">Topic</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full rounded-xl border border-stone-200 p-2.5 text-xs"
                  required
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold text-stone-600">File</label>
                <input
                  type="file"
                  accept=".pdf,.txt,.docx,.csv"
                  onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])}
                  className="w-full rounded-xl border border-stone-200 p-2 text-xs"
                  required
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 rounded-xl bg-green-900 py-2.5 text-xs font-bold text-white hover:bg-green-800"
                >
                  {isSubmitting ? 'Uploading…' : 'Upload & index'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(false)}
                  className="rounded-xl bg-stone-100 px-4 py-2.5 text-xs font-semibold text-stone-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
};
