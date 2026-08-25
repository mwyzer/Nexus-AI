'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { del, get, postForm } from '@/lib/api';
import type { DocumentUploadResponse, KnowledgeDocument } from '@/types';

export function useDocuments(knowledgeBaseId: string) {
  return useQuery({
    queryKey: ['documents', knowledgeBaseId],
    queryFn: () => get<KnowledgeDocument[]>('/documents', { knowledgeBaseId }),
    enabled: !!knowledgeBaseId,
    refetchInterval: (query) => {
      const docs = query.state.data as KnowledgeDocument[] | undefined;
      const hasPending = docs?.some((d) => d.status === 'pending' || d.status === 'processing');
      return hasPending ? 2000 : false;
    },
  });
}

export function useUploadDocument(knowledgeBaseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('knowledgeBaseId', knowledgeBaseId);
      formData.append('file', file);
      return postForm<DocumentUploadResponse>('/documents', formData);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['documents', knowledgeBaseId] });
    },
  });
}

export function useDeleteDocument(knowledgeBaseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => del(`/documents/${id}`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['documents', knowledgeBaseId] });
    },
  });
}
