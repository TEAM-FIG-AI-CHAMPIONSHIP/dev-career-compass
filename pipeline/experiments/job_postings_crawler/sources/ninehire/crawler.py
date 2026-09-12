"""나인하이어(NineHire) 계열 공통 크롤러.

나인하이어는 호스팅 방식이 두 가지다. 새 회사가 나인하이어로 확인되면
어느 쪽인지 먼저 판별하고 접근 방법을 정해야 한다.

  (1) `*.ninehire.site` 표준 호스팅 — 이 모듈이 다루는 방식.
      robots.txt가 `Disallow: /api`라 API를 못 쓰므로
      sitemap.xml → SSR 상세 페이지(`__NEXT_DATA__`) 순으로 접근한다.
      예: 요기요(wesangcareer), 리멤버(hello.remember.co.kr)

  (2) 자체 도메인 + `api.ninehire.com` 직접 호출.
      회사가 만든 Next.js 사이트가 나인하이어 공개 API를 부른다.
      sitemap에 공고 URL이 없고 목록 HTML도 하이드레이션 전이라 비어 있으므로
      프런트 번들에서 `companyId`를 읽어 API를 직접 호출한다.
      `Disallow: /api`는 `*.ninehire.site` 호스트에만 적용되고
      `api.ninehire.com`에는 robots.txt가 없다(404).

레코드 스키마는 두 방식 모두 동일하다.

그리팅과 달리 공고 목록이 SSR되지 않는다. 목록 블록(type=job_posting)은
클라이언트에서 `/api/...`를 호출해 채우는데, 나인하이어 robots.txt가
`Disallow: /api`로 막고 있으므로 API는 쓰지 않는다.

대신 sitemap.xml이 모든 공고 상세 URL(`/job_posting/{addressKey}`)을 명시하고 있고
이 경로는 차단 대상이 아니다. 사이트가 크롤러에게 직접 알려주는 경로이므로
sitemap → 상세 페이지 순으로 접근한다. 상세 페이지는 `__NEXT_DATA__`의
`pageProps.recruitment`에 공고 메타데이터가 전부 들어있다.

필드 대응 (그리팅 ↔ 나인하이어):
  title      ↔ recruitment.externalTitle
  occupation ↔ recruitment.jobGroup.title      (직군)
  job        ↔ recruitment.jobTask.title       (세부 직무)
  deploy     ↔ recruitment.status == "in_progress"
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch  # noqa: E402
from common.job_classifier import classify_job  # noqa: E402
from common.paths import PROCESSED_DIR, RAW_DIR  # noqa: E402

NINEHIRE_COMPANIES = {
    "yogiyo": ("요기요", "https://wesangcareer.ninehire.site"),
    "remember": ("리멤버", "https://hello.remember.co.kr"),
}

LOC = re.compile(r"<loc>(.*?)</loc>", re.S)


def job_posting_urls(base_url):
    """sitemap.xml에서 공고 상세 URL 목록을 가져온다."""
    sitemap = fetch(f"{base_url}/sitemap.xml", delay=0.5)
    urls = [u.strip() for u in LOC.findall(sitemap)]
    return [u for u in urls if "/job_posting/" in u]


def extract_recruitment(html):
    """상세 페이지 __NEXT_DATA__에서 (recruitment, jobPosting) 반환."""
    tag = BeautifulSoup(html, "html.parser").find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None, None
    props = json.loads(tag.string).get("props", {}).get("pageProps", {})
    return props.get("recruitment"), props.get("jobPosting")


def to_processed(company_id, record):
    recruitment = record.get("recruitment") or {}
    occupation = (recruitment.get("jobGroup") or {}).get("title")
    job = (recruitment.get("jobTask") or {}).get("title")
    title = recruitment.get("externalTitle")

    result = classify_job(title, occupation, job)

    return {
        "company_id": company_id,
        "opening_id": recruitment.get("recruitmentId"),
        "address_key": recruitment.get("addressKey"),
        "title": title,
        # 나인하이어는 deploy 대신 status를 쓴다. in_progress만 현재 채용 중이다.
        "deploy": recruitment.get("status") == "in_progress",
        "status": recruitment.get("status"),
        "occupations": [occupation] if occupation else [],
        "jobs": [job] if job else [],
        "category": result["category"],
        "category_source": result["source"],
        "categories": [result["category"]] if result["category"] else [],
        "structured": result["structured"],
        "title_based": result["title_based"],
        "disagreement": result["disagreement"],
        "open_date": recruitment.get("createdAt"),
        "due_date": recruitment.get("closedAt"),
        "group": (recruitment.get("affiliation") or {}).get("title"),
    }


def crawl_company(company_id, company_name, base_url):
    urls = job_posting_urls(base_url)

    records, failures = [], []
    for url in urls:
        try:
            recruitment, job_posting = extract_recruitment(fetch(url))
        except Exception as exc:
            failures.append({"url": url, "error": str(exc)})
            continue
        if not recruitment:
            failures.append({"url": url, "error": "recruitment 없음"})
            continue
        records.append({"url": url, "recruitment": recruitment, "jobPosting": job_posting})

    fetched_at = datetime.now(timezone.utc).isoformat()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{company_id}.json").write_text(
        json.dumps(
            {
                "company_id": company_id,
                "company_name": company_name,
                "source": "ninehire",
                "source_url": f"{base_url}/sitemap.xml",
                "extracted_from": "job_posting 상세 __NEXT_DATA__.pageProps.recruitment",
                "fetched_at": fetched_at,
                "sitemap_job_urls": len(urls),
                "failures": failures,
                "openings": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    processed = [to_processed(company_id, r) for r in records]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / f"{company_id}.json").write_text(
        json.dumps(
            {
                "company_id": company_id,
                "company_name": company_name,
                "source": "ninehire",
                "source_url": base_url,
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
        "url": base_url,
        "sitemap_urls": len(urls),
        "raw_count": len(records),
        "deploy_true": len(active),
        "deploy_false": len(processed) - len(active),
        "classified_active": len([p for p in active if p["category"]]),
        "disagreements": [p for p in active if p["disagreement"]],
        "no_structured": len([p for p in active if not p["structured"]]),
        "failures": failures,
        "statuses": sorted({p["status"] for p in processed}),
    }


def crawl_all():
    results = []
    for company_id, (name, base_url) in NINEHIRE_COMPANIES.items():
        print(f"  수집 중: {company_id} ({name}) ...", flush=True)
        try:
            results.append(crawl_company(company_id, name, base_url))
        except Exception as exc:
            results.append({"company_id": company_id, "company_name": name, "error": str(exc), "url": base_url})
    return results


if __name__ == "__main__":
    crawl_all()
