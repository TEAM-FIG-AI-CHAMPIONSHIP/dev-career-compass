"""data/research/job_postings/keyword_audit.md 생성.

팀이 키워드 확장 여부를 직접 판단하기 위한 원자료 문서다.
판단·제안은 넣지 않고 수집된 원본 값만 정리한다.
job_classifier.py는 읽기만 하고 수정하지 않는다.
"""

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.job_classifier import (  # noqa: E402
    JOB_KEYWORDS,
    STRUCTURED_KEYWORDS,
    _ASCII_ONLY,
    _matches,
    classify_from_structured,
)
from common.paths import PROCESSED_DIR, RESEARCH_DIR  # noqa: E402

PROCESSED = PROCESSED_DIR
OUT = RESEARCH_DIR / "keyword_audit.md"

TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9\-]*|[가-힣]+")

SOURCES = ("greeting", "ninehire", "custom", "recruiter")

COMPANY_ORDER = [
    # 그리팅 계열
    "oliveyoung", "musinsa", "kurly", "catchtable", "kakaopay",
    "yeogieotdae", "kakaomobility", "watcha", "ssg", "devsisters",
    "myrealtrip", "ahnlabcloudmate", "upstage", "kakaoenterprise",
    "hancom", "buzzvil",
    # 나인하이어 계열
    "remember", "yogiyo", "megazone",
    # 리크루터
    "gsretail", "com2us",
    # 자체구축
    "naver", "kakaobank", "line", "daangn", "tving",
    "channeltalk", "banksalad", "hyperconnect", "socar", "kakao",
    "toss", "skplanet",
]

# ATS마다 구조화 필드 이름이 다르다. 문서에서는 occupation / job으로 통일해 표기한다.
FIELD_MAP = {
    "greeting": "occupation = `workspaceOccupation.occupation`, job = `workspaceJob.job`",
    "ninehire": "occupation = `recruitment.jobGroup.title`, job = `recruitment.jobTask.title`",
    "recruiter": "occupation = 직군 필터명 또는 `classificationCode`, job = 없음",
    "custom": (
        "회사마다 다름 — 네이버: occupation = `classCdNm`, job = `subJobCdNm` / "
        "카카오뱅크: occupation = `recruitClassName`, job = 없음 / "
        "라인: occupation = `job_unit[].name`, job = `job_fields[].name` / "
        "당근: occupation = `data-division`, job = `data-department-slugs` / "
        "티빙: occupation = Notion 컬렉션 이름, job = `기술스택`·`주요스킬` / "
        "채널톡: occupation = `categories.team`, job = 없음 / "
        "뱅크샐러드: occupation = 응답 그룹 키 `department`, job = `data[].job` / "
        "하이퍼커넥트: occupation = `categories.team`, job = 없음 / "
        "쏘카: occupation = `job_group_code` 라벨, job = 없음 / "
        "카카오: occupation = `jobTypeName`, job = `skillSetList[].skillSetName` / "
        "토스: occupation = metadata Job Category, job = metadata 세부 포지션 명 / "
        "SK그룹: occupation = `jobRole`, job = 없음"
    ),
}

# 키워드 문자 종류별 '단어' 구성 문자 집합.
# 부분일치 판정에 쓴다: 매칭 구간 좌우로 같은 종류 문자가 붙어 있으면 더 긴 단어의 일부다.
HANGUL = re.compile(r"[가-힣]")
ALNUM = re.compile(r"[A-Za-z0-9]")

# 섹션 5 판정용.
# occupation 경유로 분류된 건 중, 그 occupation 이름이 카테고리와 의미상 맞는지
# (company_id, occupation) 단위로 판정한 결과. 판정 근거를 팀이 다시 볼 수 있도록
# 명시적으로 관리하고, 목록에 없는 새 조합은 "판정 보류"로 노출한다.
OCCUPATION_BLEED_VERDICT = {
    # 여러 이질적 직무를 묶는 상위 직군이라 무관한 업무까지 끌려온 경우
    ("kurly", "인프라"): "무관",
    ("socar", "개발/데이터"): "무관",
    # 직군 이름 자체가 해당 카테고리 전용이고 실제 업무도 맞는 경우
    ("catchtable", "AI"): "관련",
    ("catchtable", "Data"): "관련",
    ("hyperconnect", "AI/ML"): "관련",
    ("remember", "Data"): "관련",
}

