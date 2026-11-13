import json
from pathlib import Path

results_dir = Path("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/starter/results")

with open(results_dir / "traces_strategy_a.json", encoding="utf-8") as f:
    traces_a = {t["question_id"]: t for t in json.load(f)}

with open(results_dir / "traces_strategy_b.json", encoding="utf-8") as f:
    traces_b = {t["question_id"]: t for t in json.load(f)}

with open(results_dir / "traces_strategy_c.json", encoding="utf-8") as f:
    traces_c = {t["question_id"]: t for t in json.load(f)}

test_ids = ["q16", "q17", "q18", "q19", "q20"]

print("=== GROUNDING CHECK ON TEST SET (q16-q20) ===")
for qid in test_ids:
    print(f"\n--- {qid} ---")
    print("Question:", traces_b[qid]["question"])
    print("Gold Page:", traces_b[qid]["gold_page"])
    for s_name, t_dict in [("A", traces_a), ("B", traces_b), ("C", traces_c)]:
        t = t_dict[qid]
        hit3 = t["hit_3"]
        top_pages = [c["page"] for c in t["top_chunks"]]
        top_scores = [c["score"] for c in t["top_chunks"]]
        print(f"  Strategy {s_name}: Hit3={hit3} | Pages={top_pages} | Scores={top_scores}")
