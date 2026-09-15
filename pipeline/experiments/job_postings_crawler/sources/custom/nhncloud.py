"""NHN Cloud — careers.nhn.com/recruits

목록 HTML은 셸뿐인 SPA다. 페이지가 부르는 공개 API만 쓴다.

  GET /v1/job-postings?page=0&size=100

지원·로그인(`/v1/accounts/renew`)은 요청하지 않는다.
robots.txt Disallow 없음.

표 대상은 NHN Cloud라 `corporation.name == "NHN Cloud"`만 남긴다.
(같은 호스트에 PAYCO·Bugs 등이 섞인다.)

구조화 필드:
  occupation ↔ jobSeries[].jobGroup.name  (Tech / Business / Corporate)
  job        ↔ jobSeries[].name           (Backend / Frontend / Data …)
  deploy     ↔ postingYn == Y 이고 finishYn != Y
  group      ↔ corporation.name
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_from_structured, classify_job
from common.store import build_posting, save

COMPANY_ID = "nhncloud"
COMPANY_NAME = "NHN Cloud"
LIST_URL = "https://careers.nhn.com/recruits"
JOBS_API = "https://careers.nhn.com/v1/job-postings"
CORP = "NHN Cloud"
HEADERS = {"Referer": LIST_URL, "Origin": "https://careers.nhn.com", "Accept": "application/json"}
PAGE_SIZE = 100


def fetch_all():
    collected, page = [], 0
    while True:
        body = fetch_json(
            JOBS_API,
            params={"page": page, "size": PAGE_SIZE, "intensive-recruiting": ""},
            headers=HEADERS,
        )
        batch = body.get("result") or []
        collected.extend(batch)
        total = int(body.get("totalCount") or (body.get("paging") or {}).get("totalSize") or 0)
        if not batch or len(collected) >= total:
            break
        page += 1
        if page > 20:
            break
    return collected, total


def pick_job(series):
    names = [item.get("name") for item in series or [] if item.get("name")]
    groups = [(item.get("jobGroup") or {}).get("name") for item in series or []]
    occupation = next((g for g in groups if g), None)
    job = next((n for n in names if classify_from_structured(occupation, n)), names[0] if names else None)
    return occupation, job


def is_open(record):
    if record.get("postingYn") != "Y":
        return False
    return record.get("finishYn") != "Y"


def to_processed(record):
    series = record.get("jobSeries") or []
    occupation, job = pick_job(series)
    title = record.get("name")
    opening_id = record.get("id")
    return build_posting(
        COMPANY_ID,
        opening_id=str(opening_id) if opening_id is not None else None,
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("postingStaDatetime"),
        due_date=record.get("postingEndDatetime"),
        group=(record.get("corporation") or {}).get("name"),
        url=f"https://careers.nhn.com/recruits/{opening_id}" if opening_id else LIST_URL,
        series_names=[s.get("name") for s in series],
        employee_type=(record.get("employeeType") or {}).get("name"),
        career_type=(record.get("careerType") or {}).get("name"),
    )


def crawl():
    records, total = fetch_all()
    cloud = [r for r in records if (r.get("corporation") or {}).get("name") == CORP]
    slim = []
    for record in cloud:
        row = dict(record)
        row.pop("jobPostingContentsItems", None)
        row.pop("introduction", None)
        slim.append(row)
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=slim,
        processed_records=[to_processed(r) for r in cloud],
        extracted_from=f"{JOBS_API} 중 corporation={CORP}",
        extra={"api_total": total, "cloud_count": len(cloud)},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
