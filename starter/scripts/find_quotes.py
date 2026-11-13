import pypdf
import unicodedata
import re

path = "H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/starter/data/quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
reader = pypdf.PdfReader(path)

def get_page_text(p_num):
    raw = reader.pages[p_num - 1].extract_text() or ""
    return unicodedata.normalize("NFC", raw)

def show_snippet(p, kw):
    txt = get_page_text(p)
    idx = txt.find(kw)
    if idx != -1:
        print(f"P{p} FOUND '{kw}':")
        snippet = txt[idx:idx+250].replace("\n", " ")
        print(f"  Snippet: {repr(snippet)}")
    else:
        print(f"P{p} NOT FOUND '{kw}'")

show_snippet(2, "Điều 1. Phạm vi điều chỉnh")
show_snippet(2, "Điều 2. Đối tượng áp dụng")
show_snippet(3, "Mẫu số 01")
show_snippet(4, "Mẫu số 03")
show_snippet(5, "05 ngày làm việc")
show_snippet(7, "từ 07 đến 11 thành viên")
show_snippet(8, "tối thiểu 5 năm")
show_snippet(8, "tối thiểu 01 lần/năm")
show_snippet(9, "tổng mức kinh phí")
show_snippet(10, "kết quả nghiệm thu được xếp loại")
show_snippet(10, "sai mục đích")
show_snippet(11, "áp dụng cơ chế chấp nhận rủi ro")
show_snippet(13, "Nội dung hỗ trợ bao gồm")
show_snippet(14, "miễn phí gian hàng")
show_snippet(14, "lãi suất cho vay tối thiểu")
show_snippet(14, "Mẫu số 07")
show_snippet(15, "cơ quan đầu mối")
show_snippet(16, "quy định chuyển tiếp")
show_snippet(19, "Cam kết")
show_snippet(23, "Giải pháp kỹ thuật")
