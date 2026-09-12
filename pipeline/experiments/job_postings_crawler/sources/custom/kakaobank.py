"""카카오뱅크 채용 크롤러.

recruit.kakaobank.com/jobs는 목록을 `POST /api/recruits`(JSON)로 가져온다.
robots.txt는 `User-agent: * / Allow: /`로 제한이 없다.

응답에는 마감된 공고도 함께 들어있다. 페이지가 마감 여부를 판정하는 방식과 동일하게
`receiveEndDatetime`이 현재 시각보다 뒤인지로 deploy를 정한다.

필드 대응:
  title      ↔ recruitNoticeName
  occupation ↔ recruitClassName   (직군: Engineering / AI / Data / Server / Mobile ...)
  job        ↔ (없음 — 목록 API가 세부 직무를 주지 않는다)
  deploy     ↔ receiveEndDatetime > now
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json  # noqa: E402
from common.job_classifier import classify_job  # noqa: E402
from common.store import build_posting, save  # noqa: E402

COMPANY_ID = "kakaobank"
COMPANY_NAME = "카카오뱅크"
LIST_API = "https://recruit.kakaobank.com/api/recruits"
META_API = "https://recruit.kakaobank.com/api/recruits/meta/job-categories"
REFERER = "https://recruit.kakaobank.com/jobs"

HEADERS = {"Referer": REFERER, "Content-Type": "application/json"}
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def fetch_all():
    collected, page = [], 1
    while True:
        body = fetch_json(
            LIST_API, method="POST", json_body={"pageNumber": page}, headers=HEADERS
        )
        collected.extend(body.get("list") or [])
        paging = body.get("paging") or {}
        if page >= (paging.get("totalPages") or 0):
            break
        page += 1
    return collected


def fetch_job_categories():
    """직군별 공고 수 메타. 수집 결과 교차검증용."""
    return fetch_json(META_API, headers={"Referer": REFERER})


def is_open(record, now=None):
    end = record.get("receiveEndDatetime")
    if not end:
        return True  # 마감일이 없으면 상시 채용으로 본다
    try:
        return datetime.strptime(end, DATE_FORMAT) > (now or datetime.now())
    except ValueError:
        return True


def to_processed(record):
    occupation = record.get("recruitClassName")
    title = record.get("recruitNoticeName")
    url = record.get("recruitNoticeUrl")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("recruitNoticeSn"),
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        open_date=record.get("receiveStartDatetime"),
        due_date=record.get("receiveEndDatetime"),
        group=None,
        url=f"https://{url}" if url and not url.startswith("http") else url,
        recruit_type=record.get("recruitTypeName"),
    )


def crawl():
    records = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_API,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="POST /api/recruits (JSON)",
        extra={"job_categories_meta": fetch_job_categories()},
    )


if __name__ == "__main__":
    print(crawl())
