"""농심데이터시스템(NDS) — www.ndscareers.com

JSP 목록. `/nds_recruit/app/notList.jsp` 테이블의 `javascript:goView(seq)` 행을 읽는다.
상세 POST(`notPage.jsp`)는 제목·마감 여부가 목록에 있어 요청하지 않는다.

robots.txt 없음. `[마감]`이면 deploy=false.
"""

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch
from common.job_classifier import classify_job
from common.store import build_posting, save

COMPANY_ID = "nds"
COMPANY_NAME = "농심데이터시스템(NDS)"
LIST_URL = "https://www.ndscareers.com/nds_recruit/app/notList.jsp"
MAIN_URL = "https://www.ndscareers.com/nds_recruit/main.jsp"
GO_VIEW = re.compile(r"goView\(\s*'?(\d+)'?\s*\)")
GO_PAGE = re.compile(r"goPage\(\s*'(\d+)'\s*\)")
CLOSED = re.compile(r"\[마감\]")


def parse_table(html, source_url):
    soup = BeautifulSoup(html, "html.parser")
    records, seen = [], set()
    for row in soup.select("table tr"):
        cells = [td.get_text(" ", strip=True) for td in row.find_all("td")]
        anchor = row.find("a", href=True)
        if not anchor:
            continue
        href = anchor.get("href") or ""
        match = GO_VIEW.search(href) or GO_PAGE.search(href)
        if not match:
            continue
        seq = match.group(1)
        if seq in seen:
            continue
        seen.add(seq)
        title = anchor.get_text(" ", strip=True)
        status = cells[4] if len(cells) > 4 else ""
        records.append(
            {
                "seq": seq,
                "title": title,
                "closed": bool(CLOSED.search(status or title)),
                "period": cells[2] if len(cells) > 2 else None,
                "kind": cells[3] if len(cells) > 3 else None,
                "status": status,
                "source_url": source_url,
                "url": LIST_URL,
            }
        )
    return records


def fetch_records():
    html = fetch(LIST_URL)
    records = parse_table(html, LIST_URL)
    if records:
        return records, LIST_URL
    html = fetch(MAIN_URL)
    return parse_table(html, MAIN_URL), MAIN_URL


def to_processed(record):
    title = record.get("title")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("seq"),
        title=title,
        deploy=not record.get("closed"),
        occupation=None,
        job=None,
        classification=classify_job(title, None, None),
        due_date=record.get("period"),
        url=record.get("url"),
        employment_type=record.get("kind"),
        closed=record.get("closed"),
    )


def crawl():
    records, source_url = fetch_records()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=source_url,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="notList.jsp goView 목록. 상세 POST는 미요청",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
