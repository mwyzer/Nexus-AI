'use client';

import { useRef, useState } from 'react';
import { toast } from 'sonner';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUploadDocument } from '@/hooks/use-documents';

const ACCEPTED_TYPES = ['application/pdf', 'text/markdown', 'text/plain', 'text/html'];

function errorMessage(error: unknown, fallback: string) {
  if (error && typeof error === 'object' && 'response' in error) {
    const resp = (error as { response?: { data?: { error?: { message?: string } } } }).response;
    return resp?.data?.error?.message || fallback;
  }
  return fallback;
}

export function DocumentUpload({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const upload = useUploadDocument(knowledgeBaseId);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!ACCEPTED_TYPES.includes(file.type)) {
      toast.error(`Unsupported file type: ${file.type || 'unknown'}`);
      return;
    }

    try {
      await upload.mutateAsync(file);
      toast.success(`${file.name} uploaded — processing...`);
    } catch (error) {
      toast.error(errorMessage(error, 'Upload failed'));
    } finally {
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        void handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      className={cn(
        'flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors',
        isDragging ? 'border-primary bg-primary/5' : 'border-input',
        upload.isPending && 'pointer-events-none opacity-60',
      )}
    >
      <UploadCloud className="mb-2 h-8 w-8 text-muted-foreground" />
      <p className="text-sm font-medium">
        {upload.isPending ? 'Uploading...' : 'Drag & drop a file, or click to browse'}
      </p>
      <p className="mt-1 text-xs text-muted-foreground">PDF, Markdown, plain text, or HTML</p>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.md,.txt,.html,application/pdf,text/markdown,text/plain,text/html"
        className="hidden"
        onChange={(e) => void handleFiles(e.target.files)}
      />
    </div>
  );
}
