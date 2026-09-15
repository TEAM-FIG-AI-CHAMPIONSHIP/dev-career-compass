"""kt cloud — career.ktcloud.com/recruit.html

정적 HTML. `.jd__item`에 직무명·근무지·업무가 있다.
지원은 KT그룹 통합 `recruit.kt.com/careers/263997`로 보내지만,
그 사이트 전체 목록은 KT그룹 공고가 섞이므로 요청하지 않는다.

robots.txt 없음.

구조화 필드:
  occupation / job ↔ 없음 (제목 키워드)
  deploy           ↔ 현재 캠페인 페이지에 있으면 True
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

COMPANY_ID = "ktcloud"
COMPANY_NAME = "kt cloud"
LIST_URL = "https://career.ktcloud.com/recruit.html"
APPLY_URL = "https://recruit.kt.com/careers/263997"
SLUG = re.compile(r"[^\w가-힣]+", re.UNICODE)


def parse_items(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for index, item in enumerate(soup.select(".jd__item"), 1):
        title_el = item.select_one(".title")
        location_el = item.select_one(".location")
        location = location_el.get_text(" ", strip=True) if location_el else None
        if title_el and location_el:
            location_el.extract()
        title = re.sub(r"\s+", " ", title_el.get_text(" ", strip=True)) if title_el else None
        duties = []
        for dl in item.select("dl"):
            dt = dl.find("dt")
            label = dt.get_text(" ", strip=True) if dt else ""
            if "수행업무" in label:
                duties = [li.get_text(" ", strip=True) for li in dl.select("li")]
                break
        slug = SLUG.sub("-", title or str(index)).strip("-").lower()
        records.append(
            {
                "job_id": slug or str(index),
                "title": title,
                "location": location,
                "duties": duties,
                "url": APPLY_URL,
            }
        )
    return records


def to_processed(record):
    title = record.get("title")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("job_id"),
        title=title,
        deploy=True,
        occupation=None,
        job=None,
        classification=classify_job(title, None, None),
        url=record.get("url"),
        location=record.get("location"),
        duties=record.get("duties"),
    )


def crawl():
    records = parse_items(fetch(LIST_URL))
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="recruit.html .jd__item (kt cloud 전용, recruit.kt.com 전체는 미요청)",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
