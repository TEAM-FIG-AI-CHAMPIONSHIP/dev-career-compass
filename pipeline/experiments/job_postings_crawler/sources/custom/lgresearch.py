"""LG AI연구원 — www.lgresearch.ai/careers

Nuxt SPA라 목록 HTML의 __NUXT__는 비어 있다. 페이지가 부르는 공개 API만 쓴다.

  GET /api/board/rcrt/list     pg, pgSz, schLangTp=KR, schExpsYn=Y
  GET /api/system/code/list    코드 → 라벨 (jobtypeCd / rlmCd / groupCd)

지원 호스트(productrecruit.lgresearch.ai)는 쓰지 않는다.
robots.txt는 Disallow가 없다.

구조화 필드:
  occupation ↔ groupCd 라벨 (AI Research / AI Engineering …)
  job        ↔ rlmCd 라벨 (EXAONE / Platform & Infra …)
  deploy     ↔ expsYn == Y 이고 마감일이 지나지 않음
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import build_posting, save

COMPANY_ID = "lgresearch"
COMPANY_NAME = "LG AI연구원"
LIST_URL = "https://www.lgresearch.ai/careers"
LIST_API = "https://www.lgresearch.ai/api/board/rcrt/list"
CODE_API = "https://www.lgresearch.ai/api/system/code/list"
PAGE_SIZE = 10


def _payload(body):
    if not isinstance(body, dict):
        return {}
    data = body.get("data")
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"list": data}
    return body


def fetch_codes():
    try:
        body = fetch_json(CODE_API, headers={"Referer": LIST_URL})
    except Exception:
        return {}
    rows = _payload(body).get("list") or []
    mapping = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = row.get("cd") or row.get("code")
        name = row.get("nm") or row.get("name")
        if code and name:
            mapping[str(code)] = name
    return mapping


def fetch_page(page_index):
    return fetch_json(
        LIST_API,
        params={"pg": page_index, "pgSz": PAGE_SIZE, "schLangTp": "KR", "schExpsYn": "Y"},
        headers={"Referer": LIST_URL, "Accept": "application/json"},
    )


def fetch_all():
    collected, page_index, total = [], 1, None
    while True:
        payload = _payload(fetch_page(page_index))
        batch = payload.get("list") or []
        if total is None:
            total = payload.get("totalSize") or 0
        if not batch:
            break
        for record in batch:
            slim = dict(record)
            slim.pop("cont", None)
            collected.append(slim)
        if total and len(collected) >= total:
            break
        if len(batch) < PAGE_SIZE:
            break
        page_index += 1
        if page_index > 50:
            break
    seen, unique = set(), []
    for record in collected:
        key = record.get("seq")
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique, total if total is not None else len(unique)


def _label(codes, value):
    if value is None or value == "":
        return None
    return codes.get(str(value)) or str(value)


def _first_code(value):
    if not value:
        return None
    return str(value).split(",")[0].strip() or None


def is_open(record):
    if str(record.get("expsYn") or "Y").upper() != "Y":
        return False
    end = record.get("prdEndYmd")
    if not end:
        return True
    digits = "".join(ch for ch in str(end) if ch.isdigit())[:8]
    if len(digits) != 8:
        return True
    try:
        return datetime.strptime(digits, "%Y%m%d").date() >= datetime.now(timezone.utc).date()
    except ValueError:
        return True


def to_processed(record, codes):
    title = record.get("jbrl") or record.get("title")
    occupation = _label(codes, _first_code(record.get("groupCd")))
    job = _label(codes, _first_code(record.get("rlmCd")))
    employment = _label(codes, _first_code(record.get("jobtypeCd")))
    seq = record.get("seq")
    return build_posting(
        COMPANY_ID,
        opening_id=str(seq) if seq is not None else None,
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("prdStrtYmd") or record.get("rgstYmd"),
        due_date=record.get("prdEndYmd"),
        group=occupation,
        url=f"{LIST_URL}/{seq}" if seq is not None else LIST_URL,
        employment_type=employment,
        office=_label(codes, _first_code(record.get("officeCd"))),
    )


def crawl():
    codes = fetch_codes()
    records, total = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r, codes) for r in records],
        extracted_from=f"{LIST_API} (pg/pgSz, schExpsYn=Y, schLangTp=KR)",
        extra={"api_total": total, "code_count": len(codes)},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
