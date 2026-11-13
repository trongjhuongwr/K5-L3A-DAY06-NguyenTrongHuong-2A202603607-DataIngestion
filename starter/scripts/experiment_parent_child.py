"""Experiment: Parent-Child Chunking & Retrieval on Hanoi SciTech Policy 2026.
Builds Strategy D (Parent-Child) and benchmarks against Strategy A, B, and C.
"""
import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Any
import psycopg
from dotenv import load_dotenv

ROOT_DIR = Path("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion")
STARTER_DIR = ROOT_DIR / "starter"
sys.path.insert(0, str(STARTER_DIR))

load_dotenv(STARTER_DIR / ".env")

from src.embeddings import get_embeddings
from src.store import to_vector_str

PDF_PATH = STARTER_DIR / "data" / "quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
QUESTIONS_PATH = ROOT_DIR / "benchmark" / "questions.json"
RESULTS_DIR = STARTER_DIR / "results"
DB_URL = os.getenv("DATABASE_URL", "postgresql://student:student_pass_2026@127.0.0.1:55433/day6_rag")


def parse_parent_child_corpus():
    """Extract pages from PDF and build hierarchical Parent and Child chunks."""
    from pypdf import PdfReader
    reader = PdfReader(str(PDF_PATH))
    
    pages = []
    for idx, p in enumerate(reader.pages, 1):
        txt = p.extract_text() or ""
        # Clean soft wraps
        t = re.sub(r"^\s*\d+\s*\n", "", txt)
        t = re.sub(r"\.{4,}", "...", t)
        t = t.replace("☐", "- [ ] ")
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        merged = []
        for line in lines:
            if not merged:
                merged.append(line)
                continue
            if re.match(r"^(Chương\s+[IVXLCDM]+|Điều\s+\d+\.|\d+\.\s+|[a-zđ]\)\s+|Mẫu\s+số\s+\d+|[IVXLCDM]+\.\s+)", line):
                merged.append("\n" + line)
            else:
                prev = merged[-1]
                if prev.endswith((":", ".", ";", "?", "!")):
                    merged.append("\n" + line)
                else:
                    merged[-1] = f"{prev} {line}"
        cleaned = "\n".join(merged)
        pages.append({"page": idx, "text": cleaned, "raw": txt})

    parents = []
    children = []

    # 1. Rules Section (Pages 1-16): Parent = Article (Dieu), Child = Clause (Khoan)
    # Combine text of pages 1-16 while tracking page positions
    full_text_p1_16 = ""
    page_markers = []
    for p in pages[:16]:
        start_char = len(full_text_p1_16)
        full_text_p1_16 += f"\n<!-- PAGE_{p['page']} -->\n" + p["text"]
        end_char = len(full_text_p1_16)
        page_markers.append((p["page"], start_char, end_char))

    def find_page_for_pos(pos: int) -> int:
        for pnum, s, e in page_markers:
            if s <= pos <= e:
                return pnum
        return 1

    # Split articles: Điều 1 -> Điều 18
    article_splits = list(re.finditer(r"(Điều\s+(\d+)\.\s*([^\n]+))", full_text_p1_16))
    
    for i, match in enumerate(article_splits):
        dieu_num = int(match.group(2))
        dieu_title = match.group(3).strip()
        start_idx = match.start()
        end_idx = article_splits[i+1].start() if i + 1 < len(article_splits) else len(full_text_p1_16)
        
        article_raw = full_text_p1_16[start_idx:end_idx].strip()
        # Clean page markers from text
        article_clean = re.sub(r"<!-- PAGE_\d+ -->\n?", "", article_raw).strip()
        
        start_page = find_page_for_pos(start_idx)
        end_page = find_page_for_pos(end_idx - 1)

        parent_id = f"parent_dieu_{dieu_num:02d}"
        parent_chunk = {
            "parent_id": parent_id,
            "title": f"Điều {dieu_num}. {dieu_title}",
            "dieu": f"Điều {dieu_num}",
            "page_start": start_page,
            "page_end": end_page,
            "content": article_clean,
            "section": "Chương I: Quy định chung" if dieu_num <= 2 else (
                "Chương II: Hỗ trợ hạ tầng KH&CN" if dieu_num <= 12 else (
                    "Chương III: Ưu đãi doanh nghiệp" if dieu_num <= 14 else "Chương IV: Tổ chức thi hành"
                )
            ),
            "length": len(article_clean)
        }
        parents.append(parent_chunk)

        # Build Child Chunks for this Article
        # Tách theo Khoản: 1. , 2. , 3.
        clause_splits = list(re.finditer(r"(\n|^)(\d+\.\s+)", article_clean))
        if clause_splits:
            for j, c_match in enumerate(clause_splits):
                k_num = c_match.group(2).strip()
                c_start = c_match.start()
                c_end = clause_splits[j+1].start() if j + 1 < len(clause_splits) else len(article_clean)
                clause_text = article_clean[c_start:c_end].strip()
                
                # Context Prefix: Gắn số hiệu Điều vào đầu Child Chunk để vector không bị loãng
                context_prefix = f"[{parent_chunk['title']}]\n"
                child_content = context_prefix + clause_text
                
                # Ước lượng số trang của khoản
                clause_pos_in_full = full_text_p1_16.find(clause_text[:40], start_idx)
                clause_page = find_page_for_pos(clause_pos_in_full) if clause_pos_in_full != -1 else start_page

                child_id = f"child_dieu_{dieu_num:02d}_k{j+1:02d}"
                children.append({
                    "chunk_id": child_id,
                    "parent_id": parent_id,
                    "document_id": "quy-dinh-ha-tang-khcn-hanoi-2026",
                    "source": "quy-dinh-ha-tang-khcn-hanoi-2026",
                    "page": clause_page,
                    "content": child_content,
                    "raw_clause": clause_text,
                    "metadata": {
                        "level": "child",
                        "parent_id": parent_id,
                        "dieu": f"Điều {dieu_num}",
                        "section": parent_chunk["section"],
                        "khoan": k_num,
                        "length": len(child_content)
                    }
                })
        else:
            # Điều ngắn không chia khoản (ví dụ Điều 3, Điều 4) -> 1 Child
            child_id = f"child_dieu_{dieu_num:02d}_all"
            children.append({
                "chunk_id": child_id,
                "parent_id": parent_id,
                "document_id": "quy-dinh-ha-tang-khcn-hanoi-2026",
                "source": "quy-dinh-ha-tang-khcn-hanoi-2026",
                "page": start_page,
                "content": article_clean,
                "raw_clause": article_clean,
                "metadata": {
                    "level": "child",
                    "parent_id": parent_id,
                    "dieu": f"Điều {dieu_num}",
                    "section": parent_chunk["section"],
                    "length": len(article_clean)
                }
            })

    # 2. Annex Section (Pages 17-40): Parent = Page/Form, Child = Chunks (300-500 chars)
    for p in pages[16:]:
        p_num = p["page"]
        p_text = p["text"].strip()
        parent_id = f"parent_page_{p_num:02d}"
        
        # Determine form name if any
        form_match = re.search(r"(Mẫu\s+số\s+\d+[^\n]*)", p_text)
        form_title = form_match.group(1).strip() if form_match else f"Phụ lục Biểu mẫu Trang {p_num}"

        parent_chunk = {
            "parent_id": parent_id,
            "title": form_title,
            "dieu": "Phụ lục",
            "page_start": p_num,
            "page_end": p_num,
            "content": p_text,
            "section": f"Phụ lục: Biểu mẫu (Trang {p_num})",
            "length": len(p_text)
        }
        parents.append(parent_chunk)

        # Split page into 300-500 char children with prefix
        # Split by paragraphs or double newlines
        parts = [pr.strip() for pr in p_text.split("\n\n") if pr.strip()]
        c_idx = 1
        for pr in parts:
            if len(pr) < 80:
                continue
            child_id = f"child_p{p_num:02d}_c{c_idx:02d}"
            child_content = f"[{form_title} - Trang {p_num}]\n{pr}"
            children.append({
                "chunk_id": child_id,
                "parent_id": parent_id,
                "document_id": "quy-dinh-ha-tang-khcn-hanoi-2026",
                "source": "quy-dinh-ha-tang-khcn-hanoi-2026",
                "page": p_num,
                "content": child_content,
                "raw_clause": pr,
                "metadata": {
                    "level": "child",
                    "parent_id": parent_id,
                    "section": parent_chunk["section"],
                    "form": form_title,
                    "length": len(child_content)
                }
            })
            c_idx += 1

    return parents, children


