"""가비아 — careers.gabia.com/recruit/jobs

Next.js라 목록 HTML은 비어 있다. 페이지가 부르는 하이웍스 공개 API만 쓴다.

  GET https://recruit-api.gabiaoffice.hiworks.com/v1/career-site/offices/1/announces

`/application/modification`(지원서 수정)은 요청하지 않는다.
robots.txt는 `Disallow:`(빈 값=허용).

구조화 필드:
  occupation ↔ category_position[].name
  job        ↔ 없음 (포지션 경로의 마지막 칸을 occupation으로 씀)
  deploy     ↔ apply_finish_date가 없거나 아직 지나지 않음
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import build_posting, save

COMPANY_ID = "gabia"
COMPANY_NAME = "가비아"
LIST_URL = "https://careers.gabia.com/recruit/jobs"
ANNOUNCE_API = "https://recruit-api.gabiaoffice.hiworks.com/v1/career-site/offices/1/announces"
HEADERS = {"Origin": "https://careers.gabia.com", "Referer": LIST_URL, "Accept": "application/json"}


def fetch_all():
    body = fetch_json(ANNOUNCE_API, headers=HEADERS)
    if isinstance(body, list):
        return body
    return body.get("data") or body.get("announces") or []


def position_label(record):
    rows = record.get("category_position") or []
    names = [row.get("name") or row.get("category_name") for row in rows if isinstance(row, dict)]
    names = [n for n in names if n]
    return names[-1] if names else None, names


def is_open(record):
    end = record.get("apply_finish_date")
    if not end:
        return True
    text = str(end)[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date() >= datetime.now(timezone.utc).date()
    except ValueError:
        return True


def to_processed(record):
    title = record.get("announce_name")
    occupation, path = position_label(record)
    opening_id = record.get("announce_id")
    return build_posting(
        COMPANY_ID,
        opening_id=opening_id,
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        open_date=record.get("apply_start_date"),
        due_date=record.get("apply_finish_date"),
        url=f"{LIST_URL}/{opening_id}" if opening_id else LIST_URL,
        category_path=path,
        announce_type=record.get("announce_type"),
        experience=record.get("experience"),
    )


def crawl():
    records = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=ANNOUNCE_API,
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
