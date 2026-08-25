from fastapi import APIRouter

from .documents import router as documents_router
from .health import router as health_router
from .knowledge_bases import router as knowledge_bases_router
from .rag import router as rag_router
from .search import router as search_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(
    knowledge_bases_router, prefix="/knowledge-bases", tags=["knowledge-bases"]
)
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(rag_router, prefix="/rag", tags=["rag"])
