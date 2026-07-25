# 15 — UI/UX Specification

## Design System

### Framework
- **Next.js 14** (App Router) with React Server Components
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** for accessible, customizable components
- **Lucide Icons** for iconography
- **Zustand** for client-side state
- **React Query (TanStack Query)** for server state

### Color Tokens (CSS Variables)

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --border: 214.3 31.8% 91.4%;
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  /* ... */
}
```

## Page Structure

```
/                           Landing / Dashboard
/login                      Authentication
/register                   Registration
/dashboard                  Main dashboard
/knowledge-bases            List knowledge bases
/knowledge-bases/[id]       Knowledge base detail
/knowledge-bases/[id]/documents   Document list
/agents                     List agents
/agents/[id]                Agent detail & chat
/agents/[id]/configure      Agent configuration
/conversations              Conversation history
/conversations/[id]         Conversation thread
/mcp                        MCP server management
/admin/users                User management (admin)
/admin/audit-logs           Audit log viewer (admin)
/admin/settings             System settings (admin)
/evaluations                Evaluation dashboard
/settings                   User settings
```

## Key Components

### Chat Interface

```tsx
// frontend/src/components/chat/ChatContainer.tsx
<ChatContainer>
  <ChatHeader agent={agent} />
  <ChatMessages>
    {messages.map(msg => (
      <ChatMessage
        key={msg.id}
        role={msg.role}
        content={msg.content}
        citations={msg.citations}
        toolCalls={msg.toolCalls}
      />
    ))}
  </ChatMessages>
  <ChatInput
    onSend={handleSend}
    onAttach={handleAttach}
    isStreaming={isStreaming}
  />
</ChatContainer>
```

### Agent Step Visualization

```tsx
// Shows agent's reasoning steps in real-time
<AgentSteps>
  {steps.map(step => (
    <AgentStep
      key={step.id}
      type={step.type} // 'thought' | 'action' | 'observation'
      content={step.content}
      tool={step.tool}
      status={step.status} // 'running' | 'done' | 'error'
    />
  ))}
</AgentSteps>
```

### Knowledge Base Explorer

```tsx
<KnowledgeBaseExplorer>
  <KBSidebar>
    <KBSearchBar />
    <KBDocumentList documents={documents} />
  </KBSidebar>
  <KBMain>
    <DocumentViewer document={selectedDoc} chunks={chunks} />
  </KBMain>
</KnowledgeBaseExplorer>
```

### Document Upload

```tsx
<DocumentUpload
  knowledgeBaseId={kbId}
  onUploadComplete={handleUploadComplete}
  accept=".pdf,.md,.txt,.html,.csv,.json"
  maxSize={50 * 1024 * 1024} // 50MB
  multiple
>
  <DropZone>
    <UploadIcon />
    <p>Drag & drop files or click to browse</p>
  </DropZone>
  <UploadProgress files={uploading} />
  <UploadedFiles files={uploaded} />
</DocumentUpload>
```

## Responsive Breakpoints

```css
/* Tailwind defaults */
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
2xl: 1536px  /* Extra large */
```

## Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation for all interactive elements
- Screen reader support with ARIA labels
- Focus management in modals and dialogs
- Color contrast ratios ≥ 4.5:1 (normal text)
- Reduced motion support

## Loading States

| State       | UI Treatment                          |
|-------------|---------------------------------------|
| Loading     | Skeleton screens, not spinners        |
| Streaming   | Typewriter effect with cursor         |
| Empty       | Illustrated empty state with CTA      |
| Error       | Toast notification + inline message   |
| Optimistic  | Immediate UI update, revert on error  |

## Toast Notifications

```tsx
// Using shadcn/ui Sonner
import { toast } from 'sonner';

toast.success('Document uploaded successfully');
toast.error('Failed to process document');
toast.promise(uploadPromise, {
  loading: 'Uploading document...',
  success: 'Document ready',
  error: 'Upload failed',
});
```
