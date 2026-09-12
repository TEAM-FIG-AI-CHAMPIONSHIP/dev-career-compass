"""STEP 6 1차 집계.

잠정 규칙 (raw는 그대로 둔다. 집계에서만 적용):
  1. 카카오: company_id == kakao 이면서 group == "카카오"(본사)만 카카오 몫.
     SUBSIDIARY(페이·모빌리티·손보·게임즈·헬스케어)는 집계에서 제외.
     카카오페이·카카오모빌리티는 그리팅 수집분이 대표.
  2. occupation 오염: OCCUPATION_BLEED_VERDICT == "무관" 인 건은
     "오염 제외" 버전에서 미분류로 본다. "관련"·"판정 보류"는 그대로 둔다.

사용: python3 scripts/step6_aggregate.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_keyword_audit import (  # noqa: E402
    OCCUPATION_BLEED_VERDICT,
    occupation_bleed_rows,
)
from common.job_classifier import CATEGORIES  # noqa: E402
from common.paths import PROCESSED_DIR, RESEARCH_DIR  # noqa: E402

PROCESSED = PROCESSED_DIR
OUT_MD = RESEARCH_DIR / "step6_summary.md"
OUT_JSON = RESEARCH_DIR / "step6_summary.json"

LOW_VOLUME = 10
LOW_CLASSIFIED = 2
GATE = 3

# processed.group == API companyName. 본사 필터 코드 KAKAO ↔ "카카오"
KAKAO_HQ_GROUP = "카카오"


def load_docs():
    docs = {}
    for path in PROCESSED.glob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        docs[doc["company_id"]] = doc
    return docs


def kakao_hq_only(postings, company_id):
    if company_id != "kakao":
        return postings
    return [p for p in postings if p.get("group") == KAKAO_HQ_GROUP]


def unrelated_bleed_ids(postings):
    """무관 occupation 오염으로 집계에서 뺄 opening_id 집합."""
    drop = set()
    for posting, occupation, _kws, _job, verdict in occupation_bleed_rows(postings):
        if verdict == "무관":
            drop.add(posting["opening_id"])
    return drop


def company_row(doc):
    cid = doc["company_id"]
    all_active = [p for p in doc["postings"] if p["deploy"]]
    active = kakao_hq_only(all_active, cid)
    drop = unrelated_bleed_ids(active)
    classified_with = [p for p in active if p["category"]]
    classified_without = [p for p in classified_with if p["opening_id"] not in drop]

    def cats(postings):
        found = {p["category"] for p in postings if p["category"]}
        return {c: sum(1 for p in postings if p["category"] == c) for c in CATEGORIES if c in found}

    return {
        "company_id": cid,
        "company_name": doc["company_name"],
        "source": doc["source"],
        "raw_active": len(all_active),
        "active": len(active),
        "kakao_excluded": len(all_active) - len(active) if cid == "kakao" else 0,
        "classified_with": len(classified_with),
        "classified_without": len(classified_without),
        "cats_with": cats(classified_with),
        "cats_without": cats(classified_without),
        "bleed_dropped": [
            {
                "opening_id": p["opening_id"],
                "title": p["title"],
                "occupation": (p["occupations"] or [None])[0],
                "category": p["category"],
            }
            for p in classified_with
            if p["opening_id"] in drop
        ],
    }


def is_low_volume(row, classified_key):
    return row["active"] < LOW_VOLUME or row[classified_key] <= LOW_CLASSIFIED


def companies_for(rows, classified_key, cats_key, category):
    return [
        r for r in rows
        if category in r[cats_key]
    ]


def render_md(rows, totals):
    lines = []
    add = lines.append

    add("# STEP 6 1차 집계")
    add("")
    add("스펙 키워드(`JOB_KEYWORDS`)는 바꾸지 않았다. 아래 숫자는 잠정 규칙이다.")
    add("팀이 규칙을 바꾸면 `data/work/job_postings/raw/`에서 다시 돌리면 된다.")
    add("")
    add("## 잠정 규칙")
    add("")
    add("1. **카카오 중복 방지** — `company_id == kakao` 공고 중 `group == 카카오`(본사,")
    add("   API 필터 `KAKAO`)만 카카오 몫으로 센다. `SUBSIDIARY`는 집계에서 제외한다.")
    add("   카카오페이·카카오모빌리티는 그리팅 수집분을 대표로 쓴다.")
    add("   careers.kakao.com에만 있는 `공간정보 기획자` 등은 이 규칙에서 **어디에도 안 들어간다**")
    add("   (항목 9 옵션 3으로 바꾸면 합칠 수 있다). raw는 지우거나 합치지 않았다.")
    add("2. **occupation 오염** — `OCCUPATION_BLEED_VERDICT == 무관` 인 건만")
    add("   「오염 제외」 버전에서 미분류로 본다. 해당: 쏘카 `개발/데이터`, 컬리 `인프라`.")
    add("   「관련」·「판정 보류」는 그대로 둔다.")
    add("3. **저물량** — `deploy=true < 10` 또는 분류 ≤ 2. 아래 표의 분류 칸은")
    add("   오염 제외 후 숫자다.")
    add("4. **S5 게이트** — 직무별로 분류된 회사가 3곳 이상이면 통과.")
    add("   본문 숫자는 **오염 제외 후**. 괄호는 오염 포함 시.")
    add("")
    add("## 직무별 회사 수")
    add("")
    add("| 직무 | 오염 제외 | 오염 포함 | 게이트(3곳) |")
    add("|---|---:|---:|---|")
    for cat in CATEGORIES:
        without_n = totals["without"][cat]["n"]
        with_n = totals["with"][cat]["n"]
        extra = f" (오염 포함 시 {with_n}곳)"
        gate = "통과" if without_n >= GATE else "탈락"
        add(f"| {cat} | **{without_n}곳**{extra} | {with_n}곳 | {gate} |")
    add("")
    add("```")
    for cat in CATEGORIES:
        without_n = totals["without"][cat]["n"]
        with_n = totals["with"][cat]["n"]
        add(f"{cat:<12} {without_n}곳 (오염 포함 시 {with_n}곳)  게이트 {'통과' if without_n >= GATE else '탈락'}")
    add("```")
    add("")

    passing = sum(1 for cat in CATEGORIES if totals["without"][cat]["n"] >= GATE)
    add(f"게이트 통과 직무 **{passing} / {len(CATEGORIES)}** (오염 제외 기준).")
    add("")
    same_n = all(
        totals["without"][cat]["n"] == totals["with"][cat]["n"] for cat in CATEGORIES
    )
    if same_n:
        add("회사 수(N곳)는 오염 전후가 같다. 무관 건을 빼도 해당 회사가")
        add("그 직무에 남는 분류가 있으면 회사 수에서 빠지지 않는다.")
        add("바뀌는 것은 분류 건수와 저물량 여부다.")
    add("")

    add("## 직무별 회사 목록 (오염 제외)")
    add("")
    for cat in CATEGORIES:
        names = totals["without"][cat]["names"]
        dropped = [
            n for n in totals["with"][cat]["names"]
            if n not in names
        ]
        add(f"### {cat} — {len(names)}곳")
        add("")
        add(", ".join(names) if names else "(없음)")
        add("")
        if dropped:
            add(f"오염 포함 시에만 있던 회사: {', '.join(dropped)}")
            add("")

    add("## 저물량 회사")
    add("")
    add(f"기준: 진행 중 < {LOW_VOLUME}건 **또는** 분류 ≤ {LOW_CLASSIFIED}건.")
    add("분류는 오염 제외 후. 카카오 본사 필터 적용 후 진행 중 건수.")
    add("")
    add("| 회사 | 진행 중 | 분류(제외 후) | 분류(포함) | 조건 |")
    add("|---|---:|---:|---:|---|")
    low = [r for r in rows if is_low_volume(r, "classified_without")]
    for r in sorted(low, key=lambda x: (x["active"], x["classified_without"], x["company_name"])):
        why = []
        if r["active"] < LOW_VOLUME:
            why.append("물량")
        if r["classified_without"] <= LOW_CLASSIFIED:
            why.append("분류")
        add(
            f"| {r['company_name']} | {r['active']} | {r['classified_without']} "
            f"| {r['classified_with']} | {'+'.join(why)} |"
        )
    add("")
    add(f"저물량 **{len(low)}곳** / 전체 {len(rows)}곳. 코어 후보에서 빼 두고 보면 된다.")
    add("")

    add("## 각주")
    add("")
    add("### 저물량 (오염과 무관하게 원래 기준을 충족)")
    add("")
    original_low = [r for r in rows if is_low_volume(r, "classified_with")]
    for r in sorted(original_low, key=lambda x: (x["active"], x["classified_with"])):
        add(f"- **{r['company_name']}** — 진행 {r['active']} / 분류 {r['classified_with']}")
    add("")
    bleed_to_low = [
        r for r in rows
        if r["bleed_dropped"]
        and not is_low_volume(r, "classified_with")
        and is_low_volume(r, "classified_without")
    ]
    add(f"### 오염 때문에 저물량으로 내려가는 {len(bleed_to_low)}곳")
    add("")
    if not bleed_to_low:
        add("해당 없음.")
        add("")
    else:
        add("오염을 포함하면 분류가 3건 이상이지만,")
        add("`무관` occupation 오염을 빼면 분류 ≤ 2가 되어 저물량 기준을 충족한다.")
        add("")
        for r in bleed_to_low:
            occs = sorted({b["occupation"] for b in r["bleed_dropped"] if b["occupation"]})
            add(
                f"- **{r['company_name']}** — 분류 {r['classified_with']} → {r['classified_without']} "
                f"(occupation `{', '.join(occs)}` 무관 {len(r['bleed_dropped'])}건 제외). "
                f"남은 분류 직무: {', '.join(r['cats_without']) or '없음'}"
            )
        add("")
    kurly = next((x for x in rows if x["company_id"] == "kurly"), None)
    if kurly and kurly["bleed_dropped"] and kurly not in bleed_to_low:
        add(
            f"컬리 `인프라` 무관 {len(kurly['bleed_dropped'])}건도 같은 규칙으로 뺐다. "
            f"분류 {kurly['classified_with']} → {kurly['classified_without']} "
            f"(저물량 기준은 충족하지 않음)."
        )
        add("")

    add("## 카카오 잠정 규칙이 바꾼 것")
    add("")
    kakao = next(x for x in rows if x["company_id"] == "kakao")
    add(
        f"카카오 processed는 진행 {kakao['raw_active']}건 그대로다. "
        f"집계에서는 본사 {kakao['active']}건만 썼고 관계사 {kakao['kakao_excluded']}건은 제외했다."
    )
    add("")
    add("| 직무 | 본사만(잠정) | 관계사 포함 시 카카오가 추가로 세어질 직무 |")
    add("|---|---|---|")
    # We don't have the all-kakao cats in row; recompute note from known facts
    add("| 서버·백엔드 | 본사 있음 | 페이·모빌리티와 이중 집계 |")
    add("| 웹 프론트엔드 | 본사 없음 → 카카오 카운트 안 함 | 페이 1건으로 카카오가 웹에 올라감 |")
    add("| 데이터·AI | 본사 있음 | 페이·모빌리티·헬스케어와 이중 집계 |")
    add("| 모바일 | 없음 | 없음 |")
    add("")
    add("## 회사별 원표 (참고)")
    add("")
    add("| 회사 | 진행 중 | 분류 제외 | 분류 포함 | 직무(제외) |")
    add("|---|---:|---:|---:|---|")
    for r in sorted(rows, key=lambda x: (-x["classified_without"], -x["active"], x["company_name"])):
        jobs = ", ".join(r["cats_without"]) or "—"
        flag = ""
        if r["company_id"] == "kakao":
            flag = f" (본사 {r['active']}/{r['raw_active']})"
        add(
            f"| {r['company_name']}{flag} | {r['active']} | {r['classified_without']} "
            f"| {r['classified_with']} | {jobs} |"
        )
    add("")
    return "\n".join(lines) + "\n"


def main():
    docs = load_docs()
    rows = [company_row(docs[cid]) for cid in sorted(docs)]

    totals = {"with": {}, "without": {}}
    for label, cats_key in (("with", "cats_with"), ("without", "cats_without")):
        for cat in CATEGORIES:
            names = sorted(r["company_name"] for r in rows if cat in r[cats_key])
            totals[label][cat] = {"n": len(names), "names": names}

    md = render_md(rows, totals)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(
            {
                "rules": {
                    "kakao": "group == 카카오 (KAKAO HQ) only; SUBSIDIARY excluded from kakao count",
                    "bleed": "drop OCCUPATION_BLEED_VERDICT == 무관 in without-bleed version",
                    "gate": GATE,
                    "low_volume": {"active_lt": LOW_VOLUME, "classified_lte": LOW_CLASSIFIED},
                },
                "totals": totals,
                "companies": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(md)
    print(f"저장: {OUT_MD}")
    print(f"저장: {OUT_JSON}")


if __name__ == "__main__":
    main()
