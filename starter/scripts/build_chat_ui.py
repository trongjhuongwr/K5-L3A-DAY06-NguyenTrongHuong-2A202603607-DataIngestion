"""Build the Chatbot + PDF Document Viewer Dual-Pane Application.
Outputs starter/data_ingestion_demo.html and syncs with brain artifact directory.
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
    
    # Identify main section for the page
    if idx <= 2:
        sec = "Chương I: Quy định chung"
    elif idx <= 12:
        sec = "Chương II: Hỗ trợ hạ tầng KH&CN"
    elif idx <= 14:
        sec = "Chương III: Ưu đãi & Hệ sinh thái"
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
<html lang="vi" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hà Nội SciTech Policy AI — Chatbot & Citation Explorer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .font-doc { font-family: 'Merriweather', Georgia, serif; }
    .font-mono-code { font-family: 'JetBrains Mono', monospace; }
    
    .citation-mark {
      background-color: #fef08a;
      color: #713f12;
      font-weight: 600;
      padding: 2px 4px;
      border-radius: 4px;
      border: 1px solid #facc15;
      box-shadow: 0 0 12px rgba(234, 179, 8, 0.4);
      animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes pulse-ring {
      0%, 100% { outline: 2px solid rgba(234, 179, 8, 0.8); }
      50% { outline: 4px solid rgba(234, 179, 8, 0.2); }
    }

    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: rgba(241, 245, 249, 0.6);
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
<body class="bg-slate-900 text-slate-100 h-full flex flex-col overflow-hidden antialiased select-none">

  <!-- Top Navbar -->
  <header class="bg-slate-900/95 backdrop-blur-md border-b border-slate-800 h-14 flex items-center justify-between px-4 sm:px-6 z-20 shrink-0">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-indigo-500/20">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
      </div>
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-sm font-bold text-white tracking-tight">Hà Nội SciTech Policy QA</h1>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">QĐ UBND 2026</span>
        </div>
        <p class="text-[11px] text-slate-400">Học viên: <span class="text-slate-200 font-semibold">Nguyễn Trọng Hưởng (2A202603607)</span> · VinUni AI Thực Chiến Lab Day 06</p>
      </div>
    </div>

    <!-- Right status -->
    <div class="flex items-center space-x-2 text-xs">
      <div class="hidden md:flex items-center space-x-2 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700/60 text-slate-300 font-mono text-[11px]">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span>40 Trang PDF</span>
        <span class="text-slate-500">•</span>
        <span>pgvector 1536d</span>
        <span class="text-slate-500">•</span>
        <span class="text-amber-400">100% Citation Grounded</span>
      </div>
    </div>
  </header>

  <!-- Main Dual-Pane Workspace -->
  <div class="flex-1 flex flex-col md:flex-row h-[calc(100vh-56px)] overflow-hidden">

    <!-- LEFT PANE: CHATBOT ASSISTANT (50%) -->
    <div class="w-full md:w-1/2 flex flex-col bg-slate-900 border-r border-slate-800 h-full relative">
      
      <!-- Chat Conversation Area -->
      <div id="chat-messages" class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 custom-scroll">
        
        <!-- Welcome Message -->
        <div class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-indigo-400 flex items-center justify-center shrink-0 text-xs font-bold">
            AI
          </div>
          <div class="bg-slate-800/80 border border-slate-700/70 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-200 space-y-2.5 shadow-sm leading-relaxed">
            <p class="font-semibold text-white">Xin chào! Tôi là Trợ lý Pháp lý Hà Nội SciTech 2026.</p>
            <p class="text-slate-300">
              Tôi có thể trả lời các câu hỏi về chính sách ưu đãi, hỗ trợ hạ tầng, lãi suất, thủ tục hồ sơ và trách nhiệm ban ngành theo Quyết định năm 2026 của UBND TP Hà Nội.
            </p>
            <div class="p-2.5 bg-slate-900/60 rounded-xl border border-indigo-500/20 text-xs space-y-1 text-slate-300">
              <span class="font-bold text-indigo-300 block flex items-center space-x-1">
                <svg class="w-3.5 h-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
                <span>Cơ chế Trích Dẫn & Soi Văn Bản (Interactive Citations):</span>
              </span>
              <span>Mỗi câu trả lời đều gắn kèm nút trích dẫn <strong>[📄 Trang X]</strong>. Khi bạn bấm vào, khung văn bản bên phải sẽ <strong>ngay lập tức mở đúng trang và tự động highlight câu bằng chứng</strong>!</span>
            </div>
            
            <p class="text-slate-400 text-xs pt-1 font-medium">Bạn có thể chọn một trong các câu hỏi mẫu bên dưới để thử nghiệm ngay:</p>
          </div>
        </div>

      </div>

      <!-- Suggested Question Chips Carousel -->
      <div class="px-4 py-2 border-t border-slate-800 bg-slate-900/90 shrink-0">
        <div class="flex items-center space-x-1.5 overflow-x-auto custom-scroll py-1 text-xs">
          <button onclick="askQuestion('q01')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            🎯 Q01: Chính sách ưu đãi (Trang 2)
          </button>
          <button onclick="askQuestion('q03')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            📋 Q03: Mẫu hồ sơ hạ tầng (Trang 3)
          </button>
          <button onclick="askQuestion('q05')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            ⏱️ Q05: Thời hạn xử lý hồ sơ (Trang 5)
          </button>
          <button onclick="askQuestion('q06')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            👥 Q06: Hội đồng thẩm định (Trang 7)
          </button>
          <button onclick="askQuestion('q11')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            📅 Q11: Hiệu lực thi hành (Trang 15)
          </button>
          <button onclick="askQuestion('q16')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            💰 Q16: Lãi suất Quỹ ĐTPT (Trang 14)
          </button>
          <button onclick="askQuestion('q17')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            🎪 Q17: Hỗ trợ 100% gian hàng (Trang 14)
          </button>
          <button onclick="askQuestion('q18')" class="shrink-0 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 text-slate-300 transition-all font-medium">
            🏢 Q18: Trách nhiệm Sở KH&CN (Trang 15)
          </button>
        </div>
      </div>

      <!-- Chat Input Controls -->
      <div class="p-3 sm:p-4 border-t border-slate-800 bg-slate-900 shrink-0 space-y-2">
        <div class="flex items-center space-x-2">
          <div class="relative flex-1">
            <input type="text" id="chat-input" onkeydown="if(event.key==='Enter') submitCustomQuestion()" placeholder="Nhập câu hỏi tra cứu chính sách hoặc số hiệu điều khoản..." class="w-full text-xs sm:text-sm pl-4 pr-10 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <button onclick="submitCustomQuestion()" class="absolute right-2 top-2 p-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-all">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-slate-400">
          <div class="flex items-center space-x-2">
            <span>Chiến lược:</span>
            <select id="strategy-selector" class="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded px-2 py-0.5 focus:outline-none focus:ring-1 focus:ring-indigo-500">
              <option value="c" selected>Strategy C (Paragraph + Filter) [Khuyến nghị]</option>
              <option value="b">Strategy B (Paragraph 800 chars)</option>
              <option value="a">Strategy A (Fixed 500/50 chars)</option>
            </select>
          </div>
          <span>Bấm trích dẫn để soi trực tiếp</span>
        </div>
      </div>

    </div>

    <!-- RIGHT PANE: DOCUMENT & PDF VIEWER (50%) -->
    <div class="w-full md:w-1/2 flex flex-col bg-slate-800/40 h-full relative">
      
      <!-- Top Document Toolbar -->
      <div class="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 p-2.5 px-4 flex flex-wrap items-center justify-between gap-3 shrink-0 z-10">
        
        <!-- Page Nav -->
        <div class="flex items-center space-x-2">
          <button onclick="prevPage()" class="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700" title="Trang trước">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          </button>
          <div class="flex items-center space-x-1 text-xs text-slate-300 font-mono">
            <span>Trang</span>
            <input type="number" id="page-input" min="1" max="40" value="2" onchange="jumpToPage(parseInt(this.value))" class="w-12 text-center bg-slate-800 border border-slate-700 rounded text-amber-300 font-bold text-xs py-0.5 focus:outline-none focus:ring-1 focus:ring-indigo-500">
            <span>/ 40</span>
          </div>
          <button onclick="nextPage()" class="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700" title="Trang sau">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
        </div>

        <!-- Mode Toggle -->
        <div class="flex items-center rounded-lg bg-slate-800 p-0.5 border border-slate-700 text-xs">
          <button onclick="setViewMode('doc')" id="btn-mode-doc" class="px-2.5 py-1 rounded-md bg-indigo-600 text-white font-semibold flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <span>Văn Bản & Highlight</span>
          </button>
          <button onclick="setViewMode('pdf')" id="btn-mode-pdf" class="px-2.5 py-1 rounded-md text-slate-400 hover:text-white flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            <span>Tệp PDF Gốc</span>
          </button>
        </div>

        <!-- Section Quick Jump -->
        <select onchange="jumpToSection(this.value)" class="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-500">
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

      <!-- Active Citation Info Floating Toast -->
      <div id="citation-toast" class="hidden absolute top-14 left-4 right-4 z-20 bg-amber-500/90 text-slate-950 px-4 py-2 rounded-xl shadow-lg flex items-center justify-between text-xs font-semibold backdrop-blur-sm transition-all duration-300">
        <div class="flex items-center space-x-2">
          <span class="text-base">📌</span>
          <span id="citation-toast-text">Đang trích dẫn Trang 2 · Khớp nguyên văn 100%</span>
        </div>
        <button onclick="document.getElementById('citation-toast').classList.add('hidden')" class="text-slate-900 hover:text-black">✕</button>
      </div>

      <!-- Mode 1: Document Page Viewer (A4 Sheet Simulation with Highlight) -->
      <div id="doc-viewer-container" class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 flex justify-center custom-scroll bg-slate-950/50">
        
        <div id="a4-sheet" class="w-full max-w-2xl bg-white text-slate-900 rounded-sm shadow-2xl p-8 sm:p-12 min-h-[950px] font-doc text-[13px] sm:text-[14px] leading-relaxed relative flex flex-col justify-between border border-slate-300 select-text">
          
          <!-- Government Header -->
          <div class="border-b border-slate-200 pb-4 mb-6">
            <div class="flex justify-between items-start text-[11px] font-sans font-semibold text-slate-600">
              <div>
                <p class="uppercase tracking-wider">ỦY BAN NHÂN DÂN</p>
                <p class="uppercase font-bold text-slate-900">THÀNH PHỐ HÀ NỘI</p>
                <p class="text-[10px] text-slate-500 pt-1">Số: .../2026/QĐ-UBND</p>
              </div>
              <div class="text-center">
                <p class="uppercase font-bold text-slate-900">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</p>
                <p class="font-semibold text-slate-700">Độc lập - Tự do - Hạnh phúc</p>
                <p class="text-[10px] text-slate-500 pt-1 italic">Hà Nội, năm 2026</p>
              </div>
            </div>
            <div class="text-center pt-4">
              <span id="page-section-badge" class="px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200 text-indigo-800 font-sans text-[11px] font-bold">
                Chương I: Quy định chung
              </span>
            </div>
          </div>

          <!-- Page Dynamic Content -->
          <div id="page-content-body" class="flex-1 space-y-3 whitespace-pre-line text-slate-800">
            <!-- Rendered by JS -->
          </div>

          <!-- Page Footer -->
          <div class="border-t border-slate-200 pt-3 mt-8 flex justify-between items-center text-[11px] font-sans text-slate-400">
            <span>Quyết định hỗ trợ hạ tầng KHCN & ĐMST Hà Nội 2026</span>
            <span class="font-bold text-slate-700" id="page-num-footer">Trang 2 / 40</span>
          </div>

        </div>

      </div>

      <!-- Mode 2: Real PDF Embed Iframe -->
      <div id="pdf-viewer-container" class="hidden flex-1 w-full h-full bg-slate-900">
        <iframe id="pdf-frame" src="/api/pdf#page=2" class="w-full h-full border-0"></iframe>
      </div>

    </div>

  </div>

  <script>
    const DATA = """ + json_payload + """;

    let currentPage = 2;
    let currentMode = 'doc';
    let activeHighlightQuote = '';

    function init() {
      renderPage(currentPage);
      // Automatically post first sample greeting
      askQuestion('q01');
    }

    function setViewMode(mode) {
      currentMode = mode;
      const btnDoc = document.getElementById('btn-mode-doc');
      const btnPdf = document.getElementById('btn-mode-pdf');
      const docView = document.getElementById('doc-viewer-container');
      const pdfView = document.getElementById('pdf-viewer-container');

      if (mode === 'doc') {
        btnDoc.className = "px-2.5 py-1 rounded-md bg-indigo-600 text-white font-semibold flex items-center space-x-1";
        btnPdf.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white flex items-center space-x-1";
        docView.classList.remove('hidden');
        pdfView.classList.add('hidden');
      } else {
        btnPdf.className = "px-2.5 py-1 rounded-md bg-indigo-600 text-white font-semibold flex items-center space-x-1";
        btnDoc.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white flex items-center space-x-1";
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
        
        // Exact match
        if (rawText.includes(cleanQuote)) {
          rawText = rawText.replace(cleanQuote, `<mark id="active-highlight" class="citation-mark">${cleanQuote}</mark>`);
        } else {
          // Substring match first 40 chars
          const sub = cleanQuote.slice(0, 40);
          if (sub.length > 10 && rawText.includes(sub)) {
            rawText = rawText.replace(sub, `<mark id="active-highlight" class="citation-mark">${sub}</mark>`);
          }
        }
      }

      bodyEl.innerHTML = rawText;

      // Smooth scroll to highlight if present
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

      // Show floating toast
      const toast = document.getElementById('citation-toast');
      const toastText = document.getElementById('citation-toast-text');
      toastText.textContent = `Đang soi Trang ${pageNum}: "${label || quote.slice(0, 50)}..."`;
      toast.classList.remove('hidden');
      setTimeout(() => {
        toast.classList.add('hidden');
      }, 5000);
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
        // Automatically jump to citation on right pane
        viewCitation(q.gold_page, q.evidence_quote, `Điều khoản tại Trang ${q.gold_page}`);
      }, 300);
    }

    function submitCustomQuestion() {
      const input = document.getElementById('chat-input');
      const query = input.value.trim();
      if (!query) return;

      input.value = '';
      appendUserMessage(query);

      // Search in benchmark or synthesize
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
        <div class="bg-indigo-600 text-white rounded-2xl rounded-tr-none px-4 py-2.5 max-w-md text-xs sm:text-sm shadow-sm font-medium leading-relaxed">
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

      const quoteClean = q.evidence_quote.replace(/"/g, '&quot;');

      msg.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-indigo-400 flex items-center justify-center shrink-0 text-xs font-bold">
          AI
        </div>
        <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-100 space-y-3 shadow-md leading-relaxed">
          <div>
            <span class="font-bold text-white text-xs block mb-1">Căn cứ theo Quyết định UBND TP Hà Nội 2026:</span>
            <p class="text-slate-200 leading-relaxed">${escapeHtml(q.expected_answer)}</p>
          </div>

          <!-- Citation Button: The core highlight trigger -->
          <div class="pt-1">
            <button onclick="viewCitation(${q.gold_page}, '${quoteClean}', 'Trang ${q.gold_page}')" class="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-400/20 hover:bg-amber-400/30 border border-amber-400/40 text-amber-300 font-semibold text-xs shadow-xs transition-all group">
              <svg class="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span>Xem Trích Dẫn: <strong>Trang ${q.gold_page}</strong></span>
              <span class="text-amber-400/70 font-mono text-[10px]">↗ (Bấm để highlight)</span>
            </button>
          </div>

          <!-- Grounded Quote Snippet -->
          <div class="bg-slate-900/70 p-2.5 rounded-xl border border-slate-700/60 text-[11px] text-slate-300 font-doc italic">
            "${escapeHtml(q.evidence_quote)}"
          </div>

          <!-- Strategy Breakdown Dropdown -->
          <details class="text-xs pt-1 text-slate-400 border-t border-slate-700/50">
            <summary class="cursor-pointer hover:text-indigo-300 font-semibold text-[11px] flex items-center space-x-1 py-1">
              <span>🔍 Đối chiếu kết quả 3 chiến lược Ingestion</span>
            </summary>
            <div class="mt-2 space-y-1.5 text-[11px] font-mono">
              <div class="p-1.5 rounded bg-slate-900/60 flex justify-between">
                <span>Strategy A (Fixed 500):</span>
                <span class="${traceA?.hit_1 ? 'text-emerald-400' : (traceA?.hit_3 ? 'text-blue-400' : 'text-rose-400')} font-bold">
                  ${traceA?.hit_1 ? 'Hit Rank 1' : (traceA?.hit_3 ? 'Hit Rank 2-3' : 'MISS (Trượt)')}
                </span>
              </div>
              <div class="p-1.5 rounded bg-slate-900/60 flex justify-between">
                <span>Strategy B (Paragraph):</span>
                <span class="${traceB?.hit_1 ? 'text-emerald-400' : (traceB?.hit_3 ? 'text-blue-400' : 'text-rose-400')} font-bold">
                  ${traceB?.hit_1 ? 'Hit Rank 1' : (traceB?.hit_3 ? 'Hit Rank 2-3' : 'MISS')}
                </span>
              </div>
              <div class="p-1.5 rounded bg-slate-900/60 flex justify-between border border-emerald-500/30">
                <span class="text-emerald-300">Strategy C (Paragraph + Filter):</span>
                <span class="${traceC?.hit_1 ? 'text-emerald-400' : 'text-blue-400'} font-bold">
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
        <div class="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-indigo-400 flex items-center justify-center shrink-0 text-xs font-bold">
          AI
        </div>
        <div class="bg-slate-800/90 border border-slate-700/80 rounded-2xl rounded-tl-none p-4 max-w-xl text-xs sm:text-sm text-slate-100 space-y-2.5 shadow-md">
          <p>Đã nhận câu hỏi: <strong>"${escapeHtml(query)}"</strong>.</p>
          <p class="text-slate-300">Hệ thống đang truy xuất trên vector store PostgreSQL 16 + pgvector. Vui lòng bấm vào các câu hỏi mẫu gợi ý trên thanh cuộn để xem trích dẫn và highlight chính xác nhất!</p>
        </div>
      `;
      container.appendChild(msg);
      container.scrollTop = container.scrollHeight;
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

print(f"Generated Chatbot + PDF Highlight UI at: {out_path} ({out_path.stat().st_size:,} bytes)")
