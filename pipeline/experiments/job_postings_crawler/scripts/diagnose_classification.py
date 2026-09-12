"""분류 누락 진단: 현재 스펙 키워드로 못 잡는 개발 직군 공고를 찾아낸다.

job_classifier.py는 건드리지 않는다. 확장 키워드는 "이렇게 넓히면 몇 건이
추가로 잡히는지"를 보여주기 위한 제안용이다.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.job_classifier import classify_job  # noqa: E402
from common.paths import PROCESSED_DIR  # noqa: E402

# 현재 스펙 키워드가 놓치는 표기들
PROPOSED_EXTRA = {
    "서버·백엔드": ["Back-end", "Back End", "백엔드", "서버", "DevOps", "SRE",
                 "Site Reliability", "인프라", "Infrastructure", "Cloud", "플랫폼 엔지니어"],
    "웹 프론트엔드": ["Front-end", "Front End", "프론트"],
    "모바일": ["Mobile", "앱 개발", "앱개발"],
    "데이터·AI": ["Machine Learning", "MLOps", "Analyst", "Analytics",
                "Scientist", "LLM", "추천 시스템", "빅데이터"],
}

DEV_HINT = re.compile(
    r"개발|엔지니어|Engineer|Developer|Tech|SW|소프트웨어|DevOps|SRE|Data|AI|QA",
    re.IGNORECASE,
)

_ASCII = re.compile(r"^[A-Za-z][A-Za-z\s\-]*$")


def extra_match(text):
    if not text:
        return None
    for cat, kws in PROPOSED_EXTRA.items():
        for kw in kws:
            if _ASCII.match(kw):
                if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
                    return cat
            elif kw in text:
                return cat
    return None


rows, unclassified = [], []
for f in sorted(PROCESSED_DIR.glob("*.json")):
    doc = json.loads(f.read_text(encoding="utf-8"))
    for p in doc["postings"]:
        if not p["deploy"]:
            continue
        rows.append(p)
        if not p["category"]:
            unclassified.append(p)

print("=" * 88)
print(f"전체 deploy=true {len(rows)}건 / 현재 분류됨 {len(rows) - len(unclassified)}건 / 미분류 {len(unclassified)}건")
print("=" * 88)

# 미분류 중 개발 직군으로 보이는 것
suspects = [
    p for p in unclassified
    if DEV_HINT.search(f"{p['title']} {' '.join(str(x) for x in p['occupations'])} {' '.join(str(x) for x in p['jobs'])}")
]
print(f"\n미분류 중 '개발 직군으로 보이는' 공고: {len(suspects)}건")
print("-" * 88)
recovered = {}
for p in suspects:
    hit = extra_match(p["title"]) or extra_match(" ".join(str(x) for x in p["jobs"] + p["occupations"]))
    mark = f"→ 확장시 {hit}" if hit else "→ 확장해도 미분류"
    if hit:
        recovered.setdefault(hit, []).append(p)
    print(f"  [{p['company_id']:<14}] {p['title'][:50]:<52} occ={str(p['occupations'])[:22]:<24} {mark}")

print()
print("=" * 88)
print("확장 키워드 적용 시 추가로 잡히는 건수")
print("=" * 88)
for cat, items in sorted(recovered.items(), key=lambda x: -len(x[1])):
    companies = sorted({p["company_id"] for p in items})
    print(f"  {cat}: +{len(items)}건 ({len(companies)}개사: {', '.join(companies)})")

print()
print("=" * 88)
print("현재 vs 확장: 직무별 '해당 직무가 1건 이상 있는 회사 수'")
print("=" * 88)
cur, ext = {}, {}
for p in rows:
    if p["category"]:
        cur.setdefault(p["category"], set()).add(p["company_id"])
        ext.setdefault(p["category"], set()).add(p["company_id"])
for cat, items in recovered.items():
    for p in items:
        ext.setdefault(cat, set()).add(p["company_id"])

print(f"  {'직무':<14}{'현재':>8}{'확장':>8}")
for cat in ["서버·백엔드", "웹 프론트엔드", "모바일", "데이터·AI"]:
    print(f"  {cat:<14}{len(cur.get(cat, set())):>8}{len(ext.get(cat, set())):>8}")
