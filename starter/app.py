"""Interactive Demo Web Application for Day 06 Data Ingestion Engineering.
Run with: py starter/app.py
Opens http://127.0.0.1:8080 with interactive citations, benchmark explorer, and live pgvector retrieval.
"""
import os
import sys
import json
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Path setup
ROOT_DIR = Path(__file__).resolve().parents[1]
STARTER_DIR = Path(__file__).resolve().parent
load_dotenv(STARTER_DIR / ".env")

# Preload data
RESULTS_DIR = STARTER_DIR / "results"
BENCHMARK_PATH = ROOT_DIR / "benchmark" / "questions.json"

with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
    BENCHMARK_QS = json.load(f)

with open(RESULTS_DIR / "benchmark_summary.json", "r", encoding="utf-8") as f:
    SUMMARY_DATA = json.load(f)

with open(RESULTS_DIR / "traces_strategy_a.json", "r", encoding="utf-8") as f:
    TRACES_A = {t["question_id"]: t for t in json.load(f)}

with open(RESULTS_DIR / "traces_strategy_b.json", "r", encoding="utf-8") as f:
    TRACES_B = {t["question_id"]: t for t in json.load(f)}

with open(RESULTS_DIR / "traces_strategy_c.json", "r", encoding="utf-8") as f:
    TRACES_C = {t["question_id"]: t for t in json.load(f)}


