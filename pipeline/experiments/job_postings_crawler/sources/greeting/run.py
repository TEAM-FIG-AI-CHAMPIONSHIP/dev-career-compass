"""STEP 2 실행: 그리팅 계열 11곳 수집 + 결과 리포트."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.paths import LOG_DIR  # noqa: E402
from sources.greeting.crawler import GREETING_COMPANIES, crawl_all  # noqa: E402

results = crawl_all()

print()
print("=" * 96)
print("[수집 결과]")
print("=" * 96)
header = f"{'company_id':<16}{'회사명':<16}{'raw':>6}{'deploy=T':>10}{'deploy=F':>10}{'분류됨':>8}{'구조화없음':>10}  추출경로"
print(header)
print("-" * 96)

total_raw = total_active = 0
conflicts = []
errors = []
paths = {}

for r in results:
    if "error" in r:
        errors.append(r)
        print(f"{r['company_id']:<16}{r.get('company_name', ''):<16}  ❌ {r['error'][:60]}")
        continue
    total_raw += r["raw_count"]
    total_active += r["deploy_true"]
    conflicts.extend(r["disagreements"])
    paths[r["company_id"]] = r["extracted_from"]
    print(
        f"{r['company_id']:<16}{r['company_name']:<16}{r['raw_count']:>6}{r['deploy_true']:>10}"
        f"{r['deploy_false']:>10}{r['classified_active']:>8}{r['no_structured']:>10}  {r['extracted_from']}"
    )

print("-" * 96)
print(f"{'합계':<32}{total_raw:>6}{total_active:>10}")

print()
print("=" * 96)
print("[__NEXT_DATA__ 추출 경로 — 회사별 차이 확인]")
print("=" * 96)
by_path = {}
for cid, p in paths.items():
    by_path.setdefault(p, []).append(cid)
for p, cids in by_path.items():
    print(f"  {p}")
    print(f"    → {', '.join(cids)} ({len(cids)}곳)")

print()
print("=" * 96)
print(f"[구조화 필드 vs 제목 키워드 불일치: {len(conflicts)}건 (deploy=true 기준)]")
print("=" * 96)
for c in conflicts[:40]:
    print(f"  [{c['company_id']}] {c['title'][:52]}")
    print(f"      구조화={c['structured']} (occ={c['occupations'][:2]}, job={c['jobs'][:2]}) | 제목={c['title_based']} → 채택={c['category']}")
if len(conflicts) > 40:
    print(f"  ... 외 {len(conflicts) - 40}건")

LOG_DIR.mkdir(parents=True, exist_ok=True)
(LOG_DIR / "classification_conflicts.json").write_text(
    json.dumps(conflicts, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("\n  불일치 로그 저장: data/work/job_postings/logs/classification_conflicts.json")

if errors:
    print()
    print("=" * 96)
    print("[실패]")
    print("=" * 96)
    for e in errors:
        print(f"  {e['company_id']}: {e['error']}  ({e['url']})")