def setup_database_and_store(parents: list[dict], children: list[dict], child_embeddings: list[list[float]]):
    """Create Strategy D tables in PostgreSQL pgvector and insert chunks."""
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # 1. Parent table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks_strategy_d_parent (
                    parent_id TEXT PRIMARY KEY,
                    title TEXT,
                    dieu TEXT,
                    page_start INT,
                    page_end INT,
                    content TEXT,
                    section TEXT,
                    metadata JSONB
                );
                TRUNCATE TABLE chunks_strategy_d_parent;
            """)
            
            for p in parents:
                cur.execute("""
                    INSERT INTO chunks_strategy_d_parent (parent_id, title, dieu, page_start, page_end, content, section, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb);
                """, (
                    p["parent_id"],
                    p["title"],
                    p.get("dieu", ""),
                    p["page_start"],
                    p["page_end"],
                    p["content"],
                    p["section"],
                    json.dumps(p)
                ))

            # 2. Child table with vector
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks_strategy_d_child (
                    chunk_id TEXT PRIMARY KEY,
                    parent_id TEXT REFERENCES chunks_strategy_d_parent(parent_id) ON DELETE CASCADE,
                    document_id TEXT,
                    source TEXT,
                    page INT,
                    content TEXT,
                    metadata JSONB,
                    embedding vector(1536)
                );
                TRUNCATE TABLE chunks_strategy_d_child;
            """)

            for c, emb in zip(children, child_embeddings):
                v_str = to_vector_str(emb)
                cur.execute("""
                    INSERT INTO chunks_strategy_d_child (chunk_id, parent_id, document_id, source, page, content, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::vector);
                """, (
                    c["chunk_id"],
                    c["parent_id"],
                    c["document_id"],
                    c["source"],
                    c["page"],
                    c["content"],
                    json.dumps(c["metadata"]),
                    v_str
                ))

        conn.commit()


