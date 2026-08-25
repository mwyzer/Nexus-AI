'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ProtectedRoute } from '@/components/shared/ProtectedRoute';
import { useKnowledgeBase } from '@/hooks/use-knowledge-bases';
import { DocumentUpload } from '@/components/knowledge-base/DocumentUpload';
import { DocumentList } from '@/components/knowledge-base/DocumentList';
import { SearchPanel } from '@/components/knowledge-base/SearchPanel';

export default function KnowledgeBaseDetailPage() {
  const params = useParams<{ id: string }>();
  const knowledgeBaseId = params.id;
  const { data: kb, isLoading, isError } = useKnowledgeBase(knowledgeBaseId);

  return (
    <ProtectedRoute>
      <div className="container max-w-4xl py-8">
        <Link
          href="/knowledge-bases"
          className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Knowledge Bases
        </Link>

        {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
        {isError && <p className="text-sm text-destructive">Failed to load knowledge base.</p>}

        {kb && (
          <>
            <h1 className="text-3xl font-bold">{kb.name}</h1>
            {kb.description && <p className="mt-1 text-muted-foreground">{kb.description}</p>}
            <p className="mt-1 text-xs text-muted-foreground">
              {kb.embeddingModel} embeddings · chunk size {kb.chunkSize} / overlap {kb.chunkOverlap}
            </p>

            <div className="mt-8 space-y-8">
              <section>
                <h2 className="mb-3 text-lg font-semibold">Documents</h2>
                <div className="space-y-4">
                  <DocumentUpload knowledgeBaseId={knowledgeBaseId} />
                  <DocumentList knowledgeBaseId={knowledgeBaseId} />
                </div>
              </section>

              <section>
                <h2 className="mb-3 text-lg font-semibold">Ask &amp; Search</h2>
                <SearchPanel knowledgeBaseId={knowledgeBaseId} />
              </section>
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}
