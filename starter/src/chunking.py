"""Chunking strategies: Strategy A (Fixed) and Strategy B/C (Paragraph/Clause)."""
from .models import DocumentPage, Chunk


def chunk_strategy_a_fixed(pages: list[DocumentPage], chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Strategy A: Fixed-size chunks with overlapping boundaries."""
    chunks: list[Chunk] = []
    step = chunk_size - overlap

    for page in pages:
        text = page.text
        start = 0
        chunk_idx = 1

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunk_id = f"strat_a_{page.document_id}_p{page.page:02d}_c{chunk_idx:03d}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=chunk_text,
                metadata=dict(page.metadata)
            ))
            chunk_idx += 1
            start += step

    return chunks


def chunk_strategy_b_paragraph(pages: list[DocumentPage], max_length: int = 800) -> list[Chunk]:
    """Strategy B & C: Semantic paragraph / clause-based chunking."""
    chunks: list[Chunk] = []

    for page in pages:
        # Split by paragraph breaks
        raw_paragraphs = page.text.split("\n\n")
        buffer = ""
        chunk_idx = 1

        for p in raw_paragraphs:
            p = p.strip()
            if not p:
                continue

            if len(buffer) + len(p) + 2 <= max_length:
                buffer = f"{buffer}\n\n{p}".strip()
            else:
                if buffer:
                    chunk_id = f"strat_b_{page.document_id}_p{page.page:02d}_c{chunk_idx:03d}"
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=buffer,
                        metadata=dict(page.metadata)
                    ))
                    chunk_idx += 1
                buffer = p

        if buffer:
            chunk_id = f"strat_b_{page.document_id}_p{page.page:02d}_c{chunk_idx:03d}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=buffer,
                metadata=dict(page.metadata)
            ))

    return chunks
