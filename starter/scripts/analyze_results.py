import json
from pathlib import Path

results_dir = Path("H:/VinAI/K5-L3A-DAY06-NguyenTrongHuong-2A202603607-DataIngestion/starter/results")

with open(results_dir / "benchmark_summary.json", encoding="utf-8") as f:
    summary = json.load(f)
print("=== Benchmark Summary ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))

with open(results_dir / "traces_strategy_a.json", encoding="utf-8") as f:
    traces_a = json.load(f)

with open(results_dir / "traces_strategy_b.json", encoding="utf-8") as f:
    traces_b = json.load(f)

with open(results_dir / "traces_strategy_c.json", encoding="utf-8") as f:
    traces_c = json.load(f)

print("\n=== Strategy Comparison on Specific Cases ===")
for ta, tb, tc in zip(traces_a, traces_b, traces_c):
    qid = ta["question_id"]
    split = ta["split"]
    qtype = ta["type"]
    filt = ta["filter_applied"]
    sa = f"Hit1={ta['hit_1']}, Hit3={ta['hit_3']}"
    sb = f"Hit1={tb['hit_1']}, Hit3={tb['hit_3']}"
    sc = f"Hit1={tc['hit_1']}, Hit3={tc['hit_3']}"
    print(f"[{qid} - {split} - {qtype}] Filter: {filt}")
    print(f"  A: {sa} | Pages: {[c['page'] for c in ta['top_chunks']]}")
    print(f"  B: {sb} | Pages: {[c['page'] for c in tb['top_chunks']]}")
    print(f"  C: {sc} | Pages: {[c['page'] for c in tc['top_chunks']]}")
