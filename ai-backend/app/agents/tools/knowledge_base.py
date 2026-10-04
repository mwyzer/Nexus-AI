from uuid import UUID

from pydantic import BaseModel, Field

from ...core.database import async_session
from ...models.knowledge_base import KnowledgeBase
from ...rag import vector_store
from ...rag.embedding import get_embedder, infer_embedding_provider
from .base import Tool, ToolError


class KnowledgeBaseSearchArgs(BaseModel):
    knowledge_base_id: str = Field(description="UUID of the knowledge base to search")
    query: str = Field(description="Search query text")
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeBaseSearchTool(Tool):
    name = "knowledge_base_search"
    description = "Search a Nexus AI knowledge base for relevant document chunks"
    args_schema = KnowledgeBaseSearchArgs

    async def run(self, args: KnowledgeBaseSearchArgs) -> str:
        try:
            kb_id = UUID(args.knowledge_base_id)
        except ValueError as exc:
            raise ToolError(f"Invalid knowledge_base_id: {args.knowledge_base_id!r}") from exc

        async with async_session() as session:
            kb = await session.get(KnowledgeBase, kb_id)
            if kb is None:
                raise ToolError(f"Knowledge base not found: {kb_id}")

            provider = infer_embedding_provider(kb.embedding_model)
            embedder = get_embedder(provider, kb.embedding_model)
            query_embedding = (await embedder.embed([args.query]))[0]

            results = await vector_store.search(
                session,
                knowledge_base_id=kb_id,
                query=args.query,
                query_embedding=query_embedding,
                search_type="hybrid",
                top_k=args.top_k,
            )

        if not results:
            return "No relevant results found."
        return "\n".join(f"[{r.filename}] {r.content[:500]}" for r in results)
