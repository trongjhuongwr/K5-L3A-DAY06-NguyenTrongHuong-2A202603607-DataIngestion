"""Read and normalize source data."""
import unicodedata
import re
from pathlib import Path
from pypdf import PdfReader
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC) and whitespace without discarding useful structure."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # Normalize inline whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Standardize line breaks: maximum 2 consecutive newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def get_section_for_page(page_num: int) -> str:
    """Determine the policy section based on the physical page number."""
    if page_num <= 2:
        return "quy_dinh_chung"
    elif 3 <= page_num <= 12:
        return "ha_tang_khcn"
    elif 13 <= page_num <= 14:
        return "doanh_nghiep_he_sinh_thai"
    elif 15 <= page_num <= 16:
        return "to_chuc_thuc_hien"
    else:
        return "bieu_mau_ho_so"


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; keep page number, source, and metadata."""
    reader = PdfReader(str(path))
    pages: list[DocumentPage] = []

    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        norm_text = normalize_text(raw_text)

        if len(norm_text) < 10:
            print(f"[Warning] Page {idx} has empty or unextractable text.")
            continue

        section = get_section_for_page(idx)
        doc_type = "quy_dinh" if idx <= 16 else "bieu_mau"

        metadata = {
            "section": section,
            "document_type": doc_type,
            "year": 2026,
            "authority": "ubnd_hanoi"
        }

        pages.append(DocumentPage(
            document_id=document_id,
            source=source,
            page=idx,
            text=norm_text,
            metadata=metadata
        ))

    return pages
