'use client';

import { useMutation } from '@tanstack/react-query';
import { post } from '@/lib/api';
import type { RagGenerateResponse, SearchResponse, SearchType } from '@/types';

export function useSearch() {
  return useMutation({
    mutationFn: (input: { query: string; knowledgeBaseId: string; searchType?: SearchType }) =>
      post<SearchResponse>('/search', input),
  });
}

export function useGenerateAnswer() {
  return useMutation({
    mutationFn: (input: { question: string; knowledgeBaseId: string; searchType?: SearchType }) =>
      post<RagGenerateResponse>('/rag/generate', input),
  });
}
