'use client';

import { toast } from 'sonner';
import { FileText, Trash2 } from 'lucide-react';
import { useDeleteDocument, useDocuments } from '@/hooks/use-documents';
import { Button } from '@/components/ui/Button';
import type { DocumentStatus } from '@/types';

const STATUS_STYLES: Record<DocumentStatus, string> = {
  pending: 'bg-muted text-muted-foreground',
  processing: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300',
  ready: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300',
  error: 'bg-destructive/10 text-destructive',
};

function formatFileSize(bytes: number | null) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentList({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const { data: documents, isLoading } = useDocuments(knowledgeBaseId);
  const deleteDoc = useDeleteDocument(knowledgeBaseId);

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading documents...</p>;
  }

  if (!documents || documents.length === 0) {
    return <p className="text-sm text-muted-foreground">No documents uploaded yet.</p>;
  }

  const handleDelete = async (id: string, filename: string) => {
    try {
      await deleteDoc.mutateAsync(id);
      toast.success(`${filename} deleted`);
    } catch {
      toast.error('Failed to delete document');
    }
  };

  return (
    <ul className="divide-y rounded-lg border">
      {documents.map((doc) => (
        <li key={doc.id} className="flex items-center justify-between gap-4 p-4">
          <div className="flex min-w-0 items-center gap-3">
            <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{doc.filename}</p>
              <p className="truncate text-xs text-muted-foreground">
                {formatFileSize(doc.fileSize)}
                {doc.status === 'error' && doc.errorMessage ? ` · ${doc.errorMessage}` : ''}
              </p>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[doc.status]}`}
            >
              {doc.status}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => void handleDelete(doc.id, doc.filename)}
              disabled={deleteDoc.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </li>
      ))}
    </ul>
  );
}
