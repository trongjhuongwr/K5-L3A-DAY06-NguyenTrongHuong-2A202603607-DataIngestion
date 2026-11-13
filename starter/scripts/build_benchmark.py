import pypdf
import unicodedata
import json
import os

pdf_path = "H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/starter/data/quy_dinh_ha_tang_khcn_hanoi_2026.pdf"
reader = pypdf.PdfReader(pdf_path)

def get_page_text(p_num):
    raw = reader.pages[p_num - 1].extract_text() or ""
    return unicodedata.normalize("NFC", raw)

pages = {i: get_page_text(i) for i in range(1, 41)}
doc_id = "quy-dinh-ha-tang-khcn-hanoi-2026"

questions = [
    {
        "id": "q01",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Quyết định quy định trình tự, thủ tục thực hiện các chính sách gì trên địa bàn thành phố Hà Nội?",
        "expected_answer": "Trình tự, thủ tục thực hiện các chính sách ưu đãi, hỗ trợ phát triển hạ tầng và tổ chức có hoạt động trong lĩnh vực khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số.",
        "gold_source_id": doc_id,
        "gold_page": 2,
        "evidence_quote": "Quyết định này quy định trình tự, thủ tục thực hiện các chính sách ưu đãi, hỗ trợ phát triển hạ tầng và tổ chức có hoạt động trong lĩnh vực khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số trên địa bàn thành phố Hà Nội",
        "filter": None
    },
    {
        "id": "q02",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Đối tượng áp dụng tại Điều 2 của Quyết định bao gồm những tổ chức nào?",
        "expected_answer": "Quỹ Phát triển KHCN và ĐMST thành phố Hà Nội, các cơ quan nhà nước thực hiện chính sách và các tổ chức thụ hưởng theo Nghị quyết 25/2026/NQ-HĐND.",
        "gold_source_id": doc_id,
        "gold_page": 2,
        "evidence_quote": "1. Quỹ Phát triển khoa học, công nghệ và đổi mới sáng tạo của thành phố Hà Nội (sau đây gọi tắt là Quỹ), các cơ quan nhà nước có chức năng, nhiệm vụ tổ chức thực hiện các chính sách hỗ trợ theo Nghị quyết số 25/2026/NQ-HĐND.",
        "filter": None
    },
    {
        "id": "q03",
        "split": "dev",
        "type": "liet_ke",
        "question": "Hồ sơ đề nghị hỗ trợ phát triển hạ tầng quy định đơn đề nghị và thuyết minh dự án theo những mẫu nào?",
        "expected_answer": "Đơn đề nghị hỗ trợ theo Mẫu số 01 và Thuyết minh dự án theo Mẫu số 02.",
        "gold_source_id": doc_id,
        "gold_page": 3,
        "evidence_quote": "Mẫu số 01 tại Phụ lục ban hành kèm theo Quyết định này); b) Thuyết minh dự án, trong đó bao gồm phương án vận hành và dự toán kinh phí vận hành (nếu đề nghị hỗ trợ chi phí vận hành) (theo Mẫu số 02",
        "filter": None
    },
    {
        "id": "q04",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Hồ sơ đề nghị hỗ trợ chi phí kiểm định, hiệu chuẩn trang thiết bị phải sử dụng các biểu mẫu nào?",
        "expected_answer": "Đơn đề nghị theo Mẫu số 03 và Thuyết minh nội dung theo Mẫu số 04.",
        "gold_source_id": doc_id,
        "gold_page": 4,
        "evidence_quote": "Mẫu số 03 tại Phụ lục ban hành kèm theo Quyết định này); b) Thuyết minh nội dung đề nghị hỗ trợ (theo Mẫu số 04 tại Phụ lục ban hành kèm theo Quyết định này);",
        "filter": None
    },
    {
        "id": "q05",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Sở Khoa học và Công nghệ có thời hạn bao nhiêu ngày làm việc để kiểm tra tính đầy đủ, hợp lệ của hồ sơ hỗ trợ phát triển hạ tầng?",
        "expected_answer": "Trong thời hạn không quá 05 ngày làm việc kể từ ngày tiếp nhận hồ sơ.",
        "gold_source_id": doc_id,
        "gold_page": 5,
        "evidence_quote": "Trong thời hạn không quá 05 ngày làm việc kể từ ngày tiếp nhận hồ sơ, Sở Khoa học và Công nghệ kiểm tra tính đầy đủ, hợp lệ của hồ sơ. Sở Khoa học và Công nghệ thông báo cho tổ chức có nhu cầu nhận hỗ trợ về tính hợp lệ của hồ sơ; hoặc yêu cầu bổ sung, hoàn thiện hồ sơ",
        "filter": {"section": "ha_tang_khcn"}
    },
    {
        "id": "q06",
        "split": "dev",
        "type": "truc_tiep",
        "question": "Hội đồng tư vấn xét duyệt hồ sơ có số lượng thành viên là bao nhiêu và gồm những ai?",
        "expected_answer": "Từ 07 đến 11 thành viên, gồm Chủ tịch, Phó Chủ tịch, các Ủy viên, Thư ký hành chính và các thành viên khác.",
        "gold_source_id": doc_id,
        "gold_page": 7,
        "evidence_quote": "từ 07 đến 11 thành viên, bao gồm Chủ tịch Hội đồng, Phó Chủ tịch Hội đồng, các Ủy viên, Thư ký hành chính và các thành viên khác do người có thẩm quyền quyết định trên cơ sở tính chất, nội dung xem xét.",
        "filter": None
    },
    {
        "id": "q07",
        "split": "dev",
        "type": "so_lieu",
        "question": "Trách nhiệm duy trì vận hành hạ tầng sau hỗ trợ được quy định tối thiểu trong bao lâu?",
        "expected_answer": "Tối thiểu 5 năm.",
        "gold_source_id": doc_id,
        "gold_page": 8,
        "evidence_quote": "trách nhiệm duy trì vận hành hạ tầng sau hỗ trợ tối thiểu 5 năm; đ) Chế độ báo cáo, kiểm tra, giám sát, nghiệm thu;",
        "filter": None
    },
    {
        "id": "q08",
        "split": "dev",
        "type": "dinh_ky",
        "question": "Việc kiểm tra, giám sát định kỳ hợp đồng hỗ trợ được thực hiện với tần suất như thế nào?",
        "expected_answer": "Tối thiểu 01 lần/năm hoặc theo các mốc tiến độ trong hợp đồng.",
        "gold_source_id": doc_id,
        "gold_page": 8,
        "evidence_quote": "Việc kiểm tra, giám sát được thực hiện theo định kỳ tối thiểu 01 lần/năm hoặc theo các mốc tiến độ, kết quả đầu ra quy định trong hợp đồng hỗ trợ.",
        "filter": None
    },
    {
        "id": "q09",
        "split": "dev",
        "type": "dieu_kien",
        "question": "Việc điều chỉnh hợp đồng hỗ trợ có được làm tăng tổng mức kinh phí hỗ trợ từ ngân sách Thành phố không?",
        "expected_answer": "Việc điều chỉnh không được làm tăng tổng mức kinh phí hỗ trợ từ ngân sách Thành phố.",
        "gold_source_id": doc_id,
        "gold_page": 9,
        "evidence_quote": "tổng mức kinh phí hỗ trợ từ ngân sách Thành phố.",
        "filter": None
    },
    {
        "id": "q10",
        "split": "dev",
        "type": "nghiem_thu",
        "question": "Kết quả đánh giá, nghiệm thu thực hiện hợp đồng hỗ trợ được xếp loại theo các mức nào?",
        "expected_answer": "Xếp loại theo 2 mức: Đạt hoặc Không đạt.",
        "gold_source_id": doc_id,
        "gold_page": 10,
        "evidence_quote": "Kết quả nghiệm thu được xếp loại theo một trong các mức sau: a) Đạt; b) Không đạt.",
        "filter": None
    },
    {
        "id": "q11",
        "split": "dev",
        "type": "che_tai",
        "question": "Hậu quả pháp lý khi tổ chức sử dụng kinh phí hỗ trợ sai mục đích là gì?",
        "expected_answer": "Xem xét dừng hỗ trợ, thu hồi toàn bộ hoặc một phần kinh phí hỗ trợ.",
        "gold_source_id": doc_id,
        "gold_page": 10,
        "evidence_quote": "dừng hỗ trợ, thu hồi toàn bộ hoặc một phần kinh phí hỗ trợ theo quy định tại Điều 13 Quyết định này;",
        "filter": None
    },
    {
        "id": "q12",
        "split": "dev",
        "type": "ngoai_le",
        "question": "Khi dự án gặp rủi ro khách quan dẫn đến không đạt kết quả, tổ chức cần gửi hồ sơ đề nghị áp dụng cơ chế chấp nhận rủi ro đến cơ quan nào?",
        "expected_answer": "Quỹ Phát triển khoa học, công nghệ và đổi mới sáng tạo Thành phố.",
        "gold_source_id": doc_id,
        "gold_page": 11,
        "evidence_quote": "áp dụng cơ chế chấp nhận rủi ro, kèm theo tài liệu chứng minh gửi Quỹ Phát triển khoa học, công nghệ và đổi mới sáng tạo Thành phố.",
        "filter": None
    },
    {
        "id": "q13",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Nội dung hỗ trợ kết nối hệ sinh thái ĐMST với chuyên gia, nhà khoa học bao gồm hoạt động gì?",
        "expected_answer": "Tư vấn hoàn thiện hồ sơ, chuẩn bị tài liệu minh chứng quyền sở hữu công nghệ.",
        "gold_source_id": doc_id,
        "gold_page": 13,
        "evidence_quote": "2. Nội dung hỗ trợ bao gồm:\na) Tư vấn, hướng dẫn doanh nghiệp và các tổ chức có hoạt động trong lĩnh vực khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số hoàn thiện hồ sơ theo quy định của pháp luật; hỗ trợ chuẩn bị tài liệu, minh chứng về quyền sở hữu hoặc quyền sử dụng hợp pháp đối với kết quả khoa học và công nghệ, công nghệ hoặc tài sản trí tuệ;",
        "filter": {"section": "doanh_nghiep_he_sinh_thai"}
    },
    {
        "id": "q14",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Tổ chức được hưởng chính sách gì về gian hàng tại các sự kiện xúc tiến của Thành phố?",
        "expected_answer": "Được miễn phí gian hàng trưng bày sản phẩm khoa học và công nghệ.",
        "gold_source_id": doc_id,
        "gold_page": 14,
        "evidence_quote": "Được miễn phí gian hàng trưng bày sản phẩm khoa học và công nghệ tại các sự kiện",
        "filter": {"section": "doanh_nghiep_he_sinh_thai"}
    },
    {
        "id": "q15",
        "split": "dev",
        "type": "metadata_filter",
        "question": "Trong Mẫu số 01, tổ chức đề nghị hỗ trợ phải cam kết thực hiện đúng những quy định nào?",
        "expected_answer": "Cam kết thực hiện đúng các quy định của Nghị quyết số 25/2026/NQ-HĐND và Quyết định của UBND Thành phố.",
        "gold_source_id": doc_id,
        "gold_page": 19,
        "evidence_quote": "Tổ chức đề nghị hỗ trợ cam kết: 1. Các thông tin trong hồ sơ là trung thực, chính xác và chịu trách nhiệm trước pháp luật về nội dung kê khai. 2. Thực hiện đúng các quy định của Nghị quyết số 25/2026/NQ-HĐND và Quyết định của Ủy ban nhân dân",
        "filter": {"section": "bieu_mau_ho_so"}
    },
    # Test set (5 questions)
    {
        "id": "q16",
        "split": "test",
        "type": "metadata_filter",
        "question": "Doanh nghiệp vay vốn tại Quỹ Đầu tư phát triển Thành phố được hưởng chính sách ưu đãi lãi suất như thế nào?",
        "expected_answer": "Được xem xét hưởng lãi suất cho vay tối thiểu khi vay vốn tại Quỹ Đầu tư phát triển Thành phố.",
        "gold_source_id": doc_id,
        "gold_page": 14,
        "evidence_quote": "lãi suất cho vay tối thiểu khi vay vốn tại Quỹ Đầu tư phát triển Thành phố để thực hiện các dự án đầu tư mới hạ tầng khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số.",
        "filter": {"section": "doanh_nghiep_he_sinh_thai"}
    },
    {
        "id": "q17",
        "split": "test",
        "type": "ngoai_le",
        "question": "Hồ sơ đề nghị hỗ trợ 100% chi phí gian hàng khi tham gia hội chợ, sự kiện công nghệ quốc tế gồm những tài liệu gì?",
        "expected_answer": "Đơn đề nghị theo Mẫu số 07, tài liệu chứng minh được chấp thuận tham gia và báo giá chi phí gian hàng.",
        "gold_source_id": doc_id,
        "gold_page": 14,
        "evidence_quote": "a) Đơn đề nghị hỗ trợ (theo Mẫu số 07 tại Phụ lục ban hành kèm theo Quyết định này); b) Tài liệu chứng minh việc đăng ký và được chấp thuận tham gia triển lãm, hội chợ, sự kiện công nghệ quốc tế theo chương trình xúc tiến của Thành phố; c) Báo giá chi phí gian hàng của Ban tổ chức",
        "filter": None
    },
    {
        "id": "q18",
        "split": "test",
        "type": "tham_quyen",
        "question": "Sở Khoa học và Công nghệ có trách nhiệm và vai trò gì trong việc triển khai Quyết định này?",
        "expected_answer": "Là cơ quan đầu mối tham mưu Ủy ban nhân dân Thành phố tổ chức triển khai thực hiện.",
        "gold_source_id": doc_id,
        "gold_page": 15,
        "evidence_quote": "1. Là cơ quan đầu mối tham mưu Ủy ban nhân dân Thành phố tổ chức triển khai thực hiện Nghị quyết số 25/2026/NQ-HĐND và Quyết định này; chủ trì hướng dẫn, tuyên truyền, phổ biến, theo dõi, đôn đốc và phối hợp với các cơ quan, đơn vị liên quan tổ chức thực hiện các chính sách hỗ trợ theo quy định.",
        "filter": None
    },
    {
        "id": "q19",
        "split": "test",
        "type": "chuyen_tiep",
        "question": "Trách nhiệm của các sở, ban, ngành, cơ quan liên quan được quy định tại Điều nào trong Quyết định?",
        "expected_answer": "Được quy định tại Điều 26: Trách nhiệm của các cơ quan liên quan.",
        "gold_source_id": doc_id,
        "gold_page": 16,
        "evidence_quote": "Điều 26. Trách nhiệm của các cơ quan liên quan Các sở, ban, ngành, đơn vị thuộc Thành phố và các cơ quan, tổ chức có liên quan có trách nhiệm phối hợp với Sở Khoa học và Công nghệ",
        "filter": None
    },
    {
        "id": "q20",
        "split": "test",
        "type": "bieu_mau",
        "question": "Trong Mẫu số 02 (Thuyết minh đề xuất hỗ trợ), mục Giải pháp kỹ thuật, công nghệ bao gồm những nội dung gì?",
        "expected_answer": "Công nghệ thiết bị dự kiến áp dụng, mức độ tiên tiến, khả năng kết nối mở rộng và yêu cầu an toàn an ninh bảo mật.",
        "gold_source_id": doc_id,
        "gold_page": 23,
        "evidence_quote": "Giải pháp kỹ thuật, công nghệ - Công nghệ, thiết bị, giải pháp kỹ thuật dự kiến áp dụng; - Mức độ tiên tiến, đồng bộ; - Khả năng kết nối, tích hợp và mở rộng; - Yêu cầu về an toàn, an ninh, bảo mật dữ liệu (nếu có);",
        "filter": None
    }
]

def clean_str(s):
    return " ".join(s.strip().replace("\n", " ").split()).lower()

all_valid = True
for q in questions:
    p_num = q["gold_page"]
    page_txt = pages[p_num]
    norm_eq = clean_str(q["evidence_quote"])
    norm_pt = clean_str(page_txt)
    if norm_eq not in norm_pt:
        print(f"MISMATCH in {q['id']} (Page {p_num})!")
        print("  Quote:", norm_eq[:80])
        print("  Page text around:", norm_pt[:200])
        all_valid = False

if all_valid:
    print("ALL 20 EVIDENCE QUOTES VERIFIED 100% IN ACTUAL PDF TEXT!")
    os.makedirs("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/benchmark", exist_ok=True)
    with open("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/benchmark/questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print("Saved to benchmark/questions.json successfully!")
else:
    print("Verification failed! Please fix quotes.")
