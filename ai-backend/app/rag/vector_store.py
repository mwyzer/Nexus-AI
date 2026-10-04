from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chunk import Chunk as ChunkModel
from ..models.chunk_embedding import ChunkEmbedding
from ..models.document import Document
from ..schemas.chunk import SearchResult
from .chunking import Chunk


async def add_chunks(
    session: AsyncSession,
    document_id: UUID,
    chunks: list[Chunk],
    embeddings: list[list[float]],
    embedding_model: str,
) -> list[ChunkModel]:
    """Persist chunks and their embeddings for a document."""
    chunk_rows: list[ChunkModel] = []
    for chunk in chunks:
        row = ChunkModel(
            document_id=document_id,
            content=chunk.content,
            chunk_index=chunk.index,
            chunk_metadata=chunk.metadata,
        )
        session.add(row)
        chunk_rows.append(row)
    await session.flush()  # assign chunk row IDs before creating embeddings

    for row, embedding in zip(chunk_rows, embeddings):
        session.add(ChunkEmbedding(chunk_id=row.id, embedding=embedding, model=embedding_model))

    return chunk_rows


async def delete_document_chunks(session: AsyncSession, document_id: UUID) -> None:
    result = await session.execute(select(ChunkModel).where(ChunkModel.document_id == document_id))
    for row in result.scalars():
        await session.delete(row)


async def semantic_search(
    session: AsyncSession,
    knowledge_base_id: UUID,
    query_embedding: list[float],
    top_k: int,
    score_threshold: float = 0.0,
) -> list[SearchResult]:
    distance = ChunkEmbedding.embedding.cosine_distance(query_embedding)
    stmt = (
        select(
            ChunkModel.id,
            ChunkModel.document_id,
            Document.filename,
            ChunkModel.content,
            ChunkModel.chunk_index,
            (1 - distance).label("score"),
        )
        .join(ChunkEmbedding, ChunkEmbedding.chunk_id == ChunkModel.id)
        .join(Document, Document.id == ChunkModel.document_id)
        .where(Document.knowledge_base_id == knowledge_base_id)
        .order_by(distance)
        .limit(top_k)
    )
    rows = (await session.execute(stmt)).all()
    return [
        SearchResult(
            chunk_id=r.id,
            document_id=r.document_id,
            filename=r.filename,
            content=r.content,
            chunk_index=r.chunk_index,
            score=float(r.score),
        )
        for r in rows
        if float(r.score) >= score_threshold
    ]


async def keyword_search(
    session: AsyncSession,
    knowledge_base_id: UUID,
    query: str,
    top_k: int,
    score_threshold: float = 0.0,
) -> list[SearchResult]:
    tsquery = func.plainto_tsquery("english", query)
    tsvector = func.to_tsvector("english", ChunkModel.content)
    rank = func.ts_rank(tsvector, tsquery).label("score")
    stmt = (
        select(
            ChunkModel.id,
            ChunkModel.document_id,
            Document.filename,
            ChunkModel.content,
            ChunkModel.chunk_index,
            rank,
        )
        .join(Document, Document.id == ChunkModel.document_id)
        .where(Document.knowledge_base_id == knowledge_base_id, tsvector.op("@@")(tsquery))
        .order_by(rank.desc())
        .limit(top_k)
    )
    rows = (await session.execute(stmt)).all()
    return [
        SearchResult(
            chunk_id=r.id,
            document_id=r.document_id,
            filename=r.filename,
            content=r.content,
            chunk_index=r.chunk_index,
            score=float(r.score),
        )
        for r in rows
        if float(r.score) >= score_threshold
    ]


def _normalize(results: list[SearchResult]) -> dict[UUID, float]:
    if not results:
        return {}
    max_score = max(r.score for r in results) or 1.0
    return {r.chunk_id: r.score / max_score for r in results}


async def hybrid_search(
    session: AsyncSession,
    knowledge_base_id: UUID,
    query: str,
    query_embedding: list[float],
    top_k: int,
    hybrid_weight: float,
    score_threshold: float = 0.0,
) -> list[SearchResult]:
    """Combine normalized semantic and keyword scores with a configurable weight."""
    candidate_k = max(top_k * 4, 20)
    # Candidates are gathered unfiltered — score_threshold applies to the
    # final blended score below, not to either component on its own.
    semantic_results = await semantic_search(session, knowledge_base_id, query_embedding, candidate_k)
    keyword_results = await keyword_search(session, knowledge_base_id, query, candidate_k)

    by_chunk: dict[UUID, SearchResult] = {r.chunk_id: r for r in semantic_results}
    for r in keyword_results:
        by_chunk.setdefault(r.chunk_id, r)

    semantic_scores = _normalize(semantic_results)
    keyword_scores = _normalize(keyword_results)

    combined: list[SearchResult] = []
    for chunk_id, result in by_chunk.items():
        score = hybrid_weight * semantic_scores.get(chunk_id, 0.0) + (
            1 - hybrid_weight
        ) * keyword_scores.get(chunk_id, 0.0)
        if score >= score_threshold:
            combined.append(result.model_copy(update={"score": score}))

    combined.sort(key=lambda r: r.score, reverse=True)
    return combined[:top_k]


async def search(
    session: AsyncSession,
    knowledge_base_id: UUID,
    query: str,
    query_embedding: list[float] | None,
    search_type: str,
    top_k: int,
    hybrid_weight: float = 0.7,
    score_threshold: float = 0.0,
) -> list[SearchResult]:
    if search_type == "semantic":
        if query_embedding is None:
            raise ValueError("query_embedding is required for semantic search")
        return await semantic_search(session, knowledge_base_id, query_embedding, top_k, score_threshold)
    if search_type == "keyword":
        return await keyword_search(session, knowledge_base_id, query, top_k, score_threshold)
    if search_type == "hybrid":
        if query_embedding is None:
            raise ValueError("query_embedding is required for hybrid search")
        return await hybrid_search(
            session, knowledge_base_id, query, query_embedding, top_k, hybrid_weight, score_threshold
        )
    raise ValueError(f"Unknown search type: {search_type}")
