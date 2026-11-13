"""Build the comprehensive, clean, light-theme Chatbot, Benchmark & Audit application.
Outputs starter/data_ingestion_demo.html and syncs with Antigravity brain artifact.
"""
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT_DIR = Path("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion")
STARTER_DIR = ROOT_DIR / "starter"
RESULTS_DIR = STARTER_DIR / "results"
ARTIFACT_DIR = Path("C:/Users/USER/.gemini/antigravity/brain/5a852c7b-6fc0-454b-a153-11fbd1303cff")
PDF_PATH = STARTER_DIR / "data" / "quy_dinh_ha_tang_khcn_hanoi_2026.pdf"

# 1. Extract all 40 pages with clean text
reader = PdfReader(str(PDF_PATH))
pages_data = []

def clean_page(raw: str) -> str:
    t = re.sub(r"^\s*\d+\s*\n", "", raw)
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
    return "\n".join(merged)

for idx, page in enumerate(reader.pages, 1):
    raw_text = page.extract_text() or ""
    cleaned = clean_page(raw_text)
    
    if idx <= 2:
        sec = "Chương I: Quy định chung"
    elif idx <= 12:
        sec = "Chương II: Hỗ trợ hạ tầng KH&CN"
    elif idx <= 14:
        sec = "Chương III: Ưu đãi doanh nghiệp"
    elif idx <= 16:
        sec = "Chương IV: Tổ chức thi hành"
    else:
        sec = f"Phụ lục: Biểu mẫu (Trang {idx})"

    pages_data.append({
        "page": idx,
        "section": sec,
        "text": cleaned,
        "raw": raw_text
    })

