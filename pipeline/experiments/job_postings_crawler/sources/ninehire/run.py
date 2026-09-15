"""STEP 3 실행: 나인하이어 계열 4곳 수집 + 결과 리포트."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.paths import LOG_DIR, PROCESSED_DIR  # noqa: E402
from sources.ninehire.crawler import crawl_all  # noqa: E402

results = crawl_all()

print()
print("=" * 96)
print("[STEP 3 수집 결과 — 나인하이어]")
print("=" * 96)
print(f"{'company_id':<14}{'회사명':<10}{'sitemap':>9}{'raw':>6}{'deploy=T':>10}{'deploy=F':>10}{'분류됨':>8}{'실패':>6}")
print("-" * 96)
for r in results:
    if "error" in r:
        print(f"{r['company_id']:<14}{r['company_name']:<10}  ❌ {r['error'][:60]}")
        continue
    print(
        f"{r['company_id']:<14}{r['company_name']:<10}{r['sitemap_urls']:>9}{r['raw_count']:>6}"
        f"{r['deploy_true']:>10}{r['deploy_false']:>10}{r['classified_active']:>8}{len(r['failures']):>6}"
    )

print()
for r in results:
    if "error" in r:
        continue
    print(f"  [{r['company_id']}] status 값: {r['statuses']}")
    if r["failures"]:
        print(f"      실패 {len(r['failures'])}건: {r['failures'][:3]}")

print()
print("=" * 96)
print("[분류 결과 상세]")
print("=" * 96)
for r in results:
    if "error" in r:
        continue
    doc = json.loads((PROCESSED_DIR / f"{r['company_id']}.json").read_text(encoding="utf-8"))
    print(f"\n--- {r['company_name']} ({r['company_id']})")
    for p in doc["postings"]:
        occ = p["occupations"][0] if p["occupations"] else "-"
        job = p["jobs"][0] if p["jobs"] else "-"
        flag = "" if p["deploy"] else "  [마감]"
        print(f"   {occ:<14} {job:<24} | {(p['title'] or '')[:48]:<50} → {p['category']}{flag}")

conflicts = [c for r in results if "error" not in r for c in r["disagreements"]]
print()
print(f"[구조화 vs 제목 불일치: {len(conflicts)}건]")
for c in conflicts:
    print(f"  [{c['company_id']}] {c['title']}")
    print(f"      구조화={c['structured']} (occ={c['occupations']}, job={c['jobs']}) | 제목={c['title_based']} → 채택={c['category']}")

if conflicts:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / "classification_conflicts.json"
    existing = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    ids = {(c["company_id"], c.get("opening_id")) for c in existing}
    existing += [c for c in conflicts if (c["company_id"], c.get("opening_id")) not in ids]
    log.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  불일치 로그 갱신: data/work/job_postings/logs/classification_conflicts.json ({len(existing)}건)")
