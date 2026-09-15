"""아임웹 — team.imweb.me/career

페이지 빌더 셸에 `<io-team-career-app>`이 있고, 공고는 그리팅 공개 API로 온다.

  GET https://gateway-platform.imwebapis.com/greetinghr/api/jobs?page=0&pageSize=1000&status=OPEN

지원 URL(`/o/*/apply`)은 요청하지 않는다. 목록 메타만 쓴다.
robots는 로그인·장바구니·관리자만 차단.

구조화 필드:
  occupation ↔ job (Data / Engineering …)
  job        ↔ 없음 (세부 직무 필드가 제목 쪽에 있음)
  deploy     ↔ status == OPEN
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import build_posting, save

COMPANY_ID = "imweb"
COMPANY_NAME = "아임웹"
LIST_URL = "https://team.imweb.me/career"
JOBS_API = "https://gateway-platform.imwebapis.com/greetinghr/api/jobs"
HEADERS = {"Origin": "https://team.imweb.me", "Referer": LIST_URL, "Accept": "application/json"}


def fetch_all():
    body = fetch_json(JOBS_API, params={"page": 0, "pageSize": 1000, "status": "OPEN"}, headers=HEADERS)
    return body.get("openings") or [], body.get("totalCount")


def posting_url(record):
    url = record.get("url") or ""
    if url.startswith("http"):
        return url
    if url:
        return "https://" + url.lstrip("/")
    return LIST_URL


def to_processed(record):
    title = record.get("title")
    occupation = record.get("job")
    opening_id = record.get("id")
    return build_posting(
        COMPANY_ID,
        opening_id=str(opening_id) if opening_id is not None else None,
        title=title,
        deploy=record.get("status") == "OPEN",
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        due_date=record.get("dueDate"),
        url=posting_url(record),
        employment=record.get("employment"),
        place=record.get("place"),
    )


def crawl():
    records, total = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=JOBS_API,
        extra={"api_total": total},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