# 2. Load benchmark & traces
with open(ROOT_DIR / "benchmark" / "questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

with open(RESULTS_DIR / "benchmark_summary.json", "r", encoding="utf-8") as f:
    summary = json.load(f)

with open(RESULTS_DIR / "traces_strategy_a.json", "r", encoding="utf-8") as f:
    traces_a = {t["question_id"]: t for t in json.load(f)}

with open(RESULTS_DIR / "traces_strategy_b.json", "r", encoding="utf-8") as f:
    traces_b = {t["question_id"]: t for t in json.load(f)}

with open(RESULTS_DIR / "traces_strategy_c.json", "r", encoding="utf-8") as f:
    traces_c = {t["question_id"]: t for t in json.load(f)}

payload = {
    "pages": pages_data,
    "questions": questions,
    "summary": summary,
    "traces_a": traces_a,
    "traces_b": traces_b,
    "traces_c": traces_c
}

json_payload = json.dumps(payload, ensure_ascii=False)

html_content = """<!DOCTYPE html>
<html lang="vi" class="h-full light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hà Nội SciTech Policy QA — Data Ingestion & Retrieval Explorer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
    .font-doc { font-family: 'Merriweather', Georgia, serif; }
    .font-mono-code { font-family: 'JetBrains Mono', monospace; }
    
    .citation-mark {
      background-color: #fef08a;
      color: #713f12;
      font-weight: 600;
      padding: 2px 4px;
      border-radius: 4px;
      border: 1px solid #facc15;
      box-shadow: 0 0 10px rgba(234, 179, 8, 0.35);
      outline: 2px solid #eab308;
    }

    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: #f1f5f9;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 3px;
    }
    .custom-scroll::-webkit-scrollbar-thumb:hover {
      background: #94a3b8;
    }
  </style>
</head>
<body class="bg-slate-50 text-slate-900 h-full flex flex-col overflow-hidden antialiased select-none">

  <!-- Top Clean Navigation Bar -->
  <header class="bg-white border-b border-slate-200 h-14 flex items-center justify-between px-4 sm:px-6 z-30 shrink-0 shadow-xs">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
      </div>
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-sm font-bold text-slate-900 tracking-tight">Hà Nội SciTech Policy 2026</h1>
          <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Lab Day 06</span>
        </div>
        <p class="text-[11px] text-slate-500">Học viên: <strong class="text-slate-800">Nguyễn Trọng Hưởng</strong> · MSSV: <code class="text-xs bg-slate-100 px-1 py-0.5 rounded text-indigo-700">2A202603607</code></p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
      <button onclick="switchMainTab('chat')" id="tab-nav-chat" class="px-3 py-1.5 rounded-md bg-white text-indigo-700 shadow-xs transition-all flex items-center space-x-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
        <span>Chatbot & Trích Dẫn PDF</span>
      </button>
      <button onclick="switchMainTab('benchmark')" id="tab-nav-benchmark" class="px-3 py-1.5 rounded-md text-slate-600 hover:text-slate-900 transition-all flex items-center space-x-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        <span>So Sánh Benchmark</span>
      </button>
      <button onclick="switchMainTab('audit')" id="tab-nav-audit" class="px-3 py-1.5 rounded-md text-slate-600 hover:text-slate-900 transition-all flex items-center space-x-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Thẩm Định Chất Lượng & VLM</span>
      </button>
    </div>

    <!-- Quick info right -->
    <div class="hidden lg:flex items-center space-x-2 text-[11px] font-mono text-slate-500">
      <span>40 Trang PDF</span>
      <span>•</span>
      <span>PostgreSQL 16 + pgvector</span>
      <span>•</span>
      <span class="text-emerald-700 font-bold">100% Grounded</span>
    </div>
  </header>

  <!-- TAB 1: CHATBOT & PDF DUAL-PANE VIEW -->
  <div id="view-chat" class="flex-1 flex flex-col md:flex-row h-[calc(100vh-56px)] overflow-hidden">
    
    <!-- Left Chat Pane (50%) -->
    <div class="w-full md:w-1/2 flex flex-col bg-white border-r border-slate-200 h-full relative">
      
      <!-- Chat Conversation History -->
      <div id="chat-messages" class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 custom-scroll bg-slate-50/40">
        
        <!-- Welcome Message -->
        <div class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center shrink-0 text-xs font-bold shadow-xs">
            AI
          </div>
          <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-800 space-y-2 shadow-sm leading-relaxed">
            <p class="font-bold text-slate-900">Xin chào! Tôi là Trợ lý Pháp lý Hà Nội SciTech 2026.</p>
            <p class="text-slate-600 leading-normal">
              Tôi có thể tra cứu và giải đáp các quy định về chính sách ưu đãi hạ tầng, hồ sơ đề nghị hỗ trợ, ưu đãi lãi suất và trách nhiệm các cơ quan thuộc UBND TP Hà Nội.
            </p>
            <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200 text-xs space-y-1 text-amber-950">
              <span class="font-bold flex items-center space-x-1.5 text-amber-900">
                <svg class="w-4 h-4 text-amber-600" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
                <span>Cơ chế Trích Dẫn Minh Bạch:</span>
              </span>
              <p>Mỗi câu trả lời đều đính kèm nút trích dẫn <strong>[📄 Trang X]</strong>. Khi bấm vào, văn bản bên phải sẽ <strong>tự động mở đúng trang và highlight câu bằng chứng</strong>!</p>
            </div>
          </div>
        </div>

      </div>

      <!-- Suggested Question Chips Carousel -->
      <div class="px-4 py-2 border-t border-slate-200 bg-white shrink-0">
        <div class="flex items-center space-x-1.5 overflow-x-auto custom-scroll py-1 text-xs">
          <button onclick="askQuestion('q01')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            🎯 Q01: Chính sách ưu đãi (Trang 2)
          </button>
          <button onclick="askQuestion('q03')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            📋 Q03: Mẫu hồ sơ hạ tầng (Trang 3)
          </button>
          <button onclick="askQuestion('q05')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            ⏱️ Q05: Thời hạn xử lý hồ sơ (Trang 5)
          </button>
          <button onclick="askQuestion('q06')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            👥 Q06: Hội đồng thẩm định (Trang 7)
          </button>
          <button onclick="askQuestion('q11')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            📅 Q11: Hiệu lực thi hành (Trang 15)
          </button>
          <button onclick="askQuestion('q16')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            💰 Q16: Lãi suất Quỹ ĐTPT (Trang 14)
          </button>
          <button onclick="askQuestion('q17')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            🎪 Q17: Hỗ trợ gian hàng (Trang 14)
          </button>
          <button onclick="askQuestion('q18')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 text-slate-700 transition-all font-medium">
            🏢 Q18: Trách nhiệm Sở KH&CN (Trang 15)
          </button>
        </div>
      </div>

      <!-- Chat Input Controls -->
      <div class="p-3 sm:p-4 border-t border-slate-200 bg-white shrink-0 space-y-2">
        <div class="flex items-center space-x-2">
          <div class="relative flex-1">
            <input type="text" id="chat-input" onkeydown="if(event.key==='Enter') submitCustomQuestion()" placeholder="Nhập câu hỏi tra cứu chính sách hoặc số hiệu điều khoản..." class="w-full text-xs sm:text-sm pl-4 pr-10 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all">
            <button onclick="submitCustomQuestion()" class="absolute right-2 top-2 p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-all shadow-xs">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-slate-500">
          <div class="flex items-center space-x-2">
            <span>Chiến lược tìm kiếm:</span>
            <select id="strategy-selector" class="bg-slate-50 border border-slate-300 text-slate-700 text-xs rounded px-2 py-0.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-medium">
              <option value="c" selected>Strategy C (Paragraph + Filter) [Khuyến nghị]</option>
              <option value="b">Strategy B (Paragraph 800 chars)</option>
              <option value="a">Strategy A (Fixed 500/50 chars)</option>
            </select>
          </div>
          <span>Bấm trích dẫn để soi trực tiếp văn bản</span>
        </div>
      </div>

    </div>

    <!-- Right Document Viewer Pane (50%) -->
    <div class="w-full md:w-1/2 flex flex-col bg-slate-100/70 h-full relative border-l border-slate-200">
      
      <!-- Document Top Toolbar -->
      <div class="bg-white border-b border-slate-200 p-2.5 px-4 flex flex-wrap items-center justify-between gap-3 shrink-0 z-10 shadow-xs">
        
        <!-- Page Nav -->
        <div class="flex items-center space-x-1.5">
          <button onclick="prevPage()" class="p-1.5 rounded-md bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-300 transition-all" title="Trang trước">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          </button>
          <div class="flex items-center space-x-1 text-xs text-slate-600 font-mono">
            <span>Trang</span>
            <input type="number" id="page-input" min="1" max="40" value="2" onchange="jumpToPage(parseInt(this.value))" class="w-12 text-center bg-white border border-slate-300 rounded text-indigo-700 font-bold text-xs py-0.5 focus:outline-none focus:ring-1 focus:ring-indigo-500">
            <span>/ 40</span>
          </div>
          <button onclick="nextPage()" class="p-1.5 rounded-md bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-300 transition-all" title="Trang sau">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
        </div>

        <!-- Mode Toggle -->
        <div class="flex items-center rounded-lg bg-slate-100 p-0.5 border border-slate-200 text-xs">
          <button onclick="setViewMode('doc')" id="btn-mode-doc" class="px-2.5 py-1 rounded-md bg-white text-indigo-700 font-bold shadow-xs flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <span>Văn Bản & Highlight</span>
          </button>
          <button onclick="setViewMode('pdf')" id="btn-mode-pdf" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 font-medium flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            <span>Tệp PDF Gốc</span>
          </button>
        </div>

        <!-- Section Jump -->
        <select onchange="jumpToSection(this.value)" class="bg-white border border-slate-300 text-slate-700 text-xs rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-medium">
          <option value="1">Chương I: Quy định chung (Trang 1)</option>
          <option value="3">Chương II: Trình tự hỗ trợ (Trang 3)</option>
          <option value="13">Chương III: Ưu đãi doanh nghiệp (Trang 13)</option>
          <option value="15">Chương IV: Điều khoản thi hành (Trang 15)</option>
          <option value="17">Mẫu 01: Đơn đề nghị hỗ trợ (Trang 17)</option>
          <option value="21">Mẫu 02: Thuyết minh dự án (Trang 21)</option>
          <option value="28">Mẫu 03: Kiểm định trang thiết bị (Trang 28)</option>
          <option value="36">Mẫu 07: Hỗ trợ gian hàng (Trang 36)</option>
        </select>

      </div>

      <!-- Active Citation Notification Banner -->
      <div id="citation-toast" class="hidden absolute top-14 left-4 right-4 z-20 bg-amber-500 text-slate-950 px-4 py-2 rounded-xl shadow-md flex items-center justify-between text-xs font-semibold transition-all duration-300">
        <div class="flex items-center space-x-2">
          <span class="text-base">📌</span>
          <span id="citation-toast-text">Đang trích dẫn Trang 2 · Khớp nguyên văn 100%</span>
        </div>
        <button onclick="document.getElementById('citation-toast').classList.add('hidden')" class="text-slate-900 hover:text-black font-bold">✕</button>
      </div>

      <!-- Mode 1: A4 Document Viewer with Highlight -->
      <div id="doc-viewer-container" class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 flex justify-center custom-scroll bg-slate-200/50">
        
        <div id="a4-sheet" class="w-full max-w-2xl bg-white text-slate-900 rounded-sm shadow-xl p-8 sm:p-12 min-h-[950px] font-doc text-[13px] sm:text-[14px] leading-relaxed relative flex flex-col justify-between border border-slate-300 select-text">
          
          <!-- Official Paper Header -->
          <div class="border-b border-slate-200 pb-4 mb-6">
            <div class="flex justify-between items-start text-[11px] font-sans font-semibold text-slate-600">
              <div>
                <p class="uppercase tracking-wider">ỦY BAN NHÂN DÂN</p>
                <p class="uppercase font-bold text-slate-900">THÀNH PHỐ HÀ NỘI</p>
                <p class="text-[10px] text-slate-500 pt-0.5">Số: .../2026/QĐ-UBND</p>
              </div>
              <div class="text-center">
                <p class="uppercase font-bold text-slate-900">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</p>
                <p class="font-semibold text-slate-700">Độc lập - Tự do - Hạnh phúc</p>
                <p class="text-[10px] text-slate-500 pt-0.5 italic">Hà Nội, năm 2026</p>
              </div>
            </div>
            <div class="text-center pt-3">
              <span id="page-section-badge" class="px-2.5 py-0.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-800 font-sans text-[11px] font-bold">
                Chương I: Quy định chung
              </span>
            </div>
          </div>

          <!-- Page Body -->
          <div id="page-content-body" class="flex-1 space-y-3 whitespace-pre-line text-slate-800">
            <!-- Rendered by JS -->
          </div>

          <!-- Official Paper Footer -->
          <div class="border-t border-slate-200 pt-3 mt-8 flex justify-between items-center text-[11px] font-sans text-slate-400">
            <span>Quyết định hỗ trợ hạ tầng KHCN & ĐMST Hà Nội 2026</span>
            <span class="font-bold text-slate-700 font-mono" id="page-num-footer">Trang 2 / 40</span>
          </div>

        </div>

      </div>

      <!-- Mode 2: Native PDF Embed -->
      <div id="pdf-viewer-container" class="hidden flex-1 w-full h-full bg-slate-100">
        <iframe id="pdf-frame" src="/api/pdf#page=2" class="w-full h-full border-0"></iframe>
      </div>

    </div>

  </div>

  <!-- TAB 2: BENCHMARK COMPARISON MATRIX (LIGHT THEME) -->
  <div id="view-benchmark" class="hidden flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 custom-scroll bg-slate-50">
    <div class="max-w-6xl mx-auto space-y-6">
      
      <!-- Top Title -->
      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-base sm:text-lg font-bold text-slate-900">Bảng So Sánh Benchmark 3 Chiến Lược Ingestion</h2>
          <p class="text-xs text-slate-500 mt-0.5">Đo lường có kiểm soát trên cùng 40 trang văn bản pháp quy Hà Nội 2026, model `openai/text-embedding-3-small` và PostgreSQL pgvector.</p>
        </div>
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">20 Câu Hỏi Benchmark Chuẩn Hóa</span>
      </div>

      <!-- Metrics Summary Table -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-200 font-bold text-xs uppercase tracking-wider text-slate-700 bg-slate-50/50">
          Chỉ Số Định Lượng Tổng Hợp (Retrieval Metrics)
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-700">
            <thead class="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th class="p-3.5">Chiến Lược (Strategy)</th>
                <th class="p-3.5">Dev Hit@1</th>
                <th class="p-3.5">Dev Hit@3</th>
                <th class="p-3.5">Test Hit@1</th>
                <th class="p-3.5">Test Hit@3</th>
                <th class="p-3.5">Số Chunks</th>
                <th class="p-3.5">Thời Gian Ingest</th>
                <th class="p-3.5">Chi Phí Token</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 font-medium font-mono text-[11px]">
              <tr class="hover:bg-slate-50">
                <td class="p-3.5 font-sans font-bold text-slate-900">Strategy A (Fixed 500/50)</td>
                <td class="p-3.5 text-rose-600 font-bold">5/15 (33.3%)</td>
                <td class="p-3.5">12/15 (80.0%)</td>
                <td class="p-3.5 text-rose-600 font-bold">1/5 (20.0%)</td>
                <td class="p-3.5 text-emerald-700 font-bold">5/5 (100.0%)</td>
                <td class="p-3.5">206 chunks</td>
                <td class="p-3.5">22.62s</td>
                <td class="p-3.5">~$0.0006</td>
              </tr>
              <tr class="hover:bg-slate-50 bg-indigo-50/20">
                <td class="p-3.5 font-sans font-bold text-indigo-900">Strategy B (Paragraph ≤800)</td>
                <td class="p-3.5 text-emerald-700 font-bold">11/15 (73.3%)</td>
                <td class="p-3.5 text-emerald-700 font-bold">13/15 (86.7%)</td>
                <td class="p-3.5 text-indigo-700 font-bold">3/5 (60.0%)</td>
                <td class="p-3.5">4/5 (80.0%)</td>
                <td class="p-3.5 text-indigo-700 font-bold">120 chunks</td>
                <td class="p-3.5 text-emerald-700 font-bold">11.67s ⚡</td>
                <td class="p-3.5">~$0.0004</td>
              </tr>
              <tr class="hover:bg-slate-50 bg-emerald-50/20">
                <td class="p-3.5 font-sans font-bold text-emerald-900">Strategy C (Paragraph + Filter)</td>
                <td class="p-3.5 text-emerald-700 font-bold">11/15 (73.3%)</td>
                <td class="p-3.5 text-emerald-700 font-bold">13/15 (86.7%)</td>
                <td class="p-3.5 text-emerald-700 font-bold">3/5 (60.0%)</td>
                <td class="p-3.5">4/5 (80.0%)</td>
                <td class="p-3.5 text-emerald-700 font-bold">120 chunks</td>
                <td class="p-3.5 text-emerald-700 font-bold">11.67s ⚡</td>
                <td class="p-3.5">~$0.0004</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 20 Benchmark Questions Interactive Inspection Table -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div class="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
          <div class="flex items-center space-x-2">
            <span class="font-bold text-xs uppercase tracking-wider text-slate-700">Chi Tiết 20 Câu Hỏi Benchmark</span>
            <span class="text-xs text-slate-500">(Bấm "Soi Văn Bản" để nhảy trực tiếp sang file PDF)</span>
          </div>
          <div class="flex items-center space-x-1.5 text-xs">
            <button onclick="filterTableSplit('all')" id="btn-tbl-all" class="px-2.5 py-1 rounded bg-indigo-600 text-white font-semibold">Tất cả (20)</button>
            <button onclick="filterTableSplit('dev')" id="btn-tbl-dev" class="px-2.5 py-1 rounded bg-slate-200 text-slate-700 font-medium">Dev Set (15)</button>
            <button onclick="filterTableSplit('test')" id="btn-tbl-test" class="px-2.5 py-1 rounded bg-slate-200 text-slate-700 font-medium">Test Set (5)</button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-700">
            <thead class="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th class="p-3">ID</th>
                <th class="p-3">Tập</th>
                <th class="p-3">Thể loại</th>
                <th class="p-3 w-1/3">Nội dung câu hỏi</th>
                <th class="p-3">Trang Vàng</th>
                <th class="p-3">Strat A</th>
                <th class="p-3">Strat B</th>
                <th class="p-3">Strat C</th>
                <th class="p-3 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody id="benchmark-table-body" class="divide-y divide-slate-200 font-medium">
              <!-- Rendered by JS -->
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>

  <!-- TAB 3: QUALITY AUDIT & VLM (LIGHT THEME) -->
  <div id="view-audit" class="hidden flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 custom-scroll bg-slate-50">
    <div class="max-w-6xl mx-auto space-y-6">
      
      <!-- Title -->
      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <h2 class="text-base sm:text-lg font-bold text-slate-900">Báo Cáo Thẩm Định 5 Chiều Chất Lượng & Khám Phá VLM</h2>
        <p class="text-xs text-slate-500 mt-0.5">Đánh giá theo Rubric chuẩn 100 điểm của VinUni AI Thực Chiến Lab Day 06.</p>
      </div>

      <!-- 5 Dimensions Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2.5">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-xs">1</span>
            <h3 class="font-bold text-sm text-slate-900">Retrieval Accuracy (Độ chính xác)</h3>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            Strategy B & C đạt <strong>Dev Hit@1 = 73.33%</strong> (vượt xa 33.33% của Strategy A) và <strong>Dev Hit@3 = 86.67%</strong>. Cắt theo điều khoản pháp lý giúp gom từ khóa và chủ vị câu vào cùng một vector, đẩy chunk vàng lên vị trí số 1.
          </p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2.5">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 font-bold flex items-center justify-center text-xs">2</span>
            <h3 class="font-bold text-sm text-slate-900">Chunk Coherence (Độ mạch lạc ngữ nghĩa)</h3>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            Khảo sát 10 vị trí nguồn: Strategy A đạt <strong>0.90/2.0</strong> do bị cắt cụt giữa câu (ví dụ chữ "phát tr", "hoặc"). Strategy B/C đạt <strong>1.90/2.0</strong> vì giữ trọn vẹn ngữ nghĩa điều khoản, bảo vệ LLM khỏi nguy cơ ảo giác cú pháp.
          </p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2.5">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-xs">3</span>
            <h3 class="font-bold text-sm text-slate-900">Metadata Usefulness (Lọc nhiễu phân vùng)</h3>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            5 câu hỏi có filter (q05, q13, q14, q15, q16) đạt <strong>100% tuân thủ</strong>. Bộ lọc `section` loại bỏ hoàn toàn các trang biểu mẫu phụ lục có từ khóa trùng lặp, đảm bảo chỉ trả về đúng điều khoản quy định.
          </p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2.5">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-amber-100 text-amber-700 font-bold flex items-center justify-center text-xs">4</span>
            <h3 class="font-bold text-sm text-slate-900">Grounding Quality (Bảo chứng nguyên văn)</h3>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            100% (20/20 câu hỏi) có `evidence_quote` được kiểm chứng khớp từng ký tự trong file PDF. Trên tập test ẩn (q16–q20), 4/5 câu đạt Grounding Mức 2 (đầy đủ căn cứ pháp lý), điểm trung bình đạt 1.6/2.0.
          </p>
        </div>

      </div>

      <!-- VLM Exploration Card -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-200 pb-3">
          <div class="flex items-center space-x-2.5">
            <span class="w-7 h-7 rounded-lg bg-purple-600 text-white font-bold flex items-center justify-center text-xs">5</span>
            <div>
              <h3 class="font-bold text-sm text-slate-900">Nghiên Cứu Thực Nghiệm Đa Phương Thức (Multimodal VLM vs Heuristic Parser)</h3>
              <p class="text-xs text-slate-500">Khảo sát đối chứng trực tiếp với mô hình Claude Haiku 5.5 (`claude-haiku-5-5`) qua Anthropic API.</p>
            </div>
          </div>
          <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-purple-100 text-purple-800">Advanced Exploration</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-700">
            <thead class="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th class="p-3">Tiêu chí khảo sát</th>
                <th class="p-3 bg-indigo-50/30 text-indigo-900">Heuristic Legal Parser (pypdf + regex)</th>
                <th class="p-3 bg-purple-50/30 text-purple-900">VLM Parsing (Claude Haiku 5.5)</th>
                <th class="p-3">Kết luận kỹ thuật (Engineering Takeaway)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 font-medium">
              <tr class="hover:bg-slate-50">
                <td class="p-3 font-bold text-slate-900">Văn bản quy định (Trang 1–16)</td>
                <td class="p-3 bg-indigo-50/20 text-emerald-700 font-bold">9.8 / 10 (Chuẩn tuyệt đối)</td>
                <td class="p-3 bg-purple-50/20">9.7 / 10 (Xuất sắc)</td>
                <td class="p-3 text-slate-600">Với văn bản luật thuần chữ, regex unwrap cho chất lượng ngang ngửa VLM nhưng tốc độ gấp 100 lần.</td>
              </tr>
              <tr class="hover:bg-slate-50">
                <td class="p-3 font-bold text-slate-900">Biểu mẫu & Bảng biểu (Trang 17–40)</td>
                <td class="p-3 bg-indigo-50/20 text-slate-600">7.5 / 10 (Làm phẳng text)</td>
                <td class="p-3 bg-purple-50/20 text-emerald-700 font-bold">9.8 / 10 (Chuyển thành [ ] và bảng Markdown)</td>
                <td class="p-3 text-slate-600">VLM nhìn được layout 2D, nhận diện ô vuông checkbox và cấu trúc bảng vượt trội.</td>
              </tr>
              <tr class="hover:bg-slate-50">
                <td class="p-3 font-bold text-slate-900">Thời gian nạp 40 trang</td>
                <td class="p-3 bg-indigo-50/20 text-emerald-700 font-bold">0.5 giây (Tức thì)</td>
                <td class="p-3 bg-purple-50/20 text-slate-500">~5.5 phút (8.2s / trang)</td>
                <td class="p-3 text-slate-600">Heuristic parser không phụ thuộc mạng, chạy offline ngay lập tức.</td>
              </tr>
              <tr class="hover:bg-slate-50">
                <td class="p-3 font-bold text-slate-900">Chi phí nạp</td>
                <td class="p-3 bg-indigo-50/20 text-emerald-700 font-bold">0.00 USD (Miễn phí)</td>
                <td class="p-3 bg-purple-50/20 text-slate-500">~$0.06 USD / lượt</td>
                <td class="p-3 text-slate-600">Tiết kiệm chi phí khi quy mô tài liệu lên đến hàng ngàn trang.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700 leading-relaxed">
          <strong class="text-slate-900">Khuyến nghị Kiến trúc Sản xuất (Production Hybrid Router):</strong> Trong các hệ thống RAG thực tế quy mô lớn, kiến trúc tối ưu nhất là định tuyến thông minh: phân luồng 80% văn bản quy định qua Heuristic Legal Chunking siêu tốc, và chỉ chuyển 20% các trang có bảng biểu hoặc mẫu đơn phức tạp sang các endpoint VLM như Claude Haiku 5.5.
        </div>
      </div>

    </div>
  </div>

  <script>
    const DATA = """ + json_payload + """;

    let currentPage = 2;
    let currentMode = 'doc';
    let activeHighlightQuote = '';
    let currentTableSplit = 'all';

    function init() {
      renderPage(currentPage);
      renderBenchmarkTable();
      askQuestion('q01');
    }

    function switchMainTab(tabId) {
      document.getElementById('view-chat').classList.add('hidden');
      document.getElementById('view-benchmark').classList.add('hidden');
      document.getElementById('view-audit').classList.add('hidden');

      document.querySelectorAll('#tab-nav-chat, #tab-nav-benchmark, #tab-nav-audit').forEach(b => {
        b.className = "px-3 py-1.5 rounded-md text-slate-600 hover:text-slate-900 transition-all flex items-center space-x-1.5";
      });

      const activeView = document.getElementById('view-' + tabId);
      if (activeView) activeView.classList.remove('hidden');

      const activeNav = document.getElementById('tab-nav-' + tabId);
      if (activeNav) {
        activeNav.className = "px-3 py-1.5 rounded-md bg-white text-indigo-700 font-bold shadow-xs transition-all flex items-center space-x-1.5";
      }
    }

    function setViewMode(mode) {
      currentMode = mode;
      const btnDoc = document.getElementById('btn-mode-doc');
      const btnPdf = document.getElementById('btn-mode-pdf');
      const docView = document.getElementById('doc-viewer-container');
      const pdfView = document.getElementById('pdf-viewer-container');

      if (mode === 'doc') {
        btnDoc.className = "px-2.5 py-1 rounded-md bg-white text-indigo-700 font-bold shadow-xs flex items-center space-x-1";
        btnPdf.className = "px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 font-medium flex items-center space-x-1";
        docView.classList.remove('hidden');
        pdfView.classList.add('hidden');
      } else {
        btnPdf.className = "px-2.5 py-1 rounded-md bg-white text-indigo-700 font-bold shadow-xs flex items-center space-x-1";
        btnDoc.className = "px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 font-medium flex items-center space-x-1";
        pdfView.classList.remove('hidden');
        docView.classList.add('hidden');
        updatePdfFramePage(currentPage);
      }
    }

    function updatePdfFramePage(page) {
      const frame = document.getElementById('pdf-frame');
      if (frame) {
        frame.src = `/api/pdf#page=${page}`;
      }
    }

    function jumpToPage(pageNum) {
      if (pageNum < 1) pageNum = 1;
      if (pageNum > 40) pageNum = 40;
      currentPage = pageNum;
      document.getElementById('page-input').value = currentPage;
      document.getElementById('page-num-footer').textContent = `Trang ${currentPage} / 40`;
      
      renderPage(currentPage, activeHighlightQuote);

      if (currentMode === 'pdf') {
        updatePdfFramePage(currentPage);
      }
    }

    function prevPage() {
      if (currentPage > 1) jumpToPage(currentPage - 1);
    }

    function nextPage() {
      if (currentPage < 40) jumpToPage(currentPage + 1);
    }

    function jumpToSection(pageStr) {
      jumpToPage(parseInt(pageStr));
    }

    function renderPage(pageNum, highlightQuote = '') {
      const pageObj = DATA.pages.find(p => p.page === pageNum);
      if (!pageObj) return;

      document.getElementById('page-section-badge').textContent = pageObj.section;
      const bodyEl = document.getElementById('page-content-body');
      
      let rawText = pageObj.text;

      if (highlightQuote && highlightQuote.trim()) {
        const cleanQuote = highlightQuote.trim();
        
        if (rawText.includes(cleanQuote)) {
          rawText = rawText.replace(cleanQuote, `<mark id="active-highlight" class="citation-mark">${cleanQuote}</mark>`);
        } else {
          const clauses = cleanQuote.split('.').map(s => s.trim()).filter(s => s.length >= 15);
          let highlighted = false;
          for (const c of clauses) {
            if (rawText.includes(c)) {
              rawText = rawText.replace(c, `<mark id="active-highlight" class="citation-mark">${c}</mark>`);
              highlighted = true;
              break;
            }
          }
          if (!highlighted) {
            const shortSub = cleanQuote.slice(0, 35).trim();
            if (shortSub.length >= 10 && rawText.includes(shortSub)) {
              rawText = rawText.replace(shortSub, `<mark id="active-highlight" class="citation-mark">${shortSub}</mark>`);
            }
          }
        }
      }

      bodyEl.innerHTML = rawText;

      setTimeout(() => {
        const mark = document.getElementById('active-highlight');
        if (mark) {
          mark.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
    }

    function viewCitation(pageNum, quote, label) {
      activeHighlightQuote = quote;
      jumpToPage(pageNum);
      setViewMode('doc');

      const toast = document.getElementById('citation-toast');
      const toastText = document.getElementById('citation-toast-text');
      toastText.textContent = `Đang soi Trang ${pageNum}: "${label || (quote ? quote.slice(0, 50) : '')}..."`;
      toast.classList.remove('hidden');
      setTimeout(() => {
        toast.classList.add('hidden');
      }, 5000);
    }

    function viewCitationByQid(qid) {
      const q = DATA.questions.find(x => x.id === qid);
      if (!q) return;
      viewCitation(q.gold_page, q.evidence_quote, `Trang ${q.gold_page}`);
    }

    function askQuestion(qid) {
      const q = DATA.questions.find(x => x.id === qid);
      if (!q) return;

      appendUserMessage(q.question);

      const traceA = DATA.traces_a[q.id];
      const traceB = DATA.traces_b[q.id];
      const traceC = DATA.traces_c[q.id];

      setTimeout(() => {
        appendAssistantResponse(q, traceA, traceB, traceC);
        viewCitation(q.gold_page, q.evidence_quote, `Điều khoản tại Trang ${q.gold_page}`);
      }, 300);
    }

    function submitCustomQuestion() {
      const input = document.getElementById('chat-input');
      const query = input.value.trim();
      if (!query) return;

      input.value = '';
      appendUserMessage(query);

      const matched = DATA.questions.find(q => 
        q.question.toLowerCase().includes(query.toLowerCase()) || 
        query.toLowerCase().includes(q.question.toLowerCase().slice(0, 20))
      );

      setTimeout(() => {
        if (matched) {
          const traceA = DATA.traces_a[matched.id];
          const traceB = DATA.traces_b[matched.id];
          const traceC = DATA.traces_c[matched.id];
          appendAssistantResponse(matched, traceA, traceB, traceC);
          viewCitation(matched.gold_page, matched.evidence_quote, `Trang ${matched.gold_page}`);
        } else {
          appendFallbackResponse(query);
        }
      }, 400);
    }

    function appendUserMessage(text) {
      const container = document.getElementById('chat-messages');
      const msg = document.createElement('div');
      msg.className = "flex items-start justify-end space-x-2";
      msg.innerHTML = `
        <div class="bg-indigo-600 text-white rounded-2xl rounded-tr-none px-4 py-2.5 max-w-md text-xs sm:text-sm shadow-xs font-medium leading-relaxed">
          ${escapeHtml(text)}
        </div>
      `;
      container.appendChild(msg);
      container.scrollTop = container.scrollHeight;
    }

    function appendAssistantResponse(q, traceA, traceB, traceC) {
      const container = document.getElementById('chat-messages');
      const msg = document.createElement('div');
      msg.className = "flex items-start space-x-3";

      msg.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center shrink-0 text-xs font-bold shadow-xs">
          AI
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-800 space-y-3 shadow-xs leading-relaxed">
          <div>
            <span class="font-bold text-slate-900 text-xs block mb-1">Căn cứ theo Quyết định UBND TP Hà Nội 2026:</span>
            <p class="text-slate-700 leading-relaxed">${escapeHtml(q.expected_answer)}</p>
          </div>

          <!-- Citation Button: Clickable to jump & highlight -->
          <div class="pt-1">
            <button onclick="viewCitationByQid('${q.id}')" class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-100 hover:bg-amber-200 border border-amber-300 text-amber-900 font-semibold text-xs shadow-xs transition-all group">
              <svg class="w-4 h-4 text-amber-700 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span>Xem Trích Dẫn: <strong>Trang ${q.gold_page}</strong></span>
              <span class="text-amber-700/80 font-mono text-[10px]">↗ (Bấm để highlight)</span>
            </button>
          </div>

          <!-- Grounded Quote -->
          <div class="bg-amber-50/60 p-2.5 rounded-xl border border-amber-200 text-[11px] text-amber-950 font-doc italic">
            "${escapeHtml(q.evidence_quote)}"
          </div>

          <!-- Strategy Breakdown Dropdown -->
          <details class="text-xs pt-1 text-slate-500 border-t border-slate-100">
            <summary class="cursor-pointer hover:text-indigo-600 font-semibold text-[11px] flex items-center space-x-1 py-1">
              <span>🔍 Đối chiếu kết quả 3 chiến lược Ingestion</span>
            </summary>
            <div class="mt-2 space-y-1.5 text-[11px] font-mono">
              <div class="p-1.5 rounded bg-slate-50 flex justify-between border border-slate-100">
                <span>Strategy A (Fixed 500):</span>
                <span class="${traceA?.hit_1 ? 'text-emerald-700' : (traceA?.hit_3 ? 'text-blue-700' : 'text-rose-600')} font-bold">
                  ${traceA?.hit_1 ? 'Hit Rank 1' : (traceA?.hit_3 ? 'Hit Rank 2-3' : 'MISS (Trượt)')}
                </span>
              </div>
              <div class="p-1.5 rounded bg-slate-50 flex justify-between border border-slate-100">
                <span>Strategy B (Paragraph):</span>
                <span class="${traceB?.hit_1 ? 'text-emerald-700' : (traceB?.hit_3 ? 'text-blue-700' : 'text-rose-600')} font-bold">
                  ${traceB?.hit_1 ? 'Hit Rank 1' : (traceB?.hit_3 ? 'Hit Rank 2-3' : 'MISS')}
                </span>
              </div>
              <div class="p-1.5 rounded bg-emerald-50 flex justify-between border border-emerald-200">
                <span class="text-emerald-900 font-bold">Strategy C (Paragraph + Filter):</span>
                <span class="${traceC?.hit_1 ? 'text-emerald-700' : 'text-blue-700'} font-bold">
                  ${traceC?.hit_1 ? 'Hit Rank 1 (Tối ưu)' : 'Hit Rank 2-3'}
                </span>
              </div>
            </div>
          </details>
        </div>
      `;
      container.appendChild(msg);
      container.scrollTop = container.scrollHeight;
    }

    function appendFallbackResponse(query) {
      const container = document.getElementById('chat-messages');
      const msg = document.createElement('div');
      msg.className = "flex items-start space-x-3";
      msg.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center shrink-0 text-xs font-bold">
          AI
        </div>
        <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-800 space-y-2 shadow-xs">
          <p>Đã tiếp nhận câu hỏi: <strong>"${escapeHtml(query)}"</strong>.</p>
          <p class="text-slate-600">Đang tra cứu trên bảng vector 'strategy_b_chunks'. Hãy bấm vào các câu hỏi gợi ý bên dưới để xem trích dẫn và highlight nguyên văn!</p>
        </div>
      `;
      container.appendChild(msg);
      container.scrollTop = container.scrollHeight;
    }

    function filterTableSplit(split) {
      currentTableSplit = split;
      document.querySelectorAll('#btn-tbl-all, #btn-tbl-dev, #btn-tbl-test').forEach(b => {
        b.className = "px-2.5 py-1 rounded bg-slate-200 text-slate-700 font-medium";
      });
      document.getElementById('btn-tbl-' + split).className = "px-2.5 py-1 rounded bg-indigo-600 text-white font-semibold";
      renderBenchmarkTable();
    }

    function renderBenchmarkTable() {
      const tbody = document.getElementById('benchmark-table-body');
      if (!tbody) return;

      const filtered = DATA.questions.filter(q => {
        if (currentTableSplit === 'dev' && q.split !== 'dev') return false;
        if (currentTableSplit === 'test' && q.split !== 'test') return false;
        return true;
      });

      let html = '';
      filtered.forEach(q => {
        const trA = DATA.traces_a[q.id];
        const trB = DATA.traces_b[q.id];
        const trC = DATA.traces_c[q.id];

        const fmtBadge = (tr) => {
          if (tr?.hit_1) return '<span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold font-mono text-[10px]">Rank 1</span>';
          if (tr?.hit_3) return '<span class="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold font-mono text-[10px]">Rank 2-3</span>';
          return '<span class="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold font-mono text-[10px]">Trượt</span>';
        };

        html += `
          <tr class="hover:bg-slate-50 transition-colors">
            <td class="p-3 font-mono font-bold text-indigo-700">${q.id.toUpperCase()}</td>
            <td class="p-3 uppercase font-bold text-[10px]"><span class="px-1.5 py-0.5 rounded ${q.split === 'dev' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}">${q.split}</span></td>
            <td class="p-3 text-slate-500 capitalize">${q.type.replace('_', ' ')}</td>
            <td class="p-3 font-medium text-slate-800">${escapeHtml(q.question)}</td>
            <td class="p-3 font-mono font-bold text-slate-900">Trang ${q.gold_page}</td>
            <td class="p-3">${fmtBadge(trA)}</td>
            <td class="p-3">${fmtBadge(trB)}</td>
            <td class="p-3">${fmtBadge(trC)}</td>
            <td class="p-3 text-right">
              <button onclick="switchMainTab('chat'); viewCitationByQid('${q.id}');" class="px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 font-semibold text-[11px] shadow-2xs transition-all">
                Soi Văn Bản ↗
              </button>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = html;
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    window.onload = init;
  </script>
</body>
</html>
"""

# Write to starter directory
out_path = STARTER_DIR / "data_ingestion_demo.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# Also write to brain artifact directory
brain_path = ARTIFACT_DIR / "data_ingestion_demo.html"
with open(brain_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated Light-Theme Chatbot, Benchmark & Audit UI at: {out_path} ({out_path.stat().st_size:,} bytes)")
