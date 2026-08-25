from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup
from pypdf import PdfReader


class UnsupportedFormatError(Exception):
    pass


@dataclass
class ParsedDocument:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _parse_pdf(raw: bytes) -> ParsedDocument:
    from io import BytesIO

    reader = PdfReader(BytesIO(raw))
    pages = [page.extract_text() or "" for page in reader.pages]
    return ParsedDocument(text="\n\n".join(pages), metadata={"page_count": len(pages)})


def _parse_markdown(raw: bytes) -> ParsedDocument:
    return ParsedDocument(text=raw.decode("utf-8", errors="replace"))


def _parse_text(raw: bytes) -> ParsedDocument:
    return ParsedDocument(text=raw.decode("utf-8", errors="replace"))


def _parse_html(raw: bytes) -> ParsedDocument:
    soup = BeautifulSoup(raw.decode("utf-8", errors="replace"), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return ParsedDocument(text="\n".join(line for line in lines if line))


_PARSERS = {
    "application/pdf": _parse_pdf,
    "text/markdown": _parse_markdown,
    "text/plain": _parse_text,
    "text/html": _parse_html,
}


def parse_document(raw: bytes, mime_type: str) -> ParsedDocument:
    """Parse raw file bytes into clean text with metadata."""
    parser = _PARSERS.get(mime_type)
    if parser is None:
        raise UnsupportedFormatError(f"Unsupported format: {mime_type}")
    return parser(raw)
