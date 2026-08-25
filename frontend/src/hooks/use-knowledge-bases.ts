'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { del, get, patch, post } from '@/lib/api';
import type { KnowledgeBase } from '@/types';

export function useKnowledgeBases() {
  return useQuery({
    queryKey: ['knowledge-bases'],
    queryFn: () => get<KnowledgeBase[]>('/knowledge-bases'),
  });
}

export function useKnowledgeBase(id: string) {
  return useQuery({
    queryKey: ['knowledge-bases', id],
    queryFn: () => get<KnowledgeBase>(`/knowledge-bases/${id}`),
    enabled: !!id,
  });
}

export function useCreateKnowledgeBase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { name: string; description?: string }) =>
      post<KnowledgeBase>('/knowledge-bases', input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] });
    },
  });
}

export function useUpdateKnowledgeBase(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { name?: string; description?: string }) =>
      patch<KnowledgeBase>(`/knowledge-bases/${id}`, input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] });
      void queryClient.invalidateQueries({ queryKey: ['knowledge-bases', id] });
    },
  });
}

export function useDeleteKnowledgeBase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => del(`/knowledge-bases/${id}`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] });
    },
  });
}
