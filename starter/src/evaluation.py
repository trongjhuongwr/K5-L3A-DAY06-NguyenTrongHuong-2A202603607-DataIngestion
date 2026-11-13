"""Evaluation metrics: Hit@1 and Evidence Hit@3 calculation and trace generation."""
import re
from typing import Any, Callable, Optional
from .models import BenchmarkQuestion, RetrievalResult


def clean_text(s: str) -> str:
    """Normalize whitespace and lowercase for reliable substring and overlap checks."""
    return " ".join(s.strip().replace("\n", " ").split()).lower()


def is_chunk_evidence_hit(chunk: dict[str, Any], gold_page: int, evidence_quote: str) -> bool:
    """Check if the chunk belongs to the gold page and contains sufficient evidence."""
    if chunk["page"] != gold_page:
        return False

    norm_quote = clean_text(evidence_quote)
    norm_content = clean_text(chunk["content"])

    # 1. Exact substring match
    if norm_quote in norm_content:
        return True

    # 2. Significant keyword overlap (>= 75% of quote words in chunk)
    quote_tokens = set(norm_quote.split())
    if not quote_tokens:
        return False
    content_tokens = set(norm_content.split())
    overlap = len(quote_tokens & content_tokens) / len(quote_tokens)
    return overlap >= 0.75


def evaluate_benchmark(
    questions: list[BenchmarkQuestion],
    strategy_name: str,
    search_func: Callable[[str, Optional[dict[str, Any]], int], list[dict[str, Any]]],
    top_k: int = 3
) -> dict[str, Any]:
    """Evaluate retrieval accuracy across Dev and Test splits for a strategy."""
    traces: list[dict[str, Any]] = []

    dev_hit1 = dev_hit3 = dev_total = 0
    test_hit1 = test_hit3 = test_total = 0

    for q in questions:
        # Determine whether this strategy applies metadata filtering
        filter_to_apply = q.filter if strategy_name == "Strategy_C" else None

        top_chunks = search_func(q.question, filter_to_apply, top_k)

        hit_1 = False
        hit_3 = False

        for rank, chunk in enumerate(top_chunks, start=1):
            if is_chunk_evidence_hit(chunk, q.gold_page, q.evidence_quote):
                hit_3 = True
                if rank == 1:
                    hit_1 = True
                break

        if q.split == "dev":
            dev_total += 1
            if hit_1:
                dev_hit1 += 1
            if hit_3:
                dev_hit3 += 1
        elif q.split == "test":
            test_total += 1
            if hit_1:
                test_hit1 += 1
            if hit_3:
                test_hit3 += 1

        traces.append({
            "question_id": q.id,
            "strategy": strategy_name,
            "split": q.split,
            "type": q.type,
            "question": q.question,
            "filter_applied": filter_to_apply,
            "gold_page": q.gold_page,
            "evidence_quote": q.evidence_quote,
            "hit_1": hit_1,
            "hit_3": hit_3,
            "top_chunks": top_chunks
        })

    return {
        "strategy": strategy_name,
        "dev_hit1_str": f"{dev_hit1}/{dev_total}",
        "dev_hit3_str": f"{dev_hit3}/{dev_total}",
        "test_hit1_str": f"{test_hit1}/{test_total}",
        "test_hit3_str": f"{test_hit3}/{test_total}",
        "dev_hit1_pct": round(dev_hit1 / max(1, dev_total) * 100, 2),
        "dev_hit3_pct": round(dev_hit3 / max(1, dev_total) * 100, 2),
        "test_hit1_pct": round(test_hit1 / max(1, test_total) * 100, 2),
        "test_hit3_pct": round(test_hit3 / max(1, test_total) * 100, 2),
        "traces": traces
    }
