"""Convert Hanoi SciTech Policy PDF into clean, structured Markdown.
Outputs starter/data/corpus_cleaned.md.
"""
import re
import unicodedata
from pathlib import Path
from pypdf import PdfReader

ROOT_DIR = Path("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion")
PDF_PATH = ROOT_DIR / "starter" / "data" / "quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
OUT_MD_PATH = ROOT_DIR / "starter" / "data" / "corpus_cleaned.md"


def clean_page_text(raw_text: str) -> str:
    """Normalize text and remove leading page number."""
    if not raw_text:
        return ""
    text = unicodedata.normalize("NFC", raw_text)
    # Strip leading page number like '2\n', '15\n'
    text = re.sub(r"^\s*\d+\s*\n", "", text)
    # Replace repeated form dots
    text = re.sub(r"\.{4,}", "...", text)
    # Replace checkbox character with markdown task checkbox
    text = text.replace("☐", "- [ ] ")
    return text


def build_markdown(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    md_lines: list[str] = [
        "# QUY ĐỊNH TRÌNH TỰ, THỦ TỤC HỖ TRỢ PHÁT TRIỂN HẠ TẦNG VÀ TỔ CHỨC CÓ HOẠT ĐỘNG TRONG LĨNH VỰC KHOA HỌC, CÔNG NGHỆ, ĐỔI MỚI SÁNG TẠO VÀ CHUYỂN ĐỔI SỐ TRÊN ĐỊA BÀN THÀNH PHỐ HÀ NỘI",
        "*(Ban hành kèm theo Quyết định số .../2026/QĐ-UBND ngày ... tháng ... năm 2026 của UBND thành phố Hà Nội)*\n",
    ]

    for page_idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned = clean_page_text(raw_text)
        
        md_lines.append(f"\n<!-- PAGE {page_idx} -->\n")
        
        lines = [l.strip() for l in cleaned.split("\n")]
        
        for line in lines:
            if not line:
                continue

            # Section / Chuong heading
            if re.match(r"^Chương\s+[IVXLCDM]+", line, re.IGNORECASE):
                md_lines.append(f"\n# {line}\n")
            # Dieu heading
            elif re.match(r"^Điều\s+\d+\.", line):
                md_lines.append(f"\n## {line}\n")
            # Mau so heading (in Annex)
            elif re.match(r"^Mẫu số\s+\d+", line) and page_idx >= 17:
                md_lines.append(f"\n## {line}\n")
            # Khoan / numbered point: 1. , 2. , 3.
            elif re.match(r"^\d+\.\s+", line):
                md_lines.append(f"\n### {line}")
            # Sub-item: a) , b) , c) , đ)
            elif re.match(r"^[a-zđ]\)\s+", line):
                md_lines.append(f"- {line}")
            # Standard prose text: determine if we should unwrap / merge
            else:
                prev_line = md_lines[-1] if md_lines else ""
                # Check if previous line is a heading or ended with a terminal colon/period/semicolon
                is_prev_closed = (
                    prev_line.endswith((".", ":", ";", "?", "!", "-->", "\n")) or
                    prev_line.startswith(("#", "-"))
                )

                if prev_line and not is_prev_closed and not prev_line.startswith("<!--"):
                    # Unwrap: join with previous sentence
                    md_lines[-1] = f"{prev_line} {line}"
                else:
                    md_lines.append(line)

    return "\n".join(md_lines)


def main():
    print(f"Reading PDF from: {PDF_PATH}")
    md_content = build_markdown(PDF_PATH)
    
    # Final cleanup of multiple empty lines
    md_content = re.sub(r"\n{3,}", "\n\n", md_content)
    
    with open(OUT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Generated clean Markdown at: {OUT_MD_PATH}")
    print(f"Total size: {OUT_MD_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
