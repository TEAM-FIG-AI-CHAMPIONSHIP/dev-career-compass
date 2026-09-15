"""삼성 — www.samsungcareers.com/hr/

관계사 통합 포털. 목록은 POST `/hr/list.data`가 HTML 조각을 내려준다.
상세(`detail.data`)·스크랩(`bookmark.cmd`)·이력서(`/api/resume/list`)는 요청하지 않는다.

robots.txt 없음. 계열사는 `company` 필드로 남긴다.
삼성반도체는 `samsungds.py`가 같은 목록에서 DS부문만 자른다.

구조화 필드:
  occupation ↔ 없음
  job        ↔ 플래그(회로설계, 시스템 소프트웨어 …) 중 분류에 매칭되는 값
  deploy     ↔ 목록에 있으면 진행 중 (마감분은 목록에서 빠지거나 D- 음수)
  group      ↔ 회사명 (삼성전자 DS부문, 삼성SDI …)
"""

import json
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import DEFAULT_TIMEOUT, HEADERS
from common.job_classifier import classify_from_structured, classify_job
from common.store import build_posting, save

COMPANY_ID = "samsung"
COMPANY_NAME = "삼성"
LIST_URL = "https://www.samsungcareers.com/hr/?ty=A"
LIST_DATA = "https://www.samsungcareers.com/hr/list.data"

DS_HINTS = ("DS부문", "DS Division")


def _post_list(page_no):
    time.sleep(1)
    response = requests.post(
        LIST_DATA,
        headers={
            **HEADERS,
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Referer": LIST_URL,
        },
        data={
            "currentPageNo": page_no,
            "intNo": 0,
            "strVal": "",
            "strTxt": "",
            "strKey": "",
            "strCompany": "",
            "strType": "",
            "strOrderBy": "",
            "strEntity": "",
        },
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    if response.encoding and response.encoding.lower() in ("iso-8859-1", "latin-1"):
        response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    count_el = soup.select_one("input.divCnt")
    total = int(count_el["data-value"]) if count_el and count_el.get("data-value") else None
    max_page = int(count_el["data-max"]) if count_el and count_el.get("data-max") else 1
    records = []
    for item in soup.select("li a[data-value]"):
        title_el = item.select_one("h3.title")
        if not title_el:
            continue
        company_el = item.select_one("p.company")
        period_el = item.select_one(".period")
        flags = [span.get_text(" ", strip=True) for span in item.select(".flag.grey")]
        seq = (item.get("data-value") or "").replace(",", "")
        records.append(
            {
                "seq": seq,
                "title": title_el.get_text(" ", strip=True),
                "company": company_el.get_text(" ", strip=True) if company_el else None,
                "period": period_el.get_text(" ", strip=True) if period_el else None,
                "flags": flags,
                "url": f"https://www.samsungcareers.com/hr/?no={seq}" if seq else LIST_URL,
            }
        )
    return records, total, max_page


def fetch_records():
    first_html = _post_list(1)
    records, total, max_page = parse_page(first_html)
    for page in range(2, (max_page or 1) + 1):
        more, _, _ = parse_page(_post_list(page))
        records.extend(more)
    seen, unique = set(), []
    for record in records:
        if record["seq"] in seen:
            continue
        seen.add(record["seq"])
        unique.append(record)
    return unique, total


def is_ds(record):
    company = record.get("company") or ""
    return any(hint in company for hint in DS_HINTS)


def to_processed(company_id, record):
    title = record.get("title")
    flags = record.get("flags") or []
    job = next((flag for flag in flags if classify_from_structured(None, flag)), flags[0] if flags else None)
    return build_posting(
        company_id,
        opening_id=record.get("seq"),
        title=title,
        deploy=True,
        occupation=None,
        job=job,
        classification=classify_job(title, None, job),
        due_date=record.get("period"),
        group=record.get("company"),
        url=record.get("url"),
        flags=flags,
    )


def crawl(company_id=COMPANY_ID, company_name=COMPANY_NAME, ds_only=False):
    records, total = fetch_records()
    if ds_only:
        records = [r for r in records if is_ds(r)]
    note = f"{LIST_DATA} HTML. 상세·스크랩 미요청"
    if ds_only:
        note += ". DS부문만"
    return save(
        company_id,
        company_name,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(company_id, r) for r in records],
        extracted_from=note,
        extra={"list_total": total},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
