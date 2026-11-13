"""Shared data contracts; keep traceability from chunk back to source."""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DocumentPage:
    document_id: str
    source: str
    page: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    source: str
    page: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkQuestion:
    id: str
    split: str
    type: str
    question: str
    expected_answer: str
    gold_source_id: str
    gold_page: int
    evidence_quote: str
    filter: Optional[dict[str, Any]] = None


@dataclass
class RetrievalResult:
    question_id: str
    strategy: str
    split: str
    question: str
    filter_applied: Optional[dict[str, Any]]
    gold_page: int
    evidence_quote: str
    hit_1: bool
    hit_3: bool
    top_chunks: list[dict[str, Any]]
