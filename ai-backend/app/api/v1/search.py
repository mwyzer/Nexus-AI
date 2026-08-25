from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.knowledge_base import KnowledgeBase
from ...rag import vector_store
from ...rag.embedding import get_embedder
from ...schemas.chunk import SearchQuery, SearchResponse

router = APIRouter()


def _infer_embedding_provider(model: str) -> str:
    return "openai" if model.startswith("text-embedding") else "ollama"


@router.post("", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query_embedding = None
    if query.search_type in ("semantic", "hybrid"):
        kb = await db.get(KnowledgeBase, query.knowledge_base_id)
        if kb is not None:
            provider = _infer_embedding_provider(kb.embedding_model)
            embedder = get_embedder(provider, kb.embedding_model)
            query_embedding = (await embedder.embed([query.query]))[0]

    results = await vector_store.search(
        db,
        knowledge_base_id=query.knowledge_base_id,
        query=query.query,
        query_embedding=query_embedding,
        search_type=query.search_type,
        top_k=query.top_k,
        hybrid_weight=query.hybrid_weight,
        score_threshold=query.score_threshold,
    )
    return SearchResponse(results=results, query=query.query, search_type=query.search_type)
