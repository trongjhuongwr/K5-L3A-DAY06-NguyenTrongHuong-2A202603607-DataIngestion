"""Chunking strategies: Strategy A (Fixed) and Strategy B/C (Semantic Paragraph/Clause)."""
import re
from .models import DocumentPage, Chunk


def chunk_strategy_a_fixed(pages: list[DocumentPage], chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Strategy A: Baseline fixed-size character chunking with overlapping boundaries."""
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


def clean_and_unwrap_page(text: str) -> str:
    """Remove header page numbers and unwrap soft line-breaks into coherent sentences."""
    # Remove leading page number (e.g., '2\n', '15\n')
    text = re.sub(r"^\s*\d+\s*\n", "", text)
    # Simplify repeated form dots
    text = re.sub(r"\.{4,}", "...", text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    merged: list[str] = []
    
    for line in lines:
        if not merged:
            merged.append(line)
            continue
        # If line starts with a legal clause marker or section heading, preserve line break
        if re.match(r"^(Chương\s+[IVXLCDM]+|Điều\s+\d+\.|\d+\.\s+|[a-zđ]\)\s+|Mẫu\s+số\s+\d+|[IVXLCDM]+\.\s+)", line):
            merged.append("\n" + line)
        else:
            prev = merged[-1]
            if prev.endswith((":", ".", ";", "?", "!")):
                merged.append("\n" + line)
            else:
                merged[-1] = f"{prev} {line}"
                
    return "\n".join(merged)


def split_long_unit(unit: str, max_length: int = 800) -> list[str]:
    """Split units exceeding max_length by sentence or semicolon boundaries."""
    if len(unit) <= max_length:
        return [unit]
    subparts = re.split(r"(?<=[;.])\s+", unit)
    out: list[str] = []
    buf = ""
    for sp in subparts:
        if len(buf) + len(sp) + 1 <= max_length:
            buf = f"{buf} {sp}".strip() if buf else sp
        else:
            if buf:
                out.append(buf)
            buf = sp
    if buf:
        out.append(buf)
    return out


def chunk_strategy_b_paragraph(pages: list[DocumentPage], max_length: int = 800) -> list[Chunk]:
    """Strategy B & C: Semantic legal clause and paragraph-based chunking (strictly <= max_length)."""
    chunks: list[Chunk] = []

    for page in pages:
        unwrapped = clean_and_unwrap_page(page.text)
        raw_units = [
            u.strip() for u in re.split(
                r"\n(?=(?:Chương\s+[IVXLCDM]+|Điều\s+\d+\.|\d+\.\s+|Mẫu\s+số\s+\d+|[IVXLCDM]+\.\s+))",
                unwrapped
            ) if u.strip()
        ]

        units: list[str] = []
        for ru in raw_units:
            units.extend(split_long_unit(ru, max_length))

        buffer = ""
        c_idx = 1

        for u in units:
            if len(buffer) + len(u) + 2 <= max_length:
                buffer = f"{buffer}\n\n{u}".strip() if buffer else u
            else:
                if buffer:
                    chunk_id = f"strat_b_{page.document_id}_p{page.page:02d}_c{c_idx:03d}"
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=buffer,
                        metadata=dict(page.metadata)
                    ))
                    c_idx += 1
                buffer = u

        if buffer:
            chunk_id = f"strat_b_{page.document_id}_p{page.page:02d}_c{c_idx:03d}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=buffer,
                metadata=dict(page.metadata)
            ))

    return chunks