HTML_PAGE = """<!DOCTYPE html>
<html lang="vi" class="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hà Nội SciTech Policy 2026 — Data Ingestion & Retrieval Demo</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
    .highlight-evidence { background-color: rgba(254, 240, 138, 0.7); font-weight: 600; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen antialiased flex flex-col">

  <!-- Header -->
  <header class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white border-b border-indigo-800/40 sticky top-0 z-50 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-400 font-bold text-xl shadow-inner">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            Hà Nội SciTech Policy 2026
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">Day 06 Lab</span>
          </h1>
          <p class="text-xs text-indigo-200/80">Data Ingestion Engineering & High-Precision Retrieval Demo • Sinh viên: Nguyễn Trọng Hưởng (2A202603607)</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center text-xs bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"></span>
          PostgreSQL 16 + pgvector • Port 55433
        </div>
        <a href="#audit-section" class="text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg transition-colors shadow-sm">
          Xem Báo Cáo 5 Khía Cạnh
        </a>
      </div>
    </div>
  </header>

  <!-- Metric Overview Cards -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 w-full">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <!-- Card 1: Corpus Scale -->
      <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow transition-shadow">
        <div class="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
          <span>Corpus Văn Bản Số</span>
          <span class="p-1 rounded bg-slate-100 text-slate-600">40 Trang</span>
        </div>
        <div class="text-2xl font-extrabold text-slate-900">82,921 <span class="text-xs font-normal text-slate-500">ký tự</span></div>
        <p class="text-xs text-slate-600 mt-1 truncate">Quy định hạ tầng KH&CN Hà Nội (UBND 2026)</p>
        <div class="mt-2 text-[11px] text-emerald-600 font-medium flex items-center">
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          100% Digital-Native Text Layer sạch
        </div>
      </div>

      <!-- Card 2: Strategy A -->
      <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow transition-shadow">
        <div class="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
          <span>Chiến Lược A (Fixed 500)</span>
          <span class="p-1 rounded bg-amber-50 text-amber-700 text-[11px] font-bold">Baseline</span>
        </div>
        <div class="flex items-baseline justify-between">
          <div class="text-2xl font-extrabold text-slate-900">206 <span class="text-xs font-normal text-slate-500">chunks</span></div>
          <span class="text-xs font-bold text-amber-600">Dev Hit@1: 33.3%</span>
        </div>
        <p class="text-xs text-slate-600 mt-1">Dev Hit@3: 80% • Coherence: 0.9/2.0</p>
        <div class="mt-2 text-[11px] text-rose-600 font-medium flex items-center">
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          Đứt gãy câu giữa chừng ở rìa chunk
        </div>
      </div>

      <!-- Card 3: Strategy B -->
      <div class="bg-white rounded-xl border border-indigo-200/80 bg-indigo-50/20 p-4 shadow-sm hover:shadow transition-shadow">
        <div class="flex items-center justify-between text-indigo-900 text-xs font-semibold uppercase tracking-wider mb-2">
          <span>Chiến Lược B (Paragraph 800)</span>
          <span class="p-1 rounded bg-indigo-100 text-indigo-700 text-[11px] font-bold">+40% Hit@1</span>
        </div>
        <div class="flex items-baseline justify-between">
          <div class="text-2xl font-extrabold text-indigo-950">40 <span class="text-xs font-normal text-slate-500">chunks</span></div>
          <span class="text-xs font-bold text-emerald-600">Dev Hit@1: 73.3%</span>
        </div>
        <p class="text-xs text-slate-600 mt-1">Giảm 80% dung lượng • Coherence: 1.9/2.0</p>
        <div class="mt-2 text-[11px] text-emerald-700 font-medium flex items-center">
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          Bảo toàn trọn vẹn ngữ nghĩa điều khoản
        </div>
      </div>

      <!-- Card 4: Strategy C -->
      <div class="bg-white rounded-xl border border-emerald-200 bg-emerald-50/20 p-4 shadow-sm hover:shadow transition-shadow">
        <div class="flex items-center justify-between text-emerald-900 text-xs font-semibold uppercase tracking-wider mb-2">
          <span>Chiến Lược C (Targeted Filter)</span>
          <span class="p-1 rounded bg-emerald-100 text-emerald-800 text-[11px] font-bold">Tối Ưu Nhất</span>
        </div>
        <div class="flex items-baseline justify-between">
          <div class="text-2xl font-extrabold text-emerald-950">40 <span class="text-xs font-normal text-slate-500">chunks</span></div>
          <span class="text-xs font-bold text-emerald-700">100% Filter Match</span>
        </div>
        <p class="text-xs text-slate-600 mt-1">Lọc sạch 100% nhiễu ngoại lai theo section</p>
        <div class="mt-2 text-[11px] text-emerald-700 font-medium flex items-center">
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
          Không nhầm lẫn giữa các chương mục
        </div>
      </div>

    </div>
  </section>

  <!-- Interactive Explorer & Search -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex-1 w-full grid grid-cols-1 lg:grid-cols-12 gap-6">

    <!-- Left Column: Benchmark Questions List (5 cols) -->
    <div class="lg:col-span-5 flex flex-col space-y-4">
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex flex-col h-full">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 class="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              Bộ 20 Câu Hỏi Benchmark
            </h2>
            <p class="text-xs text-slate-500">Bấm câu hỏi để xem chi tiết đối chứng trích dẫn</p>
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">15 Dev / 5 Test</span>
        </div>

        <!-- Filters for questions -->
        <div class="flex items-center gap-2 pt-3 pb-1 text-xs overflow-x-auto">
          <button onclick="filterQuestions('all')" id="btn-all" class="px-2.5 py-1 rounded-md bg-indigo-600 text-white font-medium shadow-xs">Tất cả (20)</button>
          <button onclick="filterQuestions('dev')" id="btn-dev" class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium">Dev (15)</button>
          <button onclick="filterQuestions('test')" id="btn-test" class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium">Test (5)</button>
          <button onclick="filterQuestions('filtered')" id="btn-filtered" class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium flex items-center gap-1">
            <svg class="w-3 h-3 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clip-rule="evenodd"></path></svg>
            Có Filter (5)
          </button>
        </div>

        <!-- Question List Container -->
        <div class="overflow-y-auto max-h-[560px] pr-1 space-y-2.5 mt-2" id="question-list">
          <!-- Populated by JS -->
        </div>
      </div>
    </div>

    <!-- Right Column: Question Details & Citation Results (7 cols) -->
    <div class="lg:col-span-7 flex flex-col space-y-4">
      
      <!-- Live Search / Active Question Card -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div class="flex items-center gap-2" id="active-question-badges">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-700" id="badge-qid">q01</span>
            <span class="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium" id="badge-split">Dev Split</span>
            <span class="text-xs px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-medium" id="badge-gold-page">Trang Gold: Trang 2</span>
          </div>
          <!-- Strategy Switcher Tabs -->
          <div class="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100 text-xs font-medium">
            <button onclick="setStrategyTab('compare')" id="tab-compare" class="px-2.5 py-1 rounded-md bg-white text-indigo-600 font-semibold shadow-xs">So Sánh (A vs B vs C)</button>
            <button onclick="setStrategyTab('A')" id="tab-A" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">Strategy A</button>
            <button onclick="setStrategyTab('B')" id="tab-B" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">Strategy B</button>
            <button onclick="setStrategyTab('C')" id="tab-C" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900">Strategy C</button>
          </div>
        </div>

        <!-- Question text display -->
        <h3 class="text-base font-bold text-slate-900 leading-snug" id="active-question-text">
          Đang tải câu hỏi...
        </h3>

        <!-- Expected answer & Gold quote -->
        <div class="mt-3 p-3 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs space-y-1.5">
          <div><strong class="text-indigo-950">Đáp án chuẩn (Gold Answer):</strong> <span class="text-slate-700" id="active-expected">...</span></div>
          <div><strong class="text-indigo-950">Bằng chứng gốc (Evidence Quote):</strong> <span class="text-slate-700 italic bg-amber-100/70 px-1 py-0.5 rounded" id="active-evidence">...</span></div>
          <div id="active-filter-container" class="hidden"><strong class="text-indigo-950">Bộ lọc Metadata:</strong> <code class="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded" id="active-filter">...</code></div>
        </div>
      </div>

      <!-- Retrieved Chunks & Citations Container -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col flex-1">
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
          <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Kết Quả Truy Xuất Top-3 & Trích Dẫn Minh Chứng (Citations)
          </h4>
          <span class="text-xs text-slate-500 font-mono" id="results-count-badge">Top 3 Chunks</span>
        </div>

        <div id="chunks-display-area" class="space-y-4 overflow-y-auto max-h-[620px] pr-1">
          <!-- Populated by JS -->
        </div>
      </div>

    </div>

  </main>

  <!-- 5 Evaluation Dimensions Section -->
  <section id="audit-section" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full border-t border-slate-200 mt-6">
    <div class="mb-6">
      <h2 class="text-xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
        <span class="p-1.5 rounded-lg bg-indigo-600 text-white text-xs">BENCHMARK AUDIT</span>
        Phân Tích 5 Khía Cạnh Chất Lượng Ingestion & Retrieval
      </h2>
      <p class="text-sm text-slate-600 mt-1">Đánh giá thực nghiệm theo đúng quy chuẩn BENCHMARK.md và RUBRIC.md</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      
      <!-- Dimension 1: Retrieval Accuracy -->
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Khía Cạnh 1</div>
        <h3 class="text-base font-bold text-slate-900">Độ Chính Xác Truy Xuất</h3>
        <p class="text-xs text-slate-500 mt-1 mb-3">Đo lường Hit@1 và Evidence Hit@3</p>
        <div class="space-y-2 text-xs">
          <div class="flex justify-between items-center p-2 rounded bg-slate-50">
            <span class="font-medium text-slate-700">Strategy A (Fixed)</span>
            <span class="font-mono font-bold text-slate-900">Dev: 5/15 (33%) | Test: 1/5 (20%)</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded bg-indigo-50/70 border border-indigo-100">
            <span class="font-bold text-indigo-900">Strategy B (Paragraph)</span>
            <span class="font-mono font-bold text-indigo-700">Dev: 11/15 (73%) | Test: 2/5 (40%)</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded bg-emerald-50/70 border border-emerald-100">
            <span class="font-bold text-emerald-900">Strategy C (Filter)</span>
            <span class="font-mono font-bold text-emerald-700">Dev: 11/15 (73%) | Test: 2/5 (40%)</span>
          </div>
        </div>
        <p class="text-xs text-slate-600 mt-3 italic leading-relaxed">
          <strong>Nhận xét:</strong> Strategy B tăng vọt Hit@1 từ 33.3% lên 73.3% vì toàn bộ câu văn và các điểm a, b, c của điều khoản không bị đứt đoạn.
        </p>
      </div>

      <!-- Dimension 2: Chunk Coherence -->
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Khía Cạnh 2</div>
        <h3 class="text-base font-bold text-slate-900">Tính Mạch Lạc (Coherence)</h3>
        <p class="text-xs text-slate-500 mt-1 mb-3">Chấm thủ công 10 vị trí nguồn (thang 0–2)</p>
        <div class="space-y-2 text-xs">
          <div class="flex justify-between items-center p-2 rounded bg-slate-50">
            <span class="font-medium text-slate-700">Strategy A (Fixed)</span>
            <span class="font-mono font-bold text-rose-600">0.90 / 2.0 (Kém)</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded bg-emerald-50/70 border border-emerald-100">
            <span class="font-bold text-emerald-900">Strategy B & C</span>
            <span class="font-mono font-bold text-emerald-700">1.90 / 2.0 (Xuất Sắc)</span>
          </div>
        </div>
        <p class="text-xs text-slate-600 mt-3 italic leading-relaxed">
          <strong>Lý do:</strong> Strategy A cắt cứng 500 ký tự làm đứt ngang câu chữ (ví dụ Điều 1 bị đứt ở từ <em>"phát tr"</em>, Điều 10 bị cụt lửng ở chữ <em>"hoặc"</em>), trong khi Strategy B giữ nguyên ranh giới pháp lý hoàn chỉnh.
        </p>
      </div>

      <!-- Dimension 3: Metadata Usefulness -->
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Khía Cạnh 3</div>
        <h3 class="text-base font-bold text-slate-900">Tính Hữu Dụng Metadata</h3>
        <p class="text-xs text-slate-500 mt-1 mb-3">Kiểm tra 5 test x top-3 và tỷ lệ tuân thủ filter</p>
        <div class="space-y-2 text-xs">
          <div class="flex justify-between items-center p-2 rounded bg-slate-50">
            <span class="font-medium text-slate-700">Độ đúng/đủ metadata</span>
            <span class="font-mono font-bold text-emerald-700">100% (14/14 chunks)</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded bg-emerald-50/70 border border-emerald-100">
            <span class="font-bold text-emerald-900">Filter Compliance (C)</span>
            <span class="font-mono font-bold text-emerald-700">100% (1/1 câu test)</span>
          </div>
        </div>
        <p class="text-xs text-slate-600 mt-3 italic leading-relaxed">
          <strong>Hiệu quả:</strong> Ở câu q13, q14, q16, trường lọc <code>section</code> đã triệt tiêu hoàn toàn 100% các trang biểu mẫu rác (như Trang 18, Trang 31) vốn có từ khóa gây nhiễu embedding.
        </p>
      </div>

      <!-- Dimension 4: Grounding Quality -->
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Khía Cạnh 4</div>
        <h3 class="text-base font-bold text-slate-900">Chất Lượng Bằng Chứng (Grounding)</h3>
        <p class="text-xs text-slate-500 mt-1 mb-3">Độ đầy đủ để trả lời câu hỏi trên 5 câu test</p>
        <div class="space-y-2 text-xs">
          <div class="flex justify-between items-center p-2 rounded bg-slate-50">
            <span class="font-medium text-slate-700">Strategy A</span>
            <span class="font-mono font-bold text-slate-900">2.0 / 2.0 (5 câu mức 2)</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded bg-indigo-50/70 border border-indigo-100">
            <span class="font-bold text-indigo-900">Strategy B & C</span>
            <span class="font-mono font-bold text-indigo-800">1.6 / 2.0 (4 câu mức 2, 1 câu 0)</span>
          </div>
        </div>
        <p class="text-xs text-slate-600 mt-3 italic leading-relaxed">
          <strong>Chi tiết:</strong> 4/5 câu (q16, q17, q18, q19) đạt mức 2 tuyệt đối; riêng q20 (Mẫu 02) bị trượt do mô hình embedding bị thu hút sang Mẫu 04.
        </p>
      </div>

      <!-- Dimension 5: Strategy Impact -->
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm md:col-span-2">
        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Khía Cạnh 5</div>
        <h3 class="text-base font-bold text-slate-900">Tác Động & Trade-offs Chiến Lược</h3>
        <p class="text-xs text-slate-500 mt-1 mb-3">So sánh hiệu năng, chi phí và tài nguyên lưu trữ</p>
        <div class="grid grid-cols-3 gap-2 text-xs text-center mb-3">
          <div class="p-2 rounded bg-slate-100">
            <div class="text-slate-500 text-[11px]">Số lượng Chunks</div>
            <div class="font-bold text-slate-800">206 -> 40 (Giảm 80%)</div>
          </div>
          <div class="p-2 rounded bg-slate-100">
            <div class="text-slate-500 text-[11px]">Thời gian Embed</div>
            <div class="font-bold text-slate-800">21.7s -> 4.6s (Nhanh 4.7x)</div>
          </div>
          <div class="p-2 rounded bg-slate-100">
            <div class="text-slate-500 text-[11px]">Chi phí Ingest</div>
            <div class="font-bold text-slate-800">< 0.001 USD</div>
          </div>
        </div>
        <p class="text-xs text-slate-600 leading-relaxed">
          <strong>Kết luận:</strong> <strong>Chiến lược C</strong> là giải pháp tối ưu toàn diện cho môi trường sản xuất: vừa đảm bảo tốc độ và tiết kiệm chi phí vector store, vừa giữ trọn vẹn ngữ nghĩa văn bản pháp lý và ngăn chặn triệt để hiện tượng lẫn lộn điều khoản nhờ siêu dữ liệu (metadata filtering).
        </p>
      </div>

    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-white border-t border-slate-200 py-4 mt-auto text-center text-xs text-slate-500">
    Day 06 · Data Ingestion Engineering Lab • <a href="https://github.com/trongjhuongwr/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion" target="_blank" class="text-indigo-600 hover:underline">GitHub Repository</a> • Nguyễn Trọng Hưởng (2A202603607)
  </footer>

  <!-- App Logic -->
  <script>
    const benchmarkQuestions = %BENCHMARK_JSON%;
    const tracesA = %TRACES_A_JSON%;
    const tracesB = %TRACES_B_JSON%;
    const tracesC = %TRACES_C_JSON%;

    let currentFilter = 'all';
    let activeQuestionId = 'q01';
    let currentStrategyTab = 'compare';

    function init() {
      renderQuestionsList();
      selectQuestion('q01');
    }

    function filterQuestions(filterType) {
      currentFilter = filterType;
      ['all', 'dev', 'test', 'filtered'].forEach(f => {
        const btn = document.getElementById('btn-' + f);
        if (f === filterType) {
          btn.className = 'px-2.5 py-1 rounded-md bg-indigo-600 text-white font-medium shadow-xs';
        } else {
          btn.className = 'px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium';
        }
      });
      renderQuestionsList();
    }

    function renderQuestionsList() {
      const container = document.getElementById('question-list');
      container.innerHTML = '';

      benchmarkQuestions.forEach(q => {
        if (currentFilter === 'dev' && q.split !== 'dev') return;
        if (currentFilter === 'test' && q.split !== 'test') return;
        if (currentFilter === 'filtered' && !q.filter) return;

        const isSelected = (q.id === activeQuestionId);
        const card = document.createElement('div');
        card.className = `p-3 rounded-lg border text-xs cursor-pointer transition-all ${
          isSelected 
            ? 'bg-indigo-50/80 border-indigo-400/80 shadow-xs ring-1 ring-indigo-400/50' 
            : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
        }`;
        card.onclick = () => selectQuestion(q.id);

        const filterBadge = q.filter 
          ? `<span class="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-semibold">Filter: ${q.filter.section}</span>` 
          : '';

        const splitBadge = q.split === 'dev'
          ? `<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-medium">Dev</span>`
          : `<span class="px-1.5 py-0.5 rounded bg-purple-100 text-purple-700 text-[10px] font-semibold">Test</span>`;

        card.innerHTML = `
          <div class="flex items-center justify-between gap-1 mb-1.5">
            <div class="flex items-center gap-1.5">
              <span class="font-mono font-bold text-indigo-700">${q.id.toUpperCase()}</span>
              ${splitBadge}
            </div>
            <div class="flex items-center gap-1">
              ${filterBadge}
              <span class="text-[11px] text-slate-500 font-medium">Trang ${q.gold_page}</span>
            </div>
          </div>
          <p class="font-medium text-slate-800 line-clamp-2">${q.question}</p>
        `;
        container.appendChild(card);
      });
    }

    function selectQuestion(qid) {
      activeQuestionId = qid;
      const q = benchmarkQuestions.find(item => item.id === qid);
      if (!q) return;

      document.getElementById('badge-qid').innerText = q.id.toUpperCase();
      document.getElementById('badge-split').innerText = q.split === 'dev' ? 'Dev Set' : 'Test Holdout';
      document.getElementById('badge-gold-page').innerText = 'Trang Gold: Trang ' + q.gold_page;
      document.getElementById('active-question-text').innerText = q.question;
      document.getElementById('active-expected').innerText = q.expected_answer;
      document.getElementById('active-evidence').innerText = q.evidence_quote;

      const filterBox = document.getElementById('active-filter-container');
      if (q.filter) {
        filterBox.classList.remove('hidden');
        document.getElementById('active-filter').innerText = JSON.stringify(q.filter);
      } else {
        filterBox.classList.add('hidden');
      }

      renderQuestionsList();
      renderChunksArea();
    }

    function setStrategyTab(tab) {
      currentStrategyTab = tab;
      ['compare', 'A', 'B', 'C'].forEach(t => {
        const btn = document.getElementById('tab-' + t);
        if (t === tab) {
          btn.className = 'px-2.5 py-1 rounded-md bg-white text-indigo-600 font-semibold shadow-xs';
        } else {
          btn.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900';
        }
      });
      renderChunksArea();
    }

    function renderChunksArea() {
      const container = document.getElementById('chunks-display-area');
      container.innerHTML = '';

      const traceA = tracesA[activeQuestionId];
      const traceB = tracesB[activeQuestionId];
      const traceC = tracesC[activeQuestionId];
      const q = benchmarkQuestions.find(item => item.id === activeQuestionId);

      if (currentStrategyTab === 'compare') {
        // Multi-column or stacked comparison
        const compareRow = document.createElement('div');
        compareRow.className = 'grid grid-cols-1 md:grid-cols-3 gap-3';

        [
          { name: 'Strategy A (Fixed 500)', trace: traceA, color: 'amber' },
          { name: 'Strategy B (Paragraph 800)', trace: traceB, color: 'indigo' },
          { name: 'Strategy C (Targeted Filter)', trace: traceC, color: 'emerald' }
        ].forEach(s => {
          const col = document.createElement('div');
          col.className = 'border border-slate-200 rounded-lg p-3 bg-slate-50/50 flex flex-col space-y-2 text-xs';
          
          const hit1Badge = s.trace.hit_1 
            ? '<span class="text-emerald-700 bg-emerald-100 font-bold px-1.5 py-0.5 rounded text-[10px]">Hit@1: ĐẠT</span>'
            : '<span class="text-slate-600 bg-slate-200 px-1.5 py-0.5 rounded text-[10px]">Hit@1: Không</span>';
          
          const hit3Badge = s.trace.hit_3 
            ? '<span class="text-emerald-700 bg-emerald-100 font-bold px-1.5 py-0.5 rounded text-[10px]">Hit@3: ĐẠT</span>'
            : '<span class="text-rose-700 bg-rose-100 font-bold px-1.5 py-0.5 rounded text-[10px]">Hit@3: TRƯỢT</span>';

          col.innerHTML = `
            <div class="font-bold text-slate-900 pb-1.5 border-b border-slate-200 flex items-center justify-between">
              <span>${s.name}</span>
            </div>
            <div class="flex items-center gap-1.5 mb-1">${hit1Badge} ${hit3Badge}</div>
            <div class="text-[11px] text-slate-500 mb-1">Top Chunks Retrieved:</div>
          `;

          s.trace.top_chunks.forEach((chunk, idx) => {
            const isGold = (chunk.page === q.gold_page);
            const chunkBox = document.createElement('div');
            chunkBox.className = `p-2.5 rounded-md border text-[11px] ${
              isGold 
                ? 'bg-emerald-50/60 border-emerald-300 ring-1 ring-emerald-200' 
                : 'bg-white border-slate-200'
            }`;
            chunkBox.innerHTML = `
              <div class="flex items-center justify-between font-semibold mb-1">
                <span class="${isGold ? 'text-emerald-800' : 'text-slate-700'}">#${idx+1} Trang ${chunk.page} • Điều ${chunk.page}</span>
                <span class="font-mono text-slate-500">${chunk.score}</span>
              </div>
              <div class="line-clamp-4 text-slate-600 font-sans text-[11px] leading-relaxed">${formatChunkText(chunk.content, q.evidence_quote)}</div>
            `;
            col.appendChild(chunkBox);
          });

          compareRow.appendChild(col);
        });

        container.appendChild(compareRow);
      } else {
        // Detailed single strategy view
        let selectedTrace = traceA;
        let stratName = 'Strategy A (Fixed-size 500/50)';
        if (currentStrategyTab === 'B') { selectedTrace = traceB; stratName = 'Strategy B (Paragraph/Clause max 800)'; }
        if (currentStrategyTab === 'C') { selectedTrace = traceC; stratName = 'Strategy C (Paragraph + Metadata Filter)'; }

        const headerBar = document.createElement('div');
        headerBar.className = 'flex items-center justify-between p-3 rounded-lg bg-indigo-50 border border-indigo-100 text-xs font-medium text-indigo-900 mb-2';
        headerBar.innerHTML = `
          <span>Đang xem chi tiết: <strong>${stratName}</strong></span>
          <div class="flex gap-2 font-mono">
            <span>Hit@1: <strong>${selectedTrace.hit_1 ? 'YES' : 'NO'}</strong></span>
            <span>Hit@3: <strong>${selectedTrace.hit_3 ? 'YES' : 'NO'}</strong></span>
          </div>
        `;
        container.appendChild(headerBar);

        selectedTrace.top_chunks.forEach((chunk, idx) => {
          const isGold = (chunk.page === q.gold_page);
          const chunkCard = document.createElement('div');
          chunkCard.className = `p-4 rounded-xl border transition-all ${
            isGold 
              ? 'bg-emerald-50/40 border-emerald-300 shadow-xs' 
              : 'bg-white border-slate-200'
          }`;

          const sectionBadge = chunk.metadata && chunk.metadata.section
            ? `<span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">section: ${chunk.metadata.section}</span>`
            : '';

          const rankBadge = idx === 0 
            ? '<span class="px-2 py-0.5 rounded-md bg-indigo-600 text-white font-bold text-xs">#1 Top Match</span>'
            : `<span class="px-2 py-0.5 rounded-md bg-slate-200 text-slate-700 font-bold text-xs">#${idx+1} Retrieved</span>`;

          const citationPill = `
            <div class="flex flex-wrap items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-200/60">
              <div class="flex items-center gap-2">
                ${rankBadge}
                <span class="font-bold text-slate-900 text-xs">📄 Văn bản UBND TP Hà Nội 2026 • <strong>Trang ${chunk.page} / 40</strong></span>
                ${sectionBadge}
              </div>
              <div class="flex items-center gap-2">
                ${isGold ? '<span class="text-xs font-bold text-emerald-700 flex items-center"><svg class="w-4 h-4 mr-1 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg> Gold Page Hit</span>' : ''}
                <span class="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-semibold">Cosine Sim: ${chunk.score}</span>
              </div>
            </div>
          `;

          chunkCard.innerHTML = `
            ${citationPill}
            <div class="text-xs text-slate-700 leading-relaxed font-sans mt-2 whitespace-pre-wrap">${formatChunkText(chunk.content, q.evidence_quote)}</div>
            <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>Chunk ID: ${chunk.chunk_id}</span>
              <span>Độ dài: ${chunk.content.length} ký tự</span>
            </div>
          `;
          container.appendChild(chunkCard);
        });
      }
    }

    function formatChunkText(content, quote) {
      if (!quote) return escapeHtml(content);
      const cleanQuote = quote.trim().split('\\n')[0];
      if (content.toLowerCase().includes(cleanQuote.toLowerCase())) {
        const regex = new RegExp(`(${escapeRegex(cleanQuote)})`, 'gi');
        return escapeHtml(content).replace(regex, '<mark class="highlight-evidence">$1</mark>');
      }
      return escapeHtml(content);
    }

    function escapeHtml(text) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
      return text.replace(/[&<>"']/g, m => map[m]);
    }

    function escapeRegex(string) {
      return string.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
    }

    window.onload = init;
  </script>
</body>
</html>
"""

