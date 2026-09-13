"""리크루터(Jobflex) 계열 수집 + 결과 리포트."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.paths import PROCESSED_DIR  # noqa: E402
from sources.recruiter.crawler import crawl_all  # noqa: E402

results = crawl_all()

print()
print("=" * 96)
print("[수집 결과 — 리크루터]")
print("=" * 96)
print(f"{'company_id':<14}{'회사명':<12}{'raw':>6}{'deploy=T':>10}{'deploy=F':>10}{'분류됨':>8}{'구조화없음':>10}")
print("-" * 96)
for r in results:
    if "error" in r:
        print(f"{r['company_id']:<14}{r.get('company_name', ''):<12}  ❌ {r['error'][:60]}")
        continue
    print(
        f"{r['company_id']:<14}{r['company_name']:<12}{r['raw_count']:>6}{r['deploy_true']:>10}"
        f"{r['deploy_false']:>10}{r['classified_active']:>8}{r['no_structured']:>10}"
    )

for r in results:
    if "error" in r:
        continue
    doc = json.loads((PROCESSED_DIR / f"{r['company_id']}.json").read_text(encoding="utf-8"))
    print(f"\n--- {r['company_name']} ({r['company_id']})")
    for p in doc["postings"]:
        occ = p["occupations"][0] if p["occupations"] else "-"
        flag = "" if p["deploy"] else "  [마감]"
        print(f"   {occ:<20} | {(p['title'] or '')[:48]:<50} → {p['category']}{flag}")
