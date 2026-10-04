import time

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.llm import LLMCompletionError as LLMGenerationError
from ..core.llm import complete as _complete
from ..models.knowledge_base import KnowledgeBase
from ..schemas.chunk import SearchResult
from ..schemas.rag import Citation, RAGQuery, RAGResponse
from . import vector_store
from .embedding import get_embedder, infer_embedding_provider

PROMPT_TEMPLATE = """You are an AI assistant with access to a knowledge base.
Answer the user's question based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based on the context provided
- Cite sources using [1], [2] format
- If the context doesn't contain the answer, say so
- Be concise and accurate
"""

NO_CONTEXT_ANSWER = "I don't have relevant information in the knowledge base to answer that."


def _build_context(results: list[SearchResult]) -> str:
    return "\n\n".join(f"[{i + 1}] {r.content}" for i, r in enumerate(results))


async def generate_answer(session: AsyncSession, query: RAGQuery) -> RAGResponse:
    start = time.perf_counter()

    kb = await session.get(KnowledgeBase, query.knowledge_base_id)
    if kb is None:
        raise ValueError("Knowledge base not found")

    provider = infer_embedding_provider(kb.embedding_model)
    embedder = get_embedder(provider, kb.embedding_model)
    query_embedding = (await embedder.embed([query.question]))[0]

    results = await vector_store.search(
        session,
        knowledge_base_id=query.knowledge_base_id,
        query=query.question,
        query_embedding=query_embedding,
        search_type=query.search_type,
        top_k=query.top_k,
    )

    if not results:
        return RAGResponse(
            answer=NO_CONTEXT_ANSWER,
            citations=[],
            confidence=0.0,
            processing_time_ms=(time.perf_counter() - start) * 1000,
        )

    prompt = PROMPT_TEMPLATE.format(context=_build_context(results), question=query.question)
    answer = await _complete(prompt)

    citations = [
        Citation(
            document_id=r.document_id,
            filename=r.filename,
            chunk_index=r.chunk_index,
            text_snippet=r.content[:280],
            relevance_score=r.score,
        )
        for r in results
    ]
    confidence = sum(r.score for r in results) / len(results)

    return RAGResponse(
        answer=answer,
        citations=citations,
        confidence=confidence,
        processing_time_ms=(time.perf_counter() - start) * 1000,
    )
