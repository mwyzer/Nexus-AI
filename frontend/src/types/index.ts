export interface User {
  id: string;
  email: string;
  displayName: string;
  roles: string[];
  isActive: boolean;
  createdAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  displayName: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: ApiError | null;
  meta?: PaginationMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Array<{ field: string; message: string }>;
}

export interface PaginationMeta {
  page: number;
  perPage: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PaginationMeta;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string | null;
  ownerId: string | null;
  embeddingModel: string;
  chunkSize: number;
  chunkOverlap: number;
  createdAt: string;
  updatedAt: string;
}

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'error';

export interface KnowledgeDocument {
  id: string;
  knowledgeBaseId: string;
  filename: string;
  mimeType: string | null;
  fileSize: number | null;
  status: DocumentStatus;
  errorMessage: string | null;
  docMetadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentUploadResponse {
  document: KnowledgeDocument;
  taskId: string;
}

export type SearchType = 'semantic' | 'keyword' | 'hybrid';

export interface SearchResultItem {
  chunkId: string;
  documentId: string;
  filename: string;
  content: string;
  chunkIndex: number;
  score: number;
}

export interface SearchResponse {
  results: SearchResultItem[];
  query: string;
  searchType: string;
}

export interface Citation {
  documentId: string;
  filename: string;
  chunkIndex: number;
  textSnippet: string;
  relevanceScore: number;
}

export interface RagGenerateResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  processingTimeMs: number;
}