# 섹션 4 판정용.
# 스펙 키워드를 품은 더 긴 영단어 중, "그 복합어가 키워드가 가리키는 기술 개념의
# 하위 개념/합성어"인 것만 모은다. (Database ⊂ Data)
# Webtoon·Taiwan·Retail처럼 철자만 겹치는 것은 여기 넣지 않는다(섹션 3 성격).
# 판정 근거를 팀이 다시 볼 수 있도록 이 목록은 명시적으로 관리한다.
RELATED_COMPOUNDS = {
    "Data": {"database", "databases", "dataset", "datasets", "datastore",
             "datastores", "datamart", "dataops", "dataware", "datawarehouse"},
    "Web": {"webapp", "webapps", "webview", "webviews", "webrtc",
            "webgl", "webassembly", "website", "websites", "webpack"},
    "Server": {"serverless"},
    "Android": set(),
    "iOS": set(),
    "AI": {"aiops"},
    "ML": {"mlops"},
    "Backend": set(),
    "Frontend": set(),
}


def load():
    docs = {}
    for f in PROCESSED.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("source") in SOURCES:
            docs[d["company_id"]] = d
    return docs


def ordered(docs):
    ids = [c for c in COMPANY_ORDER if c in docs]
    ids += [c for c in sorted(docs) if c not in ids]
    return ids


def matched_keywords(title, category):
    """제목에서 실제로 걸린 스펙 키워드. 분류기와 동일한 매칭 규칙을 쓴다."""
    if not title or not category:
        return []
    return [kw for kw in JOB_KEYWORDS.get(category, []) if _matches(kw, title)]


def _keyword_spans(keyword, title):
    """제목에서 키워드가 매칭된 (시작, 끝) 구간 목록. 분류기 규칙과 동일."""
    if _ASCII_ONLY.match(keyword):
        return [(m.start(), m.end()) for m in
                re.finditer(rf"\b{re.escape(keyword)}\b", title, re.IGNORECASE)]
    return [(m.start(), m.end()) for m in re.finditer(re.escape(keyword), title)]


def _enclosing_word(title, start, end, char_class):
    """매칭 구간을 같은 문자 종류로 좌우 확장해 실제 단어를 얻는다."""
    i, j = start, end
    while i > 0 and char_class.match(title[i - 1]):
        i -= 1
    while j < len(title) and char_class.match(title[j]):
        j += 1
    return title[i:j]


def occupation_bleed_rows(postings):
    """occupation 이름에 스펙 키워드가 섞여 들어와 분류된 사례.

    조건: (1) 구조화 분류이고 job이 아니라 occupation에서 매칭됐다
          (2) 그 occupation 문자열에 스펙 키워드가 있다
          (3) job 값도 title도 같은 카테고리를 뒷받침하지 않는다
    """
    rows = []
    for posting in postings:
        if posting["category_source"] != "structured":
            continue
        category = posting["category"]
        jobs = [j for j in (posting["jobs"] or []) if j]
        if any(classify_from_structured(None, j) == category for j in jobs):
            continue
        occupation = next(
            (
                o
                for o in (posting["occupations"] or [])
                if o and any(_matches(k, o) for k in STRUCTURED_KEYWORDS[category])
            ),
            None,
        )
        if not occupation:
            continue
        supported = any(
            _matches(k, j) for j in jobs for k in STRUCTURED_KEYWORDS[category]
        ) or any(_matches(k, posting["title"] or "") for k in JOB_KEYWORDS[category])
        if supported:
            continue
        rows.append(
            (
                posting,
                occupation,
                [k for k in STRUCTURED_KEYWORDS[category] if _matches(k, occupation)],
                jobs[0] if jobs else None,
                OCCUPATION_BLEED_VERDICT.get(
                    (posting["company_id"], occupation), "판정 보류"
                ),
            )
        )
    return rows


def boundary_blocked_hits(text):
    """ASCII 키워드가 더 긴 영단어 안에 있어서 단어 경계(\\b) 규칙에 막힌 사례.

    반환: [(카테고리, 키워드, 그 키워드를 품은 단어, 의미상 관련 여부), ...]
    한글 키워드는 부분일치를 그대로 허용하므로 여기 해당되지 않는다.
    """
    if not text:
        return []
    hits = []
    for category, keywords in JOB_KEYWORDS.items():
        for keyword in keywords:
            if not _ASCII_ONLY.match(keyword):
                continue
            for match in re.finditer(re.escape(keyword), text, re.IGNORECASE):
                start, end = match.start(), match.end()
                before = start > 0 and ALNUM.match(text[start - 1])
                after = end < len(text) and ALNUM.match(text[end])
                if not before and not after:
                    continue  # 독립된 단어 → 정상 매칭됨
                word = _enclosing_word(text, start, end, ALNUM)
                if word.lower() == keyword.lower():
                    continue
                related = word.lower() in RELATED_COMPOUNDS.get(keyword, set())
                hits.append((category, keyword, word, related))
    return hits