# Inject serialized JSON into the HTML template
HTML_PAGE = HTML_PAGE.replace("%BENCHMARK_JSON%", json.dumps(BENCHMARK_QS, ensure_ascii=False))
HTML_PAGE = HTML_PAGE.replace("%TRACES_A_JSON%", json.dumps(TRACES_A, ensure_ascii=False))
HTML_PAGE = HTML_PAGE.replace("%TRACES_B_JSON%", json.dumps(TRACES_B, ensure_ascii=False))
HTML_PAGE = HTML_PAGE.replace("%TRACES_C_JSON%", json.dumps(TRACES_C, ensure_ascii=False))


class DemoServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        demo_file = STARTER_DIR / "data_ingestion_demo.html"
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if demo_file.exists():
                with open(demo_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/summary":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(SUMMARY_DATA, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/questions":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(BENCHMARK_QS, ensure_ascii=False).encode("utf-8"))
        elif self.path.startswith("/api/pdf"):
            pdf_path = STARTER_DIR / "data" / "quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
            if pdf_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", "inline; filename=quy_dinh_ha_tang_khcn_hanoi_2026.pdf")
                self.end_headers()
                with open(pdf_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"PDF Not Found")
        elif self.path.startswith("/api/query"):
            # Live search endpoint against pgvector
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            q_text = query_params.get("q", [""])[0]
            strat = query_params.get("strategy", ["b"])[0].lower()
            table_name = "chunks_strategy_b" if strat == "b" else ("chunks_strategy_c" if strat == "c" else "chunks_strategy_a")
            
            try:
                from src.embeddings import get_embeddings
                from src.store import search_similar_chunks
                query_emb = get_embeddings([q_text])[0]
                results = search_similar_chunks(table_name, query_emb, top_k=3)
                resp = {"query": q_text, "strategy": strat, "results": results}
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


def run_server(port: int = 8080):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, DemoServerHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n=======================================================")
    print(f"  DAY 06 DEMO SERVER IS RUNNING AT: {url}")
    print(f"=======================================================")
    print("Press Ctrl+C to stop the server.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
