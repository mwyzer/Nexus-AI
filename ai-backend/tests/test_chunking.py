from app.rag.chunking import (
    FixedSizeChunker,
    MarkdownHeaderChunker,
    RecursiveChunker,
    SemanticChunker,
    get_chunker,
)
from app.schemas.chunk import ChunkConfig


def test_fixed_size_chunker_respects_size_and_overlap():
    text = "a" * 2500
    chunker = FixedSizeChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.split(text)

    assert len(chunks) >= 3
    assert all(len(c.content) <= 1000 for c in chunks)
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_fixed_size_chunker_handles_short_text():
    chunker = FixedSizeChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.split("short text")
    assert len(chunks) == 1
    assert chunks[0].content == "short text"


def test_fixed_size_chunker_handles_empty_text():
    chunker = FixedSizeChunker(chunk_size=1000, chunk_overlap=200)
    assert chunker.split("") == []


def test_recursive_chunker_splits_on_paragraphs():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 50 for i in range(10))
    chunker = RecursiveChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(chunk.content for chunk in chunks)


def test_markdown_header_chunker_splits_by_heading():
    text = "# Title\n\nIntro text.\n\n## Section A\n\n" + ("content " * 100) + "\n\n## Section B\n\nMore content."
    chunker = MarkdownHeaderChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split(text)

    assert len(chunks) >= 2
    headers = [c.metadata.get("h2") for c in chunks if c.metadata.get("h2")]
    assert "Section A" in headers
    assert "Section B" in headers


def test_semantic_chunker_groups_sentences_within_size():
    sentences = [f"This is sentence number {i}." for i in range(30)]
    text = "\n\n".join(sentences)
    chunker = SemanticChunker(chunk_size=200, chunk_overlap=40)
    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(len(c.content) <= 260 for c in chunks)  # allow slack for overlap sentence


def test_semantic_chunker_handles_single_sentence():
    chunker = SemanticChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.split("Just one sentence.")
    assert len(chunks) == 1
    assert chunks[0].content == "Just one sentence."


def test_get_chunker_factory_dispatches_by_strategy():
    assert isinstance(get_chunker(ChunkConfig(strategy="fixed")), FixedSizeChunker)
    assert isinstance(get_chunker(ChunkConfig(strategy="recursive")), RecursiveChunker)
    assert isinstance(get_chunker(ChunkConfig(strategy="markdown")), MarkdownHeaderChunker)
    assert isinstance(get_chunker(ChunkConfig(strategy="semantic")), SemanticChunker)
