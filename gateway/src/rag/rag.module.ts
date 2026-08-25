import { Module } from '@nestjs/common';
import { AiBackendClient } from './ai-backend-client.service';
import { DocumentsController } from './documents.controller';
import { KnowledgeBasesController } from './knowledge-bases.controller';
import { RagController } from './rag.controller';
import { SearchController } from './search.controller';

@Module({
  controllers: [KnowledgeBasesController, DocumentsController, SearchController, RagController],
  providers: [AiBackendClient],
})
export class RagModule {}