def run_parent_child_retrieval(questions: list[dict], query_embeddings: list[list[float]]) -> list[dict]:
    """Execute Parent-Child retrieval against PostgreSQL pgvector."""
    results = []
    
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for q, q_emb in zip(questions, query_embeddings):
                v_str = to_vector_str(q_emb)
                q_filter = q.get("filter")
                
                # 1. Search top 5 Child Chunks
                if q_filter:
                    cur.execute("""
                        SELECT c.chunk_id, c.parent_id, c.page, c.content, c.metadata,
                               1 - (c.embedding <=> %s::vector) AS similarity,
                               p.title AS parent_title, p.content AS parent_content, p.page_start, p.page_end
                        FROM chunks_strategy_d_child c
                        JOIN chunks_strategy_d_parent p ON c.parent_id = p.parent_id
                        WHERE c.metadata @> %s::jsonb
                        ORDER BY c.embedding <=> %s::vector ASC
                        LIMIT 5;
                    """, (v_str, json.dumps(q_filter), v_str))
                else:
                    cur.execute("""
                        SELECT c.chunk_id, c.parent_id, c.page, c.content, c.metadata,
                               1 - (c.embedding <=> %s::vector) AS similarity,
                               p.title AS parent_title, p.content AS parent_content, p.page_start, p.page_end
                        FROM chunks_strategy_d_child c
                        JOIN chunks_strategy_d_parent p ON c.parent_id = p.parent_id
                        ORDER BY c.embedding <=> %s::vector ASC
                        LIMIT 5;
                    """, (v_str, v_str))
                
                rows = cur.fetchall()

                # Deduplicate Parents while preserving best ranking
                seen_parents = set()
                top_parents = []
                top_children = []
                
                for r in rows:
                    ch_id, p_id, ch_page, ch_content, ch_meta, sim, p_title, p_content, p_s, p_e = r
                    top_children.append({
                        "chunk_id": ch_id,
                        "parent_id": p_id,
                        "page": ch_page,
                        "content": ch_content,
                        "similarity": float(sim)
                    })
                    if p_id not in seen_parents:
                        seen_parents.add(p_id)
                        top_parents.append({
                            "parent_id": p_id,
                            "title": p_title,
                            "page_start": p_s,
                            "page_end": p_e,
                            "content": p_content,
                            "best_child_sim": float(sim)
                        })

                # Check Grounding / Hit on Child & Parent
                quote = q["evidence_quote"].strip()
                sub_quote = quote.split(".")[0].strip()[:35]

                # Child Hit
                child_hit_1 = False
                child_hit_3 = False
                for rk, ch in enumerate(top_children[:3], 1):
                    is_match = (quote in ch["content"]) or (sub_quote and sub_quote in ch["content"])
                    if is_match:
                        if rk == 1:
                            child_hit_1 = True
                        child_hit_3 = True
                        break

                # Parent Hit (Lookup Level)
                parent_hit_1 = False
                parent_hit_3 = False
                for rk, pr in enumerate(top_parents[:3], 1):
                    is_match = (quote in pr["content"]) or (sub_quote and sub_quote in pr["content"])
                    if is_match:
                        if rk == 1:
                            parent_hit_1 = True
                        parent_hit_3 = True
                        break

                results.append({
                    "question_id": q["id"],
                    "question": q["question"],
                    "split": q["split"],
                    "gold_page": q["gold_page"],
                    "evidence_quote": q["evidence_quote"],
                    "child_hit_1": child_hit_1,
                    "child_hit_3": child_hit_3,
                    "parent_hit_1": parent_hit_1,
                    "parent_hit_3": parent_hit_3,
                    "top_child": top_children[0] if top_children else None,
                    "top_parent": top_parents[0] if top_parents else None
                })

    return results


