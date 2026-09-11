import React, { useState } from 'react';
import { UserCheck } from 'lucide-react';
import type { ExpertValidationCase } from '../../types';
import { EmptyState } from '../ui/States';

interface ValidationQueueProps {
  queue: ExpertValidationCase[];
  onReview: (
    id: string,
    review: { status: string; confirmed_disease?: string; expert_notes: string }
  ) => Promise<void>;
}

export const ValidationQueue: React.FC<ValidationQueueProps> = ({ queue, onReview }) => {
  const [selectedCase, setSelectedCase] = useState<ExpertValidationCase | null>(null);
  const [confirmedDisease, setConfirmedDisease] = useState('');
  const [expertNotes, setExpertNotes] = useState('');
  const [reviewStatus, setReviewStatus] = useState('CONFIRMED');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenReview = (item: ExpertValidationCase) => {
    setSelectedCase(item);
    setConfirmedDisease(item.confirmed_disease || item.ai_predicted_disease);
    setExpertNotes(item.expert_notes || '');
    setReviewStatus(item.status === 'PENDING' ? 'CONFIRMED' : item.status);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase) return;
    setIsSubmitting(true);
    try {
      await onReview(selectedCase.id, {
        status: reviewStatus,
        confirmed_disease: confirmedDisease,
        expert_notes: expertNotes,
      });
      setSelectedCase(null);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const pendingCount = queue.filter((q) => q.status === 'PENDING').length;

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6">
      <div className="panel flex items-center justify-between rounded-xl p-6">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-lg border border-green-200 bg-green-50 p-1.5 text-green-800">
              <UserCheck className="h-4 w-4" />
            </span>
            <h2 className="text-xl font-semibold text-stone-900">Expert validation queue</h2>
          </div>
          <p className="text-xs text-stone-500">
            Review flagged AI diagnoses and record ground-truth outcomes.
          </p>
        </div>
        <span className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-bold text-amber-900">
          {pendingCount} pending
        </span>
      </div>

      <div className="panel overflow-hidden rounded-xl">
        {queue.length === 0 ? (
          <EmptyState
            title="Queue is empty"
            detail="No validation cases returned from /api/v1/validation/queue."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-stone-700">
              <thead className="border-b border-stone-200 bg-stone-50 text-[10px] uppercase tracking-wider text-stone-500">
                <tr>
                  <th className="p-3.5">Case / Farmer</th>
                  <th className="p-3.5">Crop</th>
                  <th className="p-3.5">AI prediction</th>
                  <th className="p-3.5">Notes</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {queue.map((item) => (
                  <tr key={item.id} className="hover:bg-stone-50">
                    <td className="p-3.5">
                      <p className="font-bold text-stone-900">{item.farmer_name}</p>
                      <p className="text-[11px] text-stone-500">
                        {item.district}, {item.state}
                      </p>
                      <p className="font-mono text-[10px] text-stone-400">{item.id}</p>
                    </td>
                    <td className="p-3.5 font-bold text-green-900">{item.crop}</td>
                    <td className="p-3.5">
                      <p className="font-semibold text-stone-800">{item.ai_predicted_disease}</p>
                      <span className="text-[10px] text-stone-500">
                        Confidence: {Math.round(item.ai_confidence * 100)}% • {item.ai_risk_level}
                      </span>
                    </td>
                    <td className="max-w-xs p-3.5">
                      <p className="line-clamp-2 italic text-stone-500">
                        {item.farmer_notes ? `"${item.farmer_notes}"` : '—'}
                      </p>
                    </td>
                    <td className="p-3.5">
                      <span className="rounded border border-stone-200 bg-stone-50 px-2.5 py-0.5 text-[10px] font-bold text-stone-700">
                        {item.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        type="button"
                        onClick={() => handleOpenReview(item)}
                        className="rounded-lg border border-green-200 bg-green-50 px-3 py-1.5 text-xs font-bold text-green-900 hover:bg-green-900 hover:text-white"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedCase ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/50 p-4 backdrop-blur-sm">
          <div className="panel max-h-[90vh] w-full max-w-2xl space-y-4 overflow-y-auto rounded-xl p-6">
            <div className="flex items-center justify-between border-b border-stone-200 pb-3">
              <div>
                <h3 className="text-base font-semibold text-stone-900">Ground-truth review</h3>
                <p className="text-xs text-stone-500">
                  Case {selectedCase.id} • {selectedCase.farmer_name}
                </p>
              </div>
              <button type="button" onClick={() => setSelectedCase(null)} className="text-stone-400 hover:text-stone-800">
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <span className="block text-xs font-semibold text-stone-500">Field specimen</span>
                {selectedCase.image_url ? (
                  <img
                    src={selectedCase.image_url}
                    alt="Field sample"
                    className="h-52 w-full rounded-xl border border-stone-200 object-cover"
                  />
                ) : (
                  <div className="flex h-52 items-center justify-center rounded-xl border border-dashed border-stone-300 text-xs text-stone-400">
                    No image URL
                  </div>
                )}
              </div>

              <form onSubmit={handleSubmit} className="space-y-3">
                <div>
                  <label className="mb-1 block text-xs font-semibold text-stone-600">Status</label>
                  <select
                    value={reviewStatus}
                    onChange={(e) => setReviewStatus(e.target.value)}
                    className="w-full rounded-lg border border-stone-200 bg-white p-2.5 text-xs"
                  >
                    <option value="CONFIRMED">CONFIRMED</option>
                    <option value="CORRECTED">CORRECTED</option>
                    <option value="REJECTED">REJECTED</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold text-stone-600">Verified disease</label>
                  <input
                    type="text"
                    value={confirmedDisease}
                    onChange={(e) => setConfirmedDisease(e.target.value)}
                    className="w-full rounded-lg border border-stone-200 bg-white p-2.5 text-xs"
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold text-stone-600">Expert notes</label>
                  <textarea
                    rows={4}
                    value={expertNotes}
                    onChange={(e) => setExpertNotes(e.target.value)}
                    className="w-full rounded-lg border border-stone-200 bg-white p-2.5 text-xs"
                    required
                  />
                </div>
                <div className="flex gap-2 pt-2">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 rounded-lg bg-green-900 py-2.5 text-xs font-bold text-white hover:bg-green-800"
                  >
                    {isSubmitting ? 'Saving…' : 'Save review'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedCase(null)}
                    className="rounded-lg bg-stone-100 px-4 py-2.5 text-xs font-semibold text-stone-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
