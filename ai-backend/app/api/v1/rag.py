from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import get_current_user
from ...rag.generation import LLMGenerationError, generate_answer
from ...schemas.rag import RAGQuery, RAGResponse

router = APIRouter()


@router.post("/generate", response_model=RAGResponse)
async def generate(
    query: RAGQuery,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        return await generate_answer(db, query)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LLMGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
