'use client';

import { useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';
import { ProtectedRoute } from '@/components/shared/ProtectedRoute';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { useCreateKnowledgeBase, useKnowledgeBases } from '@/hooks/use-knowledge-bases';

function errorMessage(error: unknown, fallback: string) {
  if (error && typeof error === 'object' && 'response' in error) {
    const resp = (error as { response?: { data?: { error?: { message?: string } } } }).response;
    return resp?.data?.error?.message || fallback;
  }
  return fallback;
}

export default function KnowledgeBasesPage() {
  return (
    <ProtectedRoute>
      <div className="container max-w-4xl py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Bases</h1>
            <p className="mt-1 text-muted-foreground">
              Collections of documents your agents and searches can draw on.
            </p>
          </div>
        </div>

        <CreateKnowledgeBaseCard />
        <KnowledgeBaseList />
      </div>
    </ProtectedRoute>
  );
}

function CreateKnowledgeBaseCard() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const createKb = useCreateKnowledgeBase();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await createKb.mutateAsync({ name: name.trim(), description: description.trim() || undefined });
      toast.success('Knowledge base created');
      setName('');
      setDescription('');
      setOpen(false);
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to create knowledge base'));
    }
  };

  if (!open) {
    return (
      <Button className="mb-6" onClick={() => setOpen(true)}>
        + New Knowledge Base
      </Button>
    );
  }

  return (
    <Card className="mb-6">
      <form onSubmit={handleSubmit}>
        <CardHeader>
          <CardTitle className="text-lg">New Knowledge Base</CardTitle>
          <CardDescription>Give it a name — you can add documents next.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="kb-name">Name</Label>
            <Input
              id="kb-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Product Documentation"
              autoFocus
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="kb-description">Description (optional)</Label>
            <Input
              id="kb-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What is this knowledge base for?"
            />
          </div>
        </CardContent>
        <CardFooter className="gap-2">
          <Button type="submit" disabled={!name.trim() || createKb.isPending}>
            {createKb.isPending ? 'Creating...' : 'Create'}
          </Button>
          <Button type="button" variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

function KnowledgeBaseList() {
  const { data: knowledgeBases, isLoading, isError } = useKnowledgeBases();

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading knowledge bases...</p>;
  }

  if (isError) {
    return <p className="text-sm text-destructive">Failed to load knowledge bases.</p>;
  }

  if (!knowledgeBases || knowledgeBases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No knowledge bases yet. Create one to start uploading documents.
      </p>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {knowledgeBases.map((kb) => (
        <Link key={kb.id} href={`/knowledge-bases/${kb.id}`}>
          <Card className="h-full transition-colors hover:border-primary">
            <CardHeader>
              <CardTitle className="text-lg">{kb.name}</CardTitle>
              {kb.description && <CardDescription>{kb.description}</CardDescription>}
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {kb.embeddingModel} · chunk {kb.chunkSize}/{kb.chunkOverlap}
              </p>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
