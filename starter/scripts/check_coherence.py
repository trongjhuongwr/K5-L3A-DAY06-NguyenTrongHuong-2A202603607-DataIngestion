import psycopg
from dotenv import load_dotenv
import os

load_dotenv("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/starter/.env")
db_url = os.getenv("DATABASE_URL")

positions = [
    ("Dieu 1 (p2)", 2, "Điều 1. Phạm vi điều chỉnh"),
    ("Dieu 6 (p3)", 3, "Điều 6. Điều kiện, tiêu chí hỗ trợ"),
    ("Dieu 7 (p5)", 5, "Điều 7. Trình tự xét duyệt hỗ trợ"),
    ("Dieu 8 (p7)", 7, "Điều 8. Hội đồng tư vấn"),
    ("Dieu 10 (p8)", 8, "Điều 10. Kiểm tra, giám sát việc thực hiện hỗ trợ"),
    ("Dieu 11 (p9)", 9, "Điều 11. Điều chỉnh hợp đồng hỗ trợ"),
    ("Dieu 13 (p10)", 10, "Điều 13. Thu hồi, hoàn trả kinh phí hỗ trợ"),
    ("Dieu 14 (p11)", 11, "Điều 14. Xem xét áp dụng Cơ chế chấp nhận rủi ro"),
    ("Dieu 19 (p13)", 13, "Điều 19. Hỗ trợ kết nối hệ sinh thái"),
    ("Dieu 20 (p14)", 14, "Điều 20. Thực hiện hỗ trợ miễn phí gian hàng")
]

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for label, page, kw in positions:
            print(f"\n==================== {label} ====================")
            # Find chunk in strategy_a
            cur.execute("SELECT chunk_id, content FROM strategy_a_chunks WHERE page = %s AND content LIKE %s LIMIT 1;", (page, f"%{kw}%"))
            row_a = cur.fetchone()
            if row_a:
                print(f"[Strategy A - {row_a[0]}] length={len(row_a[1])}:")
                print("  Start:", repr(row_a[1][:100]))
                print("  End:  ", repr(row_a[1][-100:]))
            
            # Find chunk in strategy_b
            cur.execute("SELECT chunk_id, content FROM strategy_b_chunks WHERE page = %s AND content LIKE %s LIMIT 1;", (page, f"%{kw}%"))
            row_b = cur.fetchone()
            if row_b:
                print(f"[Strategy B - {row_b[0]}] length={len(row_b[1])}:")
                print("  Start:", repr(row_b[1][:100]))
                print("  End:  ", repr(row_b[1][-100:]))
