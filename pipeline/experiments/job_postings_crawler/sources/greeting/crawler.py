"""그리팅(Greeting) 계열 공통 크롤러.

그리팅 채용 페이지는 Next.js SSR이라 홈 HTML의 <script id="__NEXT_DATA__"> 안에
React Query의 dehydratedState가 들어있고, 그 중 queryKey ["openings"] 항목에
전체 채용공고 배열이 통째로 담겨 있다. 즉 페이지 1회 GET으로 전량 수집이 가능하며
공고 상세 페이지(robots.txt 차단 대상인 /o/*/apply 등)에 접근할 필요가 없다.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch, fetch_json  # noqa: E402
from common.job_classifier import classify_from_structured, classify_job  # noqa: E402
from common.paths import PROCESSED_DIR, RAW_DIR  # noqa: E402

GREETING_COMPANIES = {
    "oliveyoung": ("올리브영", "https://career.oliveyoung.com/ko/home"),
    "yeogieotdae": ("여기어때", "https://gccompany.career.greetinghr.com/ko/home"),
    "kakaopay": ("카카오페이", "https://kakaopay.career.greetinghr.com/ko/main"),
    "kurly": ("컬리", "https://kurly.career.greetinghr.com/ko/home"),
    "musinsa": ("무신사(+29CM)", "https://www.musinsacareers.com/ko/home"),
    "ssg": ("SSG.COM", "https://ssg.career.greetinghr.com/ko/home"),
    "watcha": ("왓챠", "https://watchateam.career.greetinghr.com/ko/intro"),
    "catchtable": ("캐치테이블", "https://career.catchtable.co.kr/ko/home"),
    "kakaomobility": ("카카오모빌리티", "https://kakaomobility.career.greetinghr.com/ko/home"),
    "devsisters": ("데브시스터즈", "https://careers.devsisters.com/ko/home"),
    # STEP 4에서는 자체구축으로 분류돼 있었으나, about.myrealtrip.com/work가
    # Vite SPA로 이 그리팅 워크스페이스를 가리키는 것을 확인해 여기로 옮겼다.
    # robots.txt도 다른 10곳과 동일하다(`Allow: /` + apply 경로만 차단).
    "myrealtrip": ("마이리얼트립", "https://myrealtrip.career.greetinghr.com/ko/home"),
}

# 지정 URL에서 openings를 못 찾았을 때만 시도할 대체 경로
FALLBACK_PATHS = ["/ko/home", "/ko/main", "/ko/recruit", "/ko"]


def _looks_like_openings(value):
    return (
        isinstance(value, list)
        and value
        and isinstance(value[0], dict)
        and "openingId" in value[0]
        and "title" in value[0]
    )


def extract_openings(html):
    """__NEXT_DATA__에서 공고 배열을 뽑는다. (openings, 탐색경로) 반환.

    공고가 0건인 회사(SSG·데브시스터즈)도 빈 배열을 정상 결과로 돌려준다.
    미발견(None)과 0건([])은 다른 상태다.
    """
    tag = BeautifulSoup(html, "html.parser").find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None, "__NEXT_DATA__ 없음"

    page_props = json.loads(tag.string).get("props", {}).get("pageProps", {})

    # 1순위: queryKey가 ["openings"]인 쿼리 (그리팅 표준 구조)
    for query in page_props.get("dehydratedState", {}).get("queries", []):
        if query.get("queryKey") == ["openings"]:
            return query.get("state", {}).get("data") or [], 'queries[["openings"]]'

    # 2순위: 공고처럼 생긴 배열을 담은 다른 쿼리
    for query in page_props.get("dehydratedState", {}).get("queries", []):
        data = query.get("state", {}).get("data")
        if _looks_like_openings(data):
            key = json.dumps(query.get("queryKey"), ensure_ascii=False)
            return data, f"queries[{key}]"

    # 3순위: pageProps 전체 탐색 (사이트 구조가 다를 경우 대비)
    found = _deep_find_openings(page_props)
    if found:
        path, data = found
        return data, f"pageProps.{path}"

    return None, "openings 배열 미발견"


def extract_workspace_id(html):
    tag = BeautifulSoup(html, "html.parser").find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None
    for query in json.loads(tag.string)["props"]["pageProps"].get("dehydratedState", {}).get("queries", []):
        for part in query.get("queryKey") or []:
            if isinstance(part, dict) and "workspaceId" in part:
                return part["workspaceId"]
    return None


def fetch_openings_via_api(workspace_id, page_size=200):
    """SSR에 공고 배열이 아예 없을 때의 대비책. 그리팅 공개 API를 페이지네이션하며 호출."""
    collected, page = [], 0
    while True:
        body = fetch_json(
            f"https://api.greetinghr.com/ats/v1.1/career/workspaces/{workspace_id}/openings",
            params={"locale": "ko", "page": page, "pageSize": page_size},
        )
        data = body.get("data") or {}
        collected.extend(data.get("datas") or [])
        if len(collected) >= (data.get("totalCount") or 0) or not (data.get("datas") or []):
            break
        page += 1
    return collected


def _deep_find_openings(node, path="", depth=0):
    if depth > 8:
        return None
    if _looks_like_openings(node):
        return path, node
    if isinstance(node, dict):
        for key, value in node.items():
            hit = _deep_find_openings(value, f"{path}.{key}" if path else key, depth + 1)
            if hit:
                return hit
    elif isinstance(node, list):
        for i, value in enumerate(node[:20]):
            hit = _deep_find_openings(value, f"{path}[{i}]", depth + 1)
            if hit:
                return hit
    return None


def _positions(opening):
    return (opening.get("openingJobPosition") or {}).get("openingJobPositions") or []


def to_processed(company_id, opening):
    """원본 레코드 → 분류·정제된 레코드."""
    pairs = [
        (
            (p.get("workspaceOccupation") or {}).get("occupation"),
            (p.get("workspaceJob") or {}).get("job"),
        )
        for p in _positions(opening)
    ]

    # 공고 하나에 직무가 여러 개 붙을 수 있다. 분류에 성공하는 첫 조합을 대표로 삼고,
    # 다른 조합에서 나온 분류도 categories에 모두 남긴다.
    categories = []
    for occupation, job in pairs:
        category = classify_from_structured(occupation, job)
        if category and category not in categories:
            categories.append(category)

    representative = next(
        ((o, j) for o, j in pairs if classify_from_structured(o, j)),
        pairs[0] if pairs else (None, None),
    )

    result = classify_job(opening.get("title"), representative[0], representative[1])
    if result["category"] and result["category"] not in categories:
        categories.append(result["category"])

    return {
        "company_id": company_id,
        "opening_id": opening.get("openingId"),
        "title": opening.get("title"),
        "deploy": opening.get("deploy"),
        "occupations": [o for o, _ in pairs],
        "jobs": [j for _, j in pairs],
        "category": result["category"],
        "category_source": result["source"],
        "categories": categories,
        "structured": result["structured"],
        "title_based": result["title_based"],
        "disagreement": result["disagreement"],
        "open_date": opening.get("openDate"),
        "due_date": opening.get("dueDate"),
        "group": (opening.get("group") or {}).get("name"),
    }


def crawl_company(company_id, company_name, url):
    html = fetch(url)
    openings, path = extract_openings(html)
    used_url = url

    # openings 배열 자체가 없으면 대체 경로 → 그래도 없으면 공개 API
    if openings is None:
        base = "/".join(url.split("/")[:3])
        for candidate in FALLBACK_PATHS:
            candidate_url = base + candidate
            if candidate_url == url:
                continue
            try:
                html = fetch(candidate_url)
                openings, path = extract_openings(html)
            except Exception:
                continue  # 대체 경로는 없을 수 있으니 404 등은 넘어간다
            if openings is not None:
                used_url = candidate_url
                break

    if openings is None:
        workspace_id = extract_workspace_id(html)
        if workspace_id:
            openings = fetch_openings_via_api(workspace_id)
            path = f"API workspaces/{workspace_id}/openings"

    if openings is None:
        return {"company_id": company_id, "error": path, "url": url}

    fetched_at = datetime.now(timezone.utc).isoformat()

    # raw: __NEXT_DATA__에서 뽑은 레코드를 손대지 않고 그대로 보존
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{company_id}.json").write_text(
        json.dumps(
            {
                "company_id": company_id,
                "company_name": company_name,
                "source": "greeting",
                "source_url": used_url,
                "extracted_from": path,
                "fetched_at": fetched_at,
                "openings": openings,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # processed: 분류·정제 결과
    processed = [to_processed(company_id, o) for o in openings]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / f"{company_id}.json").write_text(
        json.dumps(
            {
                "company_id": company_id,
                "company_name": company_name,
                "source": "greeting",
                "source_url": used_url,
                "fetched_at": fetched_at,
                "postings": processed,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    active = [p for p in processed if p["deploy"]]
    return {
        "company_id": company_id,
        "company_name": company_name,
        "url": used_url,
        "extracted_from": path,
        "raw_count": len(openings),
        "deploy_true": len(active),
        "deploy_false": len(processed) - len(active),
        "classified_active": len([p for p in active if p["category"]]),
        "disagreements": [p for p in active if p["disagreement"]],
        "no_structured": len([p for p in active if not p["structured"]]),
    }


def crawl_all():
    results = []
    for company_id, (name, url) in GREETING_COMPANIES.items():
        print(f"  수집 중: {company_id} ({name}) ...", flush=True)
        try:
            results.append(crawl_company(company_id, name, url))
        except Exception as exc:
            results.append({"company_id": company_id, "company_name": name, "error": str(exc), "url": url})
    return results


if __name__ == "__main__":
    crawl_all()
