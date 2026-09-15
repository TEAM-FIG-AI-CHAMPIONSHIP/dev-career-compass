"""인프랩 / 인프런 — inflearn.com/pages?type=withus

robots.txt가 `/api`를 막으므로 인프런 API는 요청하지 않는다
(Playwright에서도 abort). 채용 카드는 랠릿 포지션 링크다.

networkidle을 기다리면 abort한 `/api` 때문에 타임아웃 나므로 load만 기다린다.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.job_classifier import classify_job
from common.playwright_capture import capture_page, extract_dom_links
from common.store import build_posting, save

COMPANY_ID = "inflab"
COMPANY_NAME = "인프랩 / 인프런"
LIST_URL = "https://www.inflearn.com/pages?type=withus"


def crawl():
    html, _responses = capture_page(
        LIST_URL,
        wait_until="load",
        extra_wait_ms=4000,
        block_url_substrings=("inflearn.com/api",),
    )
    records = extract_dom_links(
        html, LIST_URL, href_needles=("rallit.com/positions", "/positions/")
    )
    processed = [
        build_posting(
            COMPANY_ID,
            opening_id=(r.get("url") or "").rstrip("/").split("/")[-1],
            title=r.get("title"),
            deploy=True,
            occupation=None,
            job=None,
            classification=classify_job(r.get("title"), None, None),
            url=r.get("url"),
        )
        for r in records
    ]
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=processed,
        extracted_from="playwright DOM 랠릿 포지션 링크. inflearn /api abort",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