def main():
    print("==============================================================")
    print("   THỰC NGHIỆM CHIẾN LƯỢC D: PARENT-CHILD CHUNKING & RETRIEVAL")
    print("==============================================================")
    
    t0 = time.time()
    parents, children = parse_parent_child_corpus()
    print(f"\n1. Phân Tách Phân Cấp (Hierarchical Parsing):")
    print(f"   - Số lượng Parent Chunks : {len(parents)} (Độ dài TB: {sum(p['length'] for p in parents)//len(parents):,} ký tự)")
    print(f"   - Số lượng Child Chunks  : {len(children)} (Độ dài TB: {sum(c['metadata']['length'] for c in children)//len(children):,} ký tự)")

    print(f"\n2. Tạo Embeddings cho {len(children)} Child Chunks (OpenRouter)...")
    child_texts = [c["content"] for c in children]
    t_emb = time.time()
    child_embeddings = get_embeddings(child_texts)
    print(f"   -> Đã embed thành công {len(child_embeddings)} vectors ({time.time() - t_emb:.2f}s)!")

    print(f"\n3. Khởi tạo & nạp CSDL PostgreSQL pgvector...")
    setup_database_and_store(parents, children, child_embeddings)
    print(f"   -> Đã nạp thành công vào bảng `chunks_strategy_d_parent` và `chunks_strategy_d_child`!")

    print(f"\n4. Chạy Benchmark 20 câu hỏi...")
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    q_texts = [q["question"] for q in questions]
    q_embeddings = get_embeddings(q_texts)
    
    traces = run_parent_child_retrieval(questions, q_embeddings)

    # Compute metrics
    dev_traces = [t for t in traces if t["split"] == "dev"]
    test_traces = [t for t in traces if t["split"] == "test"]

    dev_c_h1 = sum(1 for t in dev_traces if t["child_hit_1"]) / len(dev_traces) * 100
    dev_c_h3 = sum(1 for t in dev_traces if t["child_hit_3"]) / len(dev_traces) * 100
    test_c_h1 = sum(1 for t in test_traces if t["child_hit_1"]) / len(test_traces) * 100
    test_c_h3 = sum(1 for t in test_traces if t["child_hit_3"]) / len(test_traces) * 100

    dev_p_h1 = sum(1 for t in dev_traces if t["parent_hit_1"]) / len(dev_traces) * 100
    dev_p_h3 = sum(1 for t in dev_traces if t["parent_hit_3"]) / len(dev_traces) * 100
    test_p_h1 = sum(1 for t in test_traces if t["parent_hit_1"]) / len(test_traces) * 100
    test_p_h3 = sum(1 for t in test_traces if t["parent_hit_3"]) / len(test_traces) * 100

    print("\n" + "=" * 65)
    print("          KẾT QUẢ ĐỐI CHỨNG CHIẾN LƯỢC D (PARENT-CHILD)")
    print("=" * 65)
    print(f"Cấp độ Child (Bắn tỉa Khoản/Đoạn ngắn):")
    print(f"  • Dev Hit@1 : {sum(1 for t in dev_traces if t['child_hit_1'])}/15 ({dev_c_h1:.1f}%)")
    print(f"  • Dev Hit@3 : {sum(1 for t in dev_traces if t['child_hit_3'])}/15 ({dev_c_h3:.1f}%)")
    print(f"  • Test Hit@1: {sum(1 for t in test_traces if t['child_hit_1'])}/5 ({test_c_h1:.1f}%)")
    print(f"  • Test Hit@3: {sum(1 for t in test_traces if t['child_hit_3'])}/5 ({test_c_h3:.1f}%)")
    print("-" * 65)
    print(f"Cấp độ Parent (Lookup Toàn Bộ Điều Luật / Biểu Mẫu):")
    print(f"  • Dev Hit@1 : {sum(1 for t in dev_traces if t['parent_hit_1'])}/15 ({dev_p_h1:.1f}%)")
    print(f"  • Dev Hit@3 : {sum(1 for t in dev_traces if t['parent_hit_3'])}/15 ({dev_p_h3:.1f}%)")
    print(f"  • Test Hit@1: {sum(1 for t in test_traces if t['parent_hit_1'])}/5 ({test_p_h1:.1f}%)")
    print(f"  • Test Hit@3: {sum(1 for t in test_traces if t['parent_hit_3'])}/5 ({test_p_h3:.1f}%)")
    print("=" * 65)

    # Save results
    out_traces_path = RESULTS_DIR / "traces_strategy_d_parent_child.json"
    with open(out_traces_path, "w", encoding="utf-8") as f:
        json.dump(traces, f, ensure_ascii=False, indent=2)

    summary = {
        "strategy": "Strategy D (Parent-Child Retriever)",
        "num_parents": len(parents),
        "num_children": len(children),
        "child_metrics": {
            "dev_hit_1": dev_c_h1,
            "dev_hit_3": dev_c_h3,
            "test_hit_1": test_c_h1,
            "test_hit_3": test_c_h3
        },
        "parent_metrics": {
            "dev_hit_1": dev_p_h1,
            "dev_hit_3": dev_p_h3,
            "test_hit_1": test_p_h1,
            "test_hit_3": test_p_h3
        },
        "total_time_seconds": round(time.time() - t0, 2)
    }

    out_summary_path = RESULTS_DIR / "parent_child_summary.json"
    with open(out_summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu kết quả thực nghiệm tại:")
    print(f" - {out_traces_path}")
    print(f" - {out_summary_path}")


if __name__ == "__main__":
    main()
