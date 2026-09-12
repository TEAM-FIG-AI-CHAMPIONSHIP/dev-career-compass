"""라인 채용 크롤러.

careers.linecorp.com은 Gatsby 사이트라 빌드 시점 데이터가
`/page-data/ko/jobs/page-data.json`에 통째로 들어있다. 공고 378건 전량이
여기 있으므로 목록 페이지 1회 요청으로 끝난다.
robots.txt가 막는 건 `/ko/2021_1st`뿐이고 이 경로는 쓰지 않는다.

필드 대응:
  title      ↔ title
  occupation ↔ job_unit[].name    (직군: Engineering / Corporate / Planning ...)
  job        ↔ job_fields[].name  (세부 직무: Server-side / Web Development / Data Engineering ...)
  deploy     ↔ publish AND is_public AND 마감 안 됨

주의: 공고에 해외 법인이 대거 섞여 있다(LINE Pay Taiwan, LINE Taiwan 등).
소속(companies)과 지역(regions)을 그대로 보존해 나중에 필터링할 수 있게 한다.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json  # noqa: E402
from common.job_classifier import classify_from_structured, classify_job  # noqa: E402
from common.store import build_posting, save  # noqa: E402

COMPANY_ID = "line"
COMPANY_NAME = "라인"
PAGE_DATA = "https://careers.linecorp.com/page-data/ko/jobs/page-data.json"


def fetch_all():
    body = fetch_json(PAGE_DATA)
    return [edge["node"] for edge in body["result"]["data"]["allStrapiJobs"]["edges"]]


def _names(record, key):
    return [item.get("name") for item in (record.get(key) or []) if item.get("name")]


def is_closed(record, now=None):
    if record.get("until_filled"):
        return False  # 채용 시 마감 — 기한 없음
    end = record.get("end_date")
    if not end:
        return False
    try:
        return datetime.fromisoformat(end.replace("Z", "+00:00")) < (now or datetime.now(timezone.utc))
    except ValueError:
        return False


def to_processed(record):
    units = _names(record, "job_unit")
    fields = _names(record, "job_fields")
    companies = _names(record, "companies")
    regions = _names(record, "regions")

    occupation = units[0] if units else None
    # 세부 직무가 여러 개면 분류에 성공하는 값을 대표로 쓴다
    job = next((f for f in fields if classify_from_structured(occupation, f)), fields[0] if fields else None)

    title = record.get("title")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("strapiId"),
        title=title,
        deploy=bool(record.get("publish")) and bool(record.get("is_public")) and not is_closed(record),
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("start_date"),
        due_date=record.get("end_date"),
        group=companies[0] if companies else None,
        url=f"https://careers.linecorp.com/ko/jobs/{record.get('strapiId')}",
        companies=companies,
        regions=regions,
        cities=_names(record, "cities"),
        all_job_fields=fields,
        publish=record.get("publish"),
        until_filled=record.get("until_filled"),
    )


def crawl():
    records = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=PAGE_DATA,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="Gatsby page-data.json → allStrapiJobs",
    )


if __name__ == "__main__":
    print(crawl())
