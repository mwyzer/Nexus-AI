import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from ..schemas.chunk import ChunkConfig

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    content: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)


class Chunker(ABC):
    @abstractmethod
    def split(self, text: str) -> list[Chunk]:
        """Split text into chunks with metadata."""


class FixedSizeChunker(Chunker):
    """Splits on raw character count with a fixed overlap. No structure awareness."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = max(0, min(chunk_overlap, chunk_size - 1))

    def split(self, text: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        step = self.chunk_size - self.chunk_overlap
        start = 0
        index = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            content = text[start:end].strip()
            if content:
                chunks.append(Chunk(content=content, index=index))
                index += 1
            if end == text_len:
                break
            start += step
        return chunks


class RecursiveChunker(Chunker):
    """Splits hierarchically on a list of separators, falling back to smaller ones."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators or ["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, text: str) -> list[Chunk]:
        pieces = self._splitter.split_text(text)
        return [
            Chunk(content=piece.strip(), index=i)
            for i, piece in enumerate(pieces)
            if piece.strip()
        ]


class MarkdownHeaderChunker(Chunker):
    """Splits by heading level first, then by size within each section."""

    _HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self._HEADERS)
        self._size_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split(self, text: str) -> list[Chunk]:
        sections = self._header_splitter.split_text(text)
        chunks: list[Chunk] = []
        index = 0
        for section in sections:
            for piece in self._size_splitter.split_text(section.page_content):
                content = piece.strip()
                if content:
                    chunks.append(Chunk(content=content, index=index, metadata=dict(section.metadata)))
                    index += 1
        return chunks


class SemanticChunker(Chunker):
    """Groups sentences into chunks, preferring to break at paragraph boundaries.

    This is a heuristic (structure-aware) semantic splitter rather than an
    embedding-similarity splitter — it avoids requiring an embedding call
    during chunking, which would otherwise couple chunking to a specific
    embedding provider before one has been chosen for the knowledge base.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[Chunk]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        sentences: list[str] = []
        for paragraph in paragraphs:
            sentences.extend(s for s in _SENTENCE_BOUNDARY.split(paragraph) if s)

        chunks: list[Chunk] = []
        current: list[str] = []
        current_len = 0
        index = 0

        for sentence in sentences:
            sentence_len = len(sentence) + 1
            if current and current_len + sentence_len > self.chunk_size:
                content = " ".join(current).strip()
                chunks.append(Chunk(content=content, index=index))
                index += 1
                overlap_sentences: list[str] = []
                overlap_len = 0
                for s in reversed(current):
                    if overlap_len + len(s) > self.chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_len += len(s) + 1
                current = overlap_sentences
                current_len = overlap_len
            current.append(sentence)
            current_len += sentence_len

        if current:
            chunks.append(Chunk(content=" ".join(current).strip(), index=index))

        return chunks


def get_chunker(config: ChunkConfig) -> Chunker:
    if config.strategy == "fixed":
        return FixedSizeChunker(config.chunk_size, config.chunk_overlap)
    if config.strategy == "recursive":
        return RecursiveChunker(config.chunk_size, config.chunk_overlap, config.separators)
    if config.strategy == "markdown":
        return MarkdownHeaderChunker(config.chunk_size, config.chunk_overlap)
    if config.strategy == "semantic":
        return SemanticChunker(config.chunk_size, config.chunk_overlap)
    raise ValueError(f"Unknown chunking strategy: {config.strategy}")
