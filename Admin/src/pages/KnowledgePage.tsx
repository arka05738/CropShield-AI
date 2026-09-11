import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { KnowledgeDocument } from '../types';
import { KnowledgeBaseAdmin } from '../components/admin/KnowledgeBaseAdmin';
import { ErrorState, LoadingState, PageHeader } from '../components/ui/States';

export function KnowledgePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const docs = await api.getKnowledgeDocs();
      setDocuments(docs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div>
      <PageHeader title="Knowledge" description="Documents from GET /api/v1/knowledge" />
      {loading ? <LoadingState /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error ? (
        <KnowledgeBaseAdmin
          documents={documents}
          onUpload={async (fd) => {
            await api.uploadKnowledgeDoc(fd);
            await load();
          }}
          onDelete={async (id) => {
            await api.deleteKnowledgeDoc(id);
            await load();
          }}
          onReindex={async () => {
            await api.reindexKnowledge();
            await load();
          }}
        />
      ) : null}
    </div>
  );
}
