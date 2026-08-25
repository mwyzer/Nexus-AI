'use client';

import Link from 'next/link';
import { ProtectedRoute } from '@/components/shared/ProtectedRoute';
import { useAuth } from '@/hooks/use-auth';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Welcome back, {user?.displayName || 'User'}
        </p>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Link href="/knowledge-bases" className="rounded-lg border p-6 transition-colors hover:border-primary">
            <h3 className="font-semibold">Knowledge Bases</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Manage your knowledge repositories
            </p>
          </Link>
          <div className="rounded-lg border p-6">
            <h3 className="font-semibold">Agents</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Configure and run AI agents
            </p>
          </div>
          <div className="rounded-lg border p-6">
            <h3 className="font-semibold">Conversations</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              View your conversation history
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