def substring_hits(title):
    """키워드가 '더 긴 단어의 일부'로 걸린 사례를 찾는다.

    반환: [(카테고리, 키워드, 키워드를 포함한 실제 단어), ...]
    """
    if not title:
        return []
    hits = []
    for category, keywords in JOB_KEYWORDS.items():
        for keyword in keywords:
            char_class = ALNUM if _ASCII_ONLY.match(keyword) else HANGUL
            for start, end in _keyword_spans(keyword, title):
                word = _enclosing_word(title, start, end, char_class)
                if word.lower() != keyword.lower():
                    hits.append((category, keyword, word))
    return hits


def freq_table(counter, headers, limit=None):
    items = sorted(counter.items(), key=lambda x: (-x[1], str(x[0])))
    if limit:
        items = items[:limit]
    lines = [f"| {' | '.join(headers)} |", f"|{'---|' * len(headers)}"]
    for value, n in items:
        label = "(없음/None)" if value is None else str(value).replace("|", "\\|")
        lines.append(f"| {label} | {n} |")
    return "\n".join(lines)


def main():
    docs = load()
    company_ids = ordered(docs)
    names = {cid: docs[cid]["company_name"] for cid in company_ids}
    srcs = {cid: docs[cid]["source"] for cid in company_ids}

    # deploy=true 공고만 대상
    posts = {cid: [p for p in docs[cid]["postings"] if p["deploy"]] for cid in company_ids}
    allp = [p for cid in company_ids for p in posts[cid]]
    unclassified = [p for p in allp if not p["category"]]
    # 구조화 필드로는 분류 실패, 제목 키워드 fallback으로 카테고리가 붙은 건
    title_fallback = [p for p in allp if p["category_source"] == "title"]
    structured = [p for p in allp if p["category_source"] == "structured"]

    # 부분일치 오탐: (공고, 카테고리, 키워드, 걸린 단어, 이 매칭이 최종 카테고리를 정했는지)
    sub_rows = []
    for p in allp:
        for category, keyword, word in substring_hits(p["title"]):
            decided = p["category_source"] == "title" and p["category"] == category
            sub_rows.append((p, category, keyword, word, decided))

    # 단어 경계에 막힌 사례. title뿐 아니라 구조화 필드도 본다.
    # (당근 Database Engineer는 job 필드에서 막혔다)
    boundary_rows = []
    for p in allp:
        for field, text in (
            [("title", p["title"])]
            + [("occupation", o) for o in p["occupations"]]
            + [("job", j) for j in p["jobs"]]
        ):
            for category, keyword, word, related in boundary_blocked_hits(text):
                boundary_rows.append((p, field, category, keyword, word, related))
    boundary_related = [r for r in boundary_rows if r[5]]
    boundary_unrelated = [r for r in boundary_rows if not r[5]]

    bleed_rows = occupation_bleed_rows(allp)
    bleed_unrelated = [r for r in bleed_rows if r[4] == "무관"]
    bleed_related = [r for r in bleed_rows if r[4] == "관련"]
    bleed_pending = [r for r in bleed_rows if r[4] == "판정 보류"]

    by_source = {}
    for cid in company_ids:
        by_source.setdefault(srcs[cid], []).append(cid)

    L = []
    add = L.append

    add("# 키워드 감사 자료 (원자료)")
    add("")
    add(f"- 생성 시각: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}")
    add(f"- 대상 ATS: {', '.join(f'{s} {len(c)}곳' for s, c in by_source.items())}")
    add(f"- 대상 공고: `deploy=true` **{len(allp)}건**")
    add("- 생성 스크립트: `scripts/build_keyword_audit.py` (재실행 시 갱신)")
    add("- 분류 기준: `common/job_classifier.py`의 **현재 스펙 키워드** (이 문서 작성 시점에 변경 없음)")
    add("")
    add("> 이 문서는 참고자료이며 코드와 무관하다. `job_classifier.py`는 수정되지 않았고,")
    add("> STEP 6 집계도 현재 스펙 키워드 그대로 수행한다.")
    add("")
    add("## 전체 규모")
    add("")
    add("| 구분 | 건수 | 설명 |")
    add("|---|---:|---|")
    add(f"| 전체 (`deploy=true`) | {len(allp)} | |")
    add(f"| 구조화 필드로 분류됨 | {len(structured)} | occupation / job 값이 스펙 카테고리에 매칭 |")
    add(f"| **제목 키워드로만 분류됨 (오탐 검토 대상)** | **{len(title_fallback)}** | 구조화 분류 실패 → 제목 fallback (섹션 2) |")
    add(f"| **미분류 (누락)** | **{len(unclassified)}** | `category = None` (섹션 1) |")
    add(f"| **부분일치 오탐** | **{len(sub_rows)}** | 키워드가 더 긴 무관한 단어의 일부로 매칭 (섹션 3) |")
    add(f"| **단어 경계로 인한 역방향 미분류** | **{len(boundary_related)}** | "
        f"키워드가 관련 있는 복합어 안에 있으나 `\\b`로 미매칭 (섹션 4) |")
    add(f"| **구조화 필드 자체 오탐** | **{len(bleed_unrelated)}** | "
        f"직군 이름에 키워드가 섞여 무관한 업무가 분류됨 (섹션 5) |")
    add("")
    add(
        f"검토 대상: **미분류(누락) {len(unclassified)}건 + 오탐 검토 대상 {len(title_fallback)}건 "
        f"+ 부분일치 오탐 {len(sub_rows)}건 + 역방향 미분류 {len(boundary_related)}건**"
    )
    add("")
    add("> **섹션 3(부분일치 허용 시 웹툰 등 오탐 발생)과 섹션 4(부분일치 금지로 인한 "
        "Database 등 누락)는 같은 규칙 변경으로 서로 반대 방향에 영향받는다.**")
    add("")
    add("섹션 2와 섹션 3은 기준이 달라 일부 겹친다. 겹치는 건수는 섹션 3-4에 정리했다.")
    add("")
    add("### ⚠️ 우선순위 — 키워드 확장 결정 지연 시 영향 범위")
    add("")
    add("> 채널톡은 Engineering팀 공고 10건 중 6건(Software Engineer x2, DevOps Engineer,")
    add("> Security Engineer, Machine Learning Engineer, Forward Deployed Engineer)이 전부")
    add("> 미분류됨. 원인 셋: (1) team 필드가 스펙 카테고리와 매핑 안 됨")
    add("> (2) DevOps/Security 키워드 부재 (3) Machine Learning/ML 키워드 부재.")
    add("> 키워드 확장 결정을 미루면 채널톡이 서버·백엔드·데이터·AI 보유 회사 목록에서")
    add("> 통째로 빠질 수 있음 — 다른 회사 사례보다 영향 범위가 큼.")
    add("")
    add("해당 6건의 원자료는 섹션 1의 채널톡 항목에 있다.")
    add("")
    add("동일 직무명(Machine Learning Engineer)이 하이퍼커넥트(team=AI/ML)에서는 분류되고 "
        "채널톡(team=Engineering)에서는 안 됨 — 분류 결과가 직무 성격이 아니라 "
        "회사별 ATS 팀 명명 방식에 좌우됨을 보여주는 사례.")
    add("")
    add("ATS별 내역은 다음과 같다.")
    add("")
    add("| ATS | 회사 수 | 공고 | 구조화 분류 | 제목 fallback | 미분류 |")
    add("|---|---:|---:|---:|---:|---:|")
    for source, cids in by_source.items():
        rows = [p for cid in cids for p in posts[cid]]
        add(
            f"| {source} | {len(cids)} | {len(rows)} | "
            f"{len([p for p in rows if p['category_source'] == 'structured'])} | "
            f"{len([p for p in rows if p['category_source'] == 'title'])} | "
            f"{len([p for p in rows if not p['category']])} |"
        )
    add("")
    add("ATS마다 구조화 필드의 원래 이름이 다르다. 이 문서에서는 `occupation` / `job`으로 통일해 표기한다.")
    add("")
    for source in by_source:
        add(f"- **{source}**: {FIELD_MAP.get(source, '(매핑 정보 없음)')}")
    add("")
    add("현재 적용 중인 키워드는 다음과 같다.")
    add("")
    add("**제목(title)용 — 기능명세 스펙 원본**")
    add("")
    add("| 직무 | 키워드 |")
    add("|---|---|")
    for cat, kws in JOB_KEYWORDS.items():
        add(f"| {cat} | {', '.join(f'`{k}`' for k in kws)} |")
    add("")
    add("**구조화 필드(occupation/job)용 — 크롤러에서 추가한 사전**")
    add("")
    add("| 직무 | 키워드 |")
    add("|---|---|")
    for cat, kws in STRUCTURED_KEYWORDS.items():
        add(f"| {cat} | {', '.join(f'`{k}`' for k in kws)} |")
    add("")
    add("---")
    add("")

    # ---------------- 섹션 1: 미분류 원본 값 (우선 검토) ----------------
    add("## 1. 현재 스펙 키워드로 분류되지 않는 원본 값 — 우선 검토 대상")
    add("")
    add(f"`deploy=true` {len(allp)}건 중 `category = None`으로 떨어진 **{len(unclassified)}건**의 원본 값이다.")
    add("")

    add("### 1-1. 미분류 공고의 title 전수 (회사별)")
    add("")
    for cid in company_ids:
        rows = [p for p in posts[cid] if not p["category"]]
        if not rows:
            add(f"#### {names[cid]} (`{cid}`, {srcs[cid]}) — 미분류 0건")
            add("")
            continue
        add(f"#### {names[cid]} (`{cid}`, {srcs[cid]}) — 미분류 {len(rows)}건 / 전체 {len(posts[cid])}건")
        add("")
        add("| title | occupation | job |")
        add("|---|---|---|")
        for p in sorted(rows, key=lambda x: x["title"] or ""):
            occ = ", ".join(str(o) for o in p["occupations"]) or "(없음)"
            job = ", ".join(str(j) for j in p["jobs"]) or "(없음)"
            add(f"| {(p['title'] or '').replace('|', '\\|')} | {occ} | {job} |")
        add("")

    add("### 1-2. 미분류 공고에 등장한 occupation 고유값 (빈도순)")
    add("")
    c = Counter()
    for p in unclassified:
        for o in (p["occupations"] or [None]):
            c[o] += 1
    add(freq_table(c, ["occupation", "건수"]))
    add("")

    add("### 1-3. 미분류 공고에 등장한 job 고유값 (빈도순)")
    add("")
    c = Counter()
    for p in unclassified:
        for j in (p["jobs"] or [None]):
            c[j] += 1
    add(freq_table(c, ["job", "건수"]))
    add("")

    add("### 1-4. 미분류 공고의 title 토큰 빈도 (2회 이상)")
    add("")
    c = Counter()
    for p in unclassified:
        c.update(set(TOKEN.findall(p["title"] or "")))
    add(freq_table(Counter({k: v for k, v in c.items() if v >= 2}), ["토큰", "공고 수"]))
    add("")
    add("---")
    add("")

    # ---------------- 섹션 2: 구조화 실패 + 제목 fallback ----------------
    add("## 2. 구조화 분류 실패 + 제목 오탐 사례 — 우선 검토 대상")
    add("")
    add("아래 조건을 **모두** 만족하는 건이다.")
    add("")
    add("1. `occupation` / `job` 구조화 필드로는 카테고리가 배정되지 않았다.")
    add("   (값이 `null`이거나, `기술` · `Tech` · `개발`처럼 스펙 카테고리와 매칭되지 않는 값)")
    add("2. 제목 키워드 fallback이 걸려서 카테고리가 배정됐다. (`category_source = \"title\"`)")
    add("")
    add(f"그리팅 + 나인하이어 전체 `deploy=true` {len(allp)}건을 재검사한 결과 **{len(title_fallback)}건**이다.")
    add("")
    add("`매칭 키워드` 열은 제목에서 실제로 걸린 스펙 키워드다.")
    add("")
    add("| company_id | ATS | title | occupation | job | 배정된 카테고리 | 매칭 키워드 |")
    add("|---|---|---|---|---|---|---|")
    for p in sorted(title_fallback, key=lambda x: (x["company_id"], x["title"] or "")):
        occ = ", ".join(str(o) for o in p["occupations"]) or "(없음)"
        job = ", ".join(str(j) for j in p["jobs"]) or "(없음)"
        hits = ", ".join(f"`{k}`" for k in matched_keywords(p["title"], p["category"])) or "-"
        title = (p["title"] or "").replace("|", "\\|")
        add(f"| `{p['company_id']}` | {srcs[p['company_id']]} | {title} | {occ} | {job} | {p['category']} | {hits} |")
    add("")

    add("### 2-1. 이 사례들에서 구조화 분류를 막은 occupation / job 값 (빈도순)")
    add("")
    c = Counter()
    for p in title_fallback:
        for o in (p["occupations"] or [None]):
            c[o] += 1
    add("**occupation**")
    add("")
    add(freq_table(c, ["occupation", "건수"]))
    add("")
    c = Counter()
    for p in title_fallback:
        for j in (p["jobs"] or [None]):
            c[j] += 1
    add("**job**")
    add("")
    add(freq_table(c, ["job", "건수"]))
    add("")

    add("### 2-2. 배정된 카테고리별 건수")
    add("")
    add(freq_table(Counter(p["category"] for p in title_fallback), ["배정된 카테고리", "건수"]))
    add("")
    add("---")
    add("")

    # ---------------- 섹션 3: 부분일치 오탐 전수 ----------------
    add("## 3. 부분일치 오탐 전수 — 우선 검토 대상")
    add("")
    add("스펙 키워드가 **그 키워드가 아닌 더 긴 단어의 일부로** 걸린 사례다.")
    add("예: `웹`이 `웹툰`의 일부로 매칭.")
    add("")
    add("판정 방법: 제목에서 키워드가 매칭된 구간을 같은 문자 종류(한글 / 영숫자)로")
    add("좌우 확장해 실제 단어를 구한 뒤, 그 단어가 키워드 자체와 다르면 부분일치로 본다.")
    add("매칭 규칙은 `job_classifier.py`와 동일하다.")
    add("")
    add(f"전체 `deploy=true` {len(allp)}건을 검사한 결과 **{len(sub_rows)}건**이다.")
    add("")

    add("### 3-1. 키워드 × 걸린 단어별 건수")
    add("")
    add("| 키워드 | 키워드가 속한 직무 | 실제로 걸린 단어 | 건수 | 이 매칭이 최종 카테고리를 결정한 건수 |")
    add("|---|---|---|---:|---:|")
    pair_count = Counter((kw, cat, word) for _, cat, kw, word, _ in sub_rows)
    decided_count = Counter((kw, cat, word) for _, cat, kw, word, decided in sub_rows if decided)
    for (kw, cat, word), n in sorted(pair_count.items(), key=lambda x: (-x[1], x[0][0])):
        add(f"| `{kw}` | {cat} | {word} | {n} | {decided_count.get((kw, cat, word), 0)} |")
    add("")

    add("### 3-2. 사례 전수")
    add("")
    add("`최종 카테고리 결정` = 이 부분일치가 실제로 공고의 카테고리를 정했는지")
    add("(구조화 필드로 이미 분류된 건은 `아니오`).")
    add("")
    add("| company_id | ATS | title | 키워드 | 걸린 단어 | 최종 카테고리 | 최종 카테고리 결정 |")
    add("|---|---|---|---|---|---|---|")
    for p, cat, kw, word, decided in sorted(sub_rows, key=lambda x: (x[0]["company_id"], x[0]["title"] or "")):
        title = (p["title"] or "").replace("|", "\\|")
        add(
            f"| `{p['company_id']}` | {srcs[p['company_id']]} | {title} | `{kw}` | {word} | "
            f"{p['category'] or '(미분류)'} | {'예' if decided else '아니오'} |"
        )
    add("")

    add("### 3-3. 회사별 건수")
    add("")
    add(freq_table(Counter(p["company_id"] for p, *_ in sub_rows), ["company_id", "건수"]))
    add("")
    add("### 3-4. 섹션 2와의 관계")
    add("")
    sub_ids = {(p["company_id"], p["opening_id"]) for p, *_ in sub_rows if p["category_source"] == "title"}
    fb_ids = {(p["company_id"], p["opening_id"]) for p in title_fallback}
    add(f"- 섹션 2(제목 fallback으로 분류됨): {len(fb_ids)}건")
    add(f"- 그 중 이 섹션의 부분일치에 해당: {len(sub_ids & fb_ids)}건")
    add(f"- 부분일치가 아닌 채로 제목 fallback된 건: {len(fb_ids - sub_ids)}건")
    add("  (키워드가 제목에서 독립된 단어로 매칭된 경우. 예: 요기요")
    add("  `[Security] Web & Application Security`는 `Web`이 단독 단어로 걸렸으므로")
    add("  이 섹션이 아니라 섹션 2에만 해당한다.)")
    add("")
    add("---")
    add("")

    # ---------------- 섹션 4: 단어 경계로 인한 역방향 미분류 ----------------
    add("## 4. 단어 경계로 인한 역방향 미분류 — 우선 검토 대상")
    add("")
    add("섹션 1(키워드 자체가 없어서 미분류)과는 성격이 다르다.")
    add("**스펙 키워드가 텍스트에 존재하고 의미상으로도 관련 있는데,**")
    add("**단어 경계(`\\b`) 규칙 때문에 매칭되지 않은** 사례다.")
    add("")
    add("분류기는 ASCII 키워드에만 단어 경계를 적용한다. 한글 키워드는 부분일치를 그대로")
    add("허용하므로 이 섹션에 해당하지 않는다.")
    add("")
    add("판정 기준: 키워드를 품은 더 긴 영단어가 **그 키워드가 가리키는 기술 개념의**")
    add("**하위 개념이거나 합성어인가**. `Database`는 `Data`의 하위 개념이므로 해당하고,")
    add("`Webtoon`은 `Web`과 철자만 겹칠 뿐이므로 해당하지 않는다(그쪽은 섹션 3 성격).")
    add("")
    add(f"`deploy=true` {len(allp)}건의 title · occupation · job을 모두 검사한 결과")
    add(f"단어 경계에 막힌 사례는 총 {len(boundary_rows)}건이고, 그 중 **의미상 관련 있는 것은 "
        f"{len(boundary_related)}건**이다.")
    add("")

    add("### 4-1. 의미상 관련 있는 사례 (역방향 미분류)")
    add("")
    if boundary_related:
        add("| company_id | 필드 | 값 | 키워드 | 막은 단어 | 현재 최종 분류 |")
        add("|---|---|---|---|---|---|")
        for p, field, category, keyword, word, _ in sorted(
            boundary_related, key=lambda x: (x[0]["company_id"], x[0]["title"] or "")
        ):
            value = (p["title"] if field == "title" else
                     (p["occupations"] or [None])[0] if field == "occupation" else
                     (p["jobs"] or [None])[0]) or ""
            add(
                f"| `{p['company_id']}` | {field} | {str(value).replace('|', '\\|')} | "
                f"`{keyword}` | {word} | {p['category'] or '**미분류**'} |"
            )
    else:
        add("(해당 없음)")
    add("")
    add("### 4-2. 키워드별 집계")
    add("")
    add(freq_table(
        Counter(f"`{kw}` → {word}" for _, _, _, kw, word, _ in boundary_related),
        ["키워드 → 막은 단어", "건수"],
    ) if boundary_related else "(해당 없음)")
    add("")

    add("### 4-3. 같은 규칙에 막혔지만 의미상 무관한 사례 (참고)")
    add("")
    add("단어 경계 규칙이 **의도대로 오탐을 막아준** 경우다. 이 섹션의 판정 기준을")
    add("팀이 다시 검토할 때 비교 대상으로 쓰라고 함께 싣는다.")
    add("")
    add(freq_table(
        Counter(f"`{kw}` → {word}" for _, _, _, kw, word, _ in boundary_unrelated),
        ["키워드 → 막은 단어", "건수"],
    ) if boundary_unrelated else "(해당 없음)")
    add("")
    add("---")
    add("")

    # ---------------- 섹션 5: 구조화 필드 자체 오탐 ----------------
    add("## 5. 구조화 필드 자체 오탐 (occupation 오염) — 우선 검토 대상")
    add("")
    add("섹션 1~4와 구분되는 유형이다. 구조화 필드가 **정상적으로 매칭됐는데**")
    add("결과가 의미상 틀린 경우다.")
    add("")
    add("분류기는 `job`(세부 직무) → `occupation`(상위 직군) 순으로 본다.")
    add("`job`이 스펙 키워드에 걸리지 않으면 `occupation`으로 넘어가는데,")
    add("그 **직군 이름 자체에 스펙 키워드가 들어 있으면** 그 직군에 속한 무관한")
    add("업무까지 함께 분류된다. 쏘카의 `개발/데이터` 직군이 그 예로,")
    add("`데이터`가 occupation에 들어 있어 무관한 공고까지 데이터·AI로 간다.")
    add("")
    add("검출 조건:")
    add("")
    add("1. 구조화 분류이고, `job`이 아니라 `occupation`에서 매칭됐다")
    add("2. 그 `occupation` 문자열에 스펙 키워드가 포함된다")
    add("3. `job` 값도 `title`도 같은 카테고리를 뒷받침하지 않는다")
    add("")
    add(f"`deploy=true` {len(allp)}건 전체에서 위 조건에 걸린 사례는 총 "
        f"{len(bleed_rows)}건이다.")
    add("")
    add("조건 3까지는 기계적으로 판정되지만, \"의미상 무관한가\"는 직군 이름과 실제")
    add("업무를 같이 봐야 갈린다. 판정은 `(company_id, occupation)` 단위로 하고")
    add("`scripts/build_keyword_audit.py`의 `OCCUPATION_BLEED_VERDICT`에 명시했다.")
    add("목록에 없는 새 조합은 `판정 보류`로 나온다.")
    add("")
    add(f"판정 결과: **무관 {len(bleed_unrelated)}건** / 관련 {len(bleed_related)}건 "
        f"/ 판정 보류 {len(bleed_pending)}건")
    add("")

    def bleed_table(rows):
        if not rows:
            return ["(해당 없음)", ""]
        out = ["| company_id | occupation | 걸린 키워드 | job | title | 배정된 직무 |",
               "|---|---|---|---|---|---|"]
        for posting, occupation, keywords, job, _ in sorted(
            rows, key=lambda r: (r[0]["company_id"], r[0]["title"] or "")
        ):
            keys = ", ".join(f"`{k}`" for k in keywords)
            out.append(
                f"| `{posting['company_id']}` | {occupation.replace('|', '\\|')} | {keys} | "
                f"{(job or '(없음)').replace('|', '\\|')} | "
                f"{(posting['title'] or '').replace('|', '\\|')} | {posting['category']} |"
            )
        out.append("")
        return out

    add("### 5-1. 의미상 무관 (occupation 오염)")
    add("")
    for line in bleed_table(bleed_unrelated):
        add(line)

    add("### 5-2. 같은 조건에 걸렸지만 의미상 관련 있는 사례 (참고)")
    add("")
    add("직군 이름이 해당 카테고리 전용이고 실제 업무도 맞는 경우다. 5-1의 판정")
    add("기준을 팀이 다시 검토할 때 비교 대상으로 쓰라고 함께 싣는다.")
    add("")
    for line in bleed_table(bleed_related):
        add(line)

    if bleed_pending:
        add("### 5-3. 판정 보류 (새로 등장한 조합)")
        add("")
        for line in bleed_table(bleed_pending):
            add(line)

    add("---")
    add("")

    # ---------------- 섹션 6: 필드 커버리지 ----------------
    add("## 6. 회사별 occupation / job 필드 커버리지")
    add("")
    add("`deploy=true` 기준. '없음'은 해당 공고의 모든 직무 항목에서 그 필드가 `null`인 경우다.")
    add("")
    add("| company_id | 회사명 | ATS | 공고 수 | occupation 없음 | job 없음 |")
    add("|---|---|---|---:|---:|---:|")
    for cid in company_ids:
        rows = posts[cid]
        occ_none = len([p for p in rows if not any(p["occupations"])])
        job_none = len([p for p in rows if not any(p["jobs"])])
        add(f"| `{cid}` | {names[cid]} | {srcs[cid]} | {len(rows)} | {occ_none} | {job_none} |")
    add("")
    add("---")
    add("")

    # ---------------- 섹션 7~9: 회사별 전수 ----------------
    add("## 7. 회사별 title 고유값 전수 (빈도순)")
    add("")
    for cid in company_ids:
        add(f"### {names[cid]} (`{cid}`, {srcs[cid]}) — {len(posts[cid])}건")
        add("")
        if not posts[cid]:
            add("(공고 없음)")
            add("")
            continue
        c = Counter(p["title"] for p in posts[cid])
        add("| title | 건수 | 현재 분류 |")
        add("|---|---:|---|")
        cat_of = {}
        for p in posts[cid]:
            cat_of.setdefault(p["title"], p["category"])
        for title, n in sorted(c.items(), key=lambda x: (-x[1], str(x[0]))):
            cat = cat_of.get(title) or "**None**"
            add(f"| {(title or '').replace('|', '\\|')} | {n} | {cat} |")
        add("")

    add("## 8. 회사별 occupation 고유값 (빈도순)")
    add("")
    for cid in company_ids:
        add(f"### {names[cid]} (`{cid}`, {srcs[cid]})")
        add("")
        c = Counter()
        for p in posts[cid]:
            for o in (p["occupations"] or [None]):
                c[o] += 1
        add(freq_table(c, ["occupation", "건수"]) if c else "(공고 없음)")
        add("")

    add("## 9. 회사별 job 고유값 (빈도순)")
    add("")
    for cid in company_ids:
        add(f"### {names[cid]} (`{cid}`, {srcs[cid]})")
        add("")
        c = Counter()
        for p in posts[cid]:
            for j in (p["jobs"] or [None]):
                c[j] += 1
        add(freq_table(c, ["job", "건수"]) if c else "(공고 없음)")
        add("")

    add("## 10. 전체 title 토큰 빈도 (3회 이상)")
    add("")
    c = Counter()
    for p in allp:
        c.update(set(TOKEN.findall(p["title"] or "")))
    add(freq_table(Counter({k: v for k, v in c.items() if v >= 3}), ["토큰", "공고 수"]))
    add("")

    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"생성 완료: {OUT}")
    print(f"  대상 공고 {len(allp)}건 (회사 {len(company_ids)}곳)")
    print(f"  미분류(누락) {len(unclassified)}건 / 제목 fallback(오탐 검토) {len(title_fallback)}건")
    print(f"  부분일치 오탐 {len(sub_rows)}건")
    print(f"  문서 {len(L)}줄, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
