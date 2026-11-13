"""Main pipeline orchestration for Day 06 Data Ingestion Engineering."""
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

from .models import DocumentPage, Chunk, BenchmarkQuestion
from .ingestion import load_pdf
from .chunking import chunk_strategy_a_fixed, chunk_strategy_b_paragraph
from .embeddings import get_embeddings
from .store import PgVectorStore
from .evaluation import evaluate_benchmark


def main() -> None:
    # 1. Environment & Setup
    root_dir = Path(__file__).resolve().parents[2]
    starter_dir = Path(__file__).resolve().parents[1]
    load_dotenv(starter_dir / ".env")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.exit("Error: DATABASE_URL is missing. Please check starter/.env.")

    pdf_path = starter_dir / "data" / "quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
    if not pdf_path.exists():
        sys.exit(f"Error: Source PDF not found at {pdf_path}")

    benchmark_path = root_dir / "benchmark" / "questions.json"
    if not benchmark_path.exists():
        sys.exit(f"Error: Benchmark questions not found at {benchmark_path}")

    print("=========================================================")
    print("      DAY 06 · DATA INGESTION ENGINEERING PIPELINE      ")
    print("=========================================================")

    # 2. Ingest Document
    print(f"\n[Step 1] Loading and normalizing PDF: {pdf_path.name}")
    t0 = time.time()
    pages = load_pdf(pdf_path, document_id="quy-dinh-ha-tang-khcn-hanoi-2026", source="Hanoi_Decision_2026_HN_ND")
    load_time = round(time.time() - t0, 3)
    print(f"-> Loaded {len(pages)} content pages in {load_time}s.")
    if len(pages) < 30:
        sys.exit(f"Requirement failure: Document must have >= 30 content pages, got {len(pages)}.")

    # 3. Load Benchmark Questions
    print(f"\n[Step 2] Loading benchmark questions: {benchmark_path.name}")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        raw_qs = json.load(f)
    questions = [BenchmarkQuestion(**q) for q in raw_qs]
    dev_count = sum(1 for q in questions if q.split == "dev")
    test_count = sum(1 for q in questions if q.split == "test")
    filter_count = sum(1 for q in questions if q.filter is not None)
    print(f"-> Total questions: {len(questions)} ({dev_count} dev, {test_count} test, {filter_count} with filters).")

    # 4. Generate Chunks for Strategy A & Strategy B
    print("\n[Step 3] Generating Chunks:")
    t_chunk_start = time.time()
    chunks_a = chunk_strategy_a_fixed(pages, chunk_size=500, overlap=50)
    chunks_b = chunk_strategy_b_paragraph(pages, max_length=800)
    t_chunk = round(time.time() - t_chunk_start, 3)
    print(f"-> Strategy A (Fixed 500/50):     {len(chunks_a)} chunks")
    print(f"-> Strategy B/C (Paragraph max 800): {len(chunks_b)} chunks")

    # 5. Embedding Generation
    embedding_model = os.getenv("EMBEDDING_MODEL") or "openai/text-embedding-3-small"
    print(f"\n[Step 4] Generating Embeddings using '{embedding_model}':")

    # Strategy A
    t_emb_a_start = time.time()
    print(f"-> Embedding Strategy A ({len(chunks_a)} texts)...")
    texts_a = [c.text for c in chunks_a]
    embeddings_a = get_embeddings(texts_a, model=embedding_model, batch_size=25)
    t_emb_a = round(time.time() - t_emb_a_start, 2)
    print(f"   Done in {t_emb_a}s.")

    # Strategy B/C
    t_emb_b_start = time.time()
    print(f"-> Embedding Strategy B/C ({len(chunks_b)} texts)...")
    texts_b = [c.text for c in chunks_b]
    embeddings_b = get_embeddings(texts_b, model=embedding_model, batch_size=25)
    t_emb_b = round(time.time() - t_emb_b_start, 2)
    print(f"   Done in {t_emb_b}s.")

    # 6. Database Storage in PostgreSQL + pgvector
    print("\n[Step 5] Storing vectors and metadata in PostgreSQL + pgvector:")
    store = PgVectorStore(db_url)

    table_a = "strategy_a_chunks"
    table_b = "strategy_b_chunks"

    print(f"-> Initializing table: {table_a} (dimension 1536)")
    store.init_table(table_a, dimension=1536)
    store.insert_chunks(table_a, chunks_a, embeddings_a)
    print(f"   Successfully inserted {len(chunks_a)} chunks into {table_a}.")

    print(f"-> Initializing table: {table_b} (dimension 1536)")
    store.init_table(table_b, dimension=1536)
    store.insert_chunks(table_b, chunks_b, embeddings_b)
    print(f"   Successfully inserted {len(chunks_b)} chunks into {table_b}.")

    # 7. Embedding Benchmark Questions
    print("\n[Step 6] Embedding 20 benchmark queries:")
    q_texts = [q.question for q in questions]
    q_embeddings = get_embeddings(q_texts, model=embedding_model, batch_size=20)
    q_emb_map = {q.id: emb for q, emb in zip(questions, q_embeddings)}
    print("-> 20 query embeddings generated successfully.")

    # 8. Run Retrieval Benchmark for All 3 Strategies
    print("\n[Step 7] Evaluating Retrieval Accuracy (Hit@1 & Evidence Hit@3):")

    def search_strategy_a(query: str, metadata_filter: dict = None, top_k: int = 3):
        q_id = next(q.id for q in questions if q.question == query)
        return store.search(table_a, q_emb_map[q_id], top_k=top_k, metadata_filter=None)

    def search_strategy_b(query: str, metadata_filter: dict = None, top_k: int = 3):
        q_id = next(q.id for q in questions if q.question == query)
        return store.search(table_b, q_emb_map[q_id], top_k=top_k, metadata_filter=None)

    def search_strategy_c(query: str, metadata_filter: dict = None, top_k: int = 3):
        q_id = next(q.id for q in questions if q.question == query)
        return store.search(table_b, q_emb_map[q_id], top_k=top_k, metadata_filter=metadata_filter)

    res_a = evaluate_benchmark(questions, "Strategy_A", search_strategy_a, top_k=3)
    res_b = evaluate_benchmark(questions, "Strategy_B", search_strategy_b, top_k=3)
    res_c = evaluate_benchmark(questions, "Strategy_C", search_strategy_c, top_k=3)

    # 9. Print Results Summary Table
    print("\n========================= BENCHMARK RESULTS =========================")
    print(f"{'Strategy':<12} | {'Dev Hit@1':<10} | {'Dev Hit@3':<10} | {'Test Hit@1':<10} | {'Test Hit@3':<10}")
    print("-" * 65)
    for res in [res_a, res_b, res_c]:
        print(f"{res['strategy']:<12} | {res['dev_hit1_str']:<10} | {res['dev_hit3_str']:<10} | {res['test_hit1_str']:<10} | {res['test_hit3_str']:<10}")
    print("=====================================================================")

    # 10. Save Artifacts & Traces
    results_dir = starter_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    with open(results_dir / "traces_strategy_a.json", "w", encoding="utf-8") as f:
        json.dump(res_a["traces"], f, ensure_ascii=False, indent=2)
    with open(results_dir / "traces_strategy_b.json", "w", encoding="utf-8") as f:
        json.dump(res_b["traces"], f, ensure_ascii=False, indent=2)
    with open(results_dir / "traces_strategy_c.json", "w", encoding="utf-8") as f:
        json.dump(res_c["traces"], f, ensure_ascii=False, indent=2)

    summary_data = {
        "dataset": "Quy_dinh_ha_tang_khcn_hanoi_2026.pdf",
        "total_pages": len(pages),
        "embedding_model": embedding_model,
        "results": {
            "Strategy_A": {k: v for k, v in res_a.items() if k != "traces"},
            "Strategy_B": {k: v for k, v in res_b.items() if k != "traces"},
            "Strategy_C": {k: v for k, v in res_c.items() if k != "traces"},
        },
        "timings_sec": {
            "ingest_load": load_time,
            "embed_strategy_a": t_emb_a,
            "embed_strategy_b": t_emb_b
        }
    }
    with open(results_dir / "benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    # 11. Update experiment_log.csv
    exp_log_path = root_dir / "artifacts" / "experiment_log.csv"
    with open(exp_log_path, "w", encoding="utf-8") as f:
        f.write("strategy,chunking,chunk_size,overlap,metadata,filter,vectorizer,hypothesis,dev_hit1,dev_hit3,test_hit1,test_hit3,notes\n")
        f.write(f"A,fixed_size,500,50,\"source,page,section\",no,openai/text-embedding-3-small,Fixed-size chunking baseline,{res_a['dev_hit1_str']},{res_a['dev_hit3_str']},{res_a['test_hit1_str']},{res_a['test_hit3_str']},Baseline fixed cut\n")
        f.write(f"B,paragraph_clause,800,0,\"source,page,section\",no,openai/text-embedding-3-small,Paragraph boundaries preserve clause semantics,{res_b['dev_hit1_str']},{res_b['dev_hit3_str']},{res_b['test_hit1_str']},{res_b['test_hit3_str']},Structural chunking\n")
        f.write(f"C,paragraph_clause,800,0,\"source,page,section\",yes,openai/text-embedding-3-small,Metadata filter removes cross-section noise,{res_c['dev_hit1_str']},{res_c['dev_hit3_str']},{res_c['test_hit1_str']},{res_c['test_hit3_str']},Structural + section filter\n")

    print(f"\n[Done] All traces saved to {results_dir.name}/")
    print(f"[Done] Updated {exp_log_path.name}")


if __name__ == "__main__":
    main()
