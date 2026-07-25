# 17 — Testing Strategy

## Testing Pyramid

```
       ┌─────────┐
       │   E2E   │   Playwright (critical flows)
       │   ~10%   │
      ┌─┴─────────┴─┐
      │ Integration │   API tests, DB tests, service integration
      │    ~30%      │
     ┌─┴─────────────┴─┐
     │    Unit Tests    │   Functions, classes, components
     │      ~60%        │
     └──────────────────┘
```

## Frontend Testing (Next.js)

### Unit Tests — Vitest + React Testing Library

```typescript
// frontend/src/components/chat/__tests__/ChatMessage.test.tsx
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '../ChatMessage';

describe('ChatMessage', () => {
  it('renders user message correctly', () => {
    render(<ChatMessage role="user" content="Hello" />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
  
  it('renders assistant message with citations', () => {
    const citations = [{ document_id: '1', filename: 'doc.pdf', text_snippet: '...' }];
    render(<ChatMessage role="assistant" content="Answer" citations={citations} />);
    expect(screen.getByText('[1]')).toBeInTheDocument();
  });
  
  it('handles tool call display', () => {
    const toolCalls = [{ name: 'search', args: { query: 'test' }, result: 'found' }];
    render(<ChatMessage role="assistant" content="" toolCalls={toolCalls} />);
    expect(screen.getByText('search')).toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
// frontend/src/app/__tests__/chat-flow.test.tsx
describe('Chat Flow', () => {
  it('sends message and receives streaming response', async () => {
    const { user } = render(<ChatPage agentId="agent-1" />);
    
    await user.type(screen.getByRole('textbox'), 'What is RAG?');
    await user.click(screen.getByRole('button', { name: /send/i }));
    
    // Loading state
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
    
    // Wait for response
    await waitFor(() => {
      expect(screen.getByText(/RAG stands for/)).toBeInTheDocument();
    });
  });
});
```

### E2E Tests — Playwright

```typescript
// e2e/auth.spec.ts
test('user can register and login', async ({ page }) => {
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'TestPass123!');
  await page.fill('[name="confirmPassword"]', 'TestPass123!');
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();
});

test('user can create knowledge base and upload document', async ({ page }) => {
  await loginAsUser(page, 'editor');
  await page.goto('/knowledge-bases');
  await page.click('text=New Knowledge Base');
  await page.fill('[name="name"]', 'Test KB');
  await page.click('button:has-text("Create")');
  
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('./fixtures/test-doc.pdf');
  await expect(page.getByText('test-doc.pdf')).toBeVisible();
});
```

## Backend Testing (NestJS)

### Unit Tests — Jest

```typescript
// gateway/src/auth/__tests__/auth.service.spec.ts
describe('AuthService', () => {
  let service: AuthService;
  let userRepo: MockRepository<User>;
  
  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: getRepositoryToken(User), useClass: MockRepository },
        { provide: JwtService, useValue: mockJwtService },
      ],
    }).compile();
    
    service = module.get(AuthService);
  });
  
  describe('register', () => {
    it('should create a new user', async () => {
      const dto = { email: 'test@test.com', password: 'Test1234!@' };
      const result = await service.register(dto);
      expect(result.email).toBe(dto.email);
      expect(result.passwordHash).not.toBe(dto.password);
    });
    
    it('should throw on duplicate email', async () => {
      userRepo.findOne.mockResolvedValue({ id: '1' });
      await expect(service.register({ email: 'a@b.com', password: 'Test1234!@' }))
        .rejects.toThrow(ConflictException);
    });
  });
});
```

### E2E Tests — Supertest

```typescript
// gateway/test/auth.e2e-spec.ts
describe('Auth (e2e)', () => {
  let app: INestApplication;
  
  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();
    app = module.createNestApplication();
    await app.init();
  });
  
  it('/auth/register (POST)', () => {
    return request(app.getHttpServer())
      .post('/api/v1/auth/register')
      .send({ email: 'e2e@test.com', password: 'TestPass123!' })
      .expect(201)
      .expect(res => {
        expect(res.body.success).toBe(true);
        expect(res.body.data.accessToken).toBeDefined();
      });
  });
});
```

## AI Backend Testing (Python)

### Unit Tests — Pytest

```python
# ai-backend/tests/rag/test_chunker.py
import pytest
from app.rag.chunker import RecursiveChunker

class TestRecursiveChunker:
    @pytest.fixture
    def chunker(self):
        return RecursiveChunker(chunk_size=100, chunk_overlap=20)
    
    def test_splits_long_text(self, chunker):
        text = "A" * 250
        chunks = chunker.split(text)
        assert len(chunks) == 3
        assert all(len(c) <= 100 for c in chunks)
    
    def test_preserves_sentence_boundaries(self, chunker):
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.split(text)
        # Should not split mid-sentence if possible
        assert all(c.endswith('.') for c in chunks[:-1])
    
    def test_handles_empty_text(self, chunker):
        assert chunker.split("") == []
```

### Integration Tests

```python
# ai-backend/tests/rag/test_rag_pipeline.py
@pytest.mark.integration
async def test_rag_search_and_generate(db_session, embedding_model):
    # Setup: ingest a document
    pipeline = RAGPipeline(db_session, embedding_model)
    doc = await pipeline.ingest(test_document)
    
    # Execute: search and generate
    response = await pipeline.query("What is the main topic?")
    
    # Assert
    assert response.answer is not None
    assert len(response.citations) > 0
    assert response.confidence > 0.5
```

### Agent Tests

```python
# ai-backend/tests/agent/test_agent_graph.py
@pytest.mark.asyncio
async def test_agent_completes_simple_task(mock_llm, test_tools):
    agent = create_test_agent(mock_llm, test_tools)
    result = await agent.run("What is 2 + 2?")
    assert "4" in result.output
    assert result.steps <= 3  # Should be efficient
```

## Coverage Targets

| Layer        | Line Coverage | Branch Coverage |
|-------------|---------------|-----------------|
| Frontend     | 80%           | 70%             |
| Gateway      | 85%           | 75%             |
| AI Backend   | 85%           | 75%             |
| Shared Libs  | 90%           | 85%             |

## CI Pipeline

```yaml
# .github/workflows/test.yml
jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run lint && npm run type-check && npm test -- --coverage
  
  gateway:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd gateway && npm ci && npm run lint && npm run test -- --coverage
  
  ai-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd ai-backend && poetry install && poetry run ruff check . && poetry run pytest --cov
  
  e2e:
    needs: [frontend, gateway, ai-backend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d
      - run: cd e2e && npm ci && npx playwright test
      - run: docker compose down
```
