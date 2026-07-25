# Prompt: Frontend Development

Use this prompt when implementing Next.js frontend features.

---

## Instructions

### Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI primitives)
- **State**: Zustand (client), React Query / TanStack Query (server)
- **Forms**: React Hook Form + Zod
- **Real-time**: Socket.IO client
- **Icons**: Lucide React
- **Testing**: Vitest + React Testing Library + Playwright (E2E)

### Component Patterns

#### Page Layout
```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        {children}
      </main>
    </div>
  );
}
```

#### Data Fetching with React Query
```tsx
// hooks/use-knowledge-bases.ts
export function useKnowledgeBases(page: number) {
  return useQuery({
    queryKey: ['knowledge-bases', page],
    queryFn: () => api.get(`/knowledge-bases?page=${page}`),
  });
}

// In component
function KnowledgeBaseList() {
  const { data, isLoading, error } = useKnowledgeBases(1);
  
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorState error={error} />;
  
  return data.items.map(kb => <KnowledgeBaseCard key={kb.id} kb={kb} />);
}
```

#### Mutation with Optimistic Updates
```tsx
const mutation = useMutation({
  mutationFn: (data: CreateKbDto) => api.post('/knowledge-bases', data),
  onMutate: async (newKb) => {
    await queryClient.cancelQueries({ queryKey: ['knowledge-bases'] });
    const previous = queryClient.getQueryData(['knowledge-bases']);
    queryClient.setQueryData(['knowledge-bases'], (old) => ({
      ...old, items: [...old.items, { id: 'temp', ...newKb }],
    }));
    return { previous };
  },
  onError: (err, newKb, context) => {
    queryClient.setQueryData(['knowledge-bases'], context.previous);
    toast.error('Failed to create knowledge base');
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['knowledge-bases'] });
  },
});
```

#### Auth Store (Zustand)
```tsx
// stores/auth-store.ts
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}
```

#### Socket.IO Hook
```tsx
// hooks/use-socket.ts
export function useSocket() {
  const socket = useMemo(() => io(WS_URL, {
    auth: { token: useAuthStore.getState().accessToken },
  }), []);
  
  useEffect(() => {
    return () => { socket.disconnect(); };
  }, [socket]);
  
  return socket;
}
```

### Key Rules
- Use React Server Components by default, `'use client'` only when needed
- Use `next/image` for all images
- Implement loading states with skeleton screens
- Implement error boundaries for graceful error handling
- Use semantic HTML and ARIA attributes
- Support dark mode via Tailwind `dark:` classes
- Mobile-first responsive design
- All user-facing strings should support i18n
- Use Zod schemas for form validation
- Never expose API keys or secrets in client code
