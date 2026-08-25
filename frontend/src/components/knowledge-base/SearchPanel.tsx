'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Search, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent } from '@/components/ui/Card';
import { useGenerateAnswer, useSearch } from '@/hooks/use-search';
import type { RagGenerateResponse, SearchResponse, SearchType } from '@/types';

type Mode = 'search' | 'ask';
const SEARCH_TYPES: SearchType[] = ['semantic', 'keyword', 'hybrid'];

export function SearchPanel({ knowledgeBaseId }: { knowledgeBaseId: string }) {
  const [mode, setMode] = useState<Mode>('ask');
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<SearchType>('hybrid');
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [answer, setAnswer] = useState<RagGenerateResponse | null>(null);

  const search = useSearch();
  const generate = useGenerateAnswer();
  const isPending = search.isPending || generate.isPending;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      if (mode === 'search') {
        setAnswer(null);
        setSearchResult(await search.mutateAsync({ query: query.trim(), knowledgeBaseId, searchType }));
      } else {
        setSearchResult(null);
        setAnswer(await generate.mutateAsync({ question: query.trim(), knowledgeBaseId, searchType }));
      }
    } catch {
      toast.error(mode === 'search' ? 'Search failed' : 'Failed to generate an answer');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          type="button"
          variant={mode === 'ask' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setMode('ask')}
        >
          <Sparkles className="mr-1.5 h-3.5 w-3.5" /> Ask
        </Button>
        <Button
          type="button"
          variant={mode === 'search' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setMode('search')}
        >
          <Search className="mr-1.5 h-3.5 w-3.5" /> Search
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            mode === 'ask' ? 'Ask a question about this knowledge base...' : 'Search chunks...'
          }
        />
        <Button type="submit" disabled={!query.trim() || isPending}>
          {isPending ? '...' : mode === 'ask' ? 'Ask' : 'Search'}
        </Button>
      </form>

      {mode === 'search' && (
        <div className="flex gap-3 text-xs text-muted-foreground">
          {SEARCH_TYPES.map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setSearchType(type)}
              className={searchType === type ? 'font-semibold text-foreground' : 'hover:text-foreground'}
            >
              {type}
            </button>
          ))}
        </div>
      )}

      {answer && (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <p className="text-sm">{answer.answer}</p>
            {answer.citations.length > 0 && (
              <div className="space-y-1 border-t pt-3">
                <p className="text-xs font-medium text-muted-foreground">Sources</p>
                {answer.citations.map((c, i) => (
                  <p key={i} className="text-xs text-muted-foreground">
                    [{i + 1}] {c.filename} — &ldquo;{c.textSnippet}&rdquo;
                  </p>
                ))}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              Confidence {(answer.confidence * 100).toFixed(0)}% ·{' '}
              {(answer.processingTimeMs / 1000).toFixed(1)}s
            </p>
          </CardContent>
        </Card>
      )}

      {searchResult && (
        <div className="space-y-2">
          {searchResult.results.length === 0 && (
            <p className="text-sm text-muted-foreground">No results found.</p>
          )}
          {searchResult.results.map((r) => (
            <Card key={r.chunkId}>
              <CardContent className="space-y-1 pt-4">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium text-muted-foreground">{r.filename}</p>
                  <p className="text-xs text-muted-foreground">{(r.score * 100).toFixed(0)}%</p>
                </div>
                <p className="text-sm">{r.content}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
