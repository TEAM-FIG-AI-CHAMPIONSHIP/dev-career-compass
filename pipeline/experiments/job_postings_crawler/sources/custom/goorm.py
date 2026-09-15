"""구름 — goorm.co/career

자체 구축 SPA. robots.txt 없음. 목록 JSON이 없어 Playwright로 렌더한 뒤
`/career/{uuid}` 앵커만 모은다. "더 알아보기" 중복 링크는 버린다.
로그인·지원 폼은 열지 않는다.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.playwright_capture import capture_page, extract_dom_links
from common.job_classifier import classify_job
from common.store import build_posting, save

COMPANY_ID = "goorm"
COMPANY_NAME = "구름"
LIST_URL = "https://goorm.co/career"
UUID_PATH = re.compile(r"/career/[0-9a-f-]{8,}$", re.I)
SKIP_TITLES = {"더 알아보기", "자세히 보기", "지원하기", "Apply"}


def crawl():
    html, _responses = capture_page(LIST_URL, wait_selector="a[href*='/career/']")
    raw_links = extract_dom_links(html, LIST_URL, href_needles=("/career/",), min_title=2)
    records, seen = [], set()
    for item in raw_links:
        url = (item.get("url") or "").split("?")[0].rstrip("/")
        title = (item.get("title") or "").strip()
        if title in SKIP_TITLES or not UUID_PATH.search(url):
            continue
        if url in seen:
            continue
        seen.add(url)
        records.append({"title": title, "url": url, "opening_id": url.rsplit("/", 1)[-1]})
    processed = [
        build_posting(
            COMPANY_ID,
            opening_id=r["opening_id"],
            title=r["title"],
            deploy=True,
            occupation=None,
            job=None,
            classification=classify_job(r["title"], None, None),
            url=r["url"],
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
        extracted_from="playwright DOM /career/{uuid} (더 알아보기 중복 제거)",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
