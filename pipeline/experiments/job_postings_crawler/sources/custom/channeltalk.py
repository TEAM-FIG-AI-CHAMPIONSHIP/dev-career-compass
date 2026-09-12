"""채널톡 — channel.io/kr/careers

ATS는 Lever다(공고 본문의 개인정보 국외이전 고지에 "Lever / 미국"으로 명시되고
applyUrl·hostedUrl이 jobs.lever.co를 가리킨다). 다만 채널톡이 자체 사이트에서
Lever 공고를 `__NEXT_DATA__`의 `pageProps.jobs`로 전량 SSR하므로
요청 한 번으로 끝나고 Lever 쪽은 건드리지 않는다.

메타데이터: `author: Channel`, `og:site_name: Channel.io`. generator 태그는 없다.

robots.txt: `/kr/careers`는 차단 대상이 아니다. 차단된 경로(`/app`, `/touch`,
`/@*`, `/kr/blog/p/` 등)는 요청하지 않는다. 공고 상세도 SSR 데이터에 본문이
다 들어있어 별도 요청이 필요 없다.

구조화 필드:
  occupation ↔ categories.team        (Engineering / Product / Design / Sales / Business ...)
  job        ↔ 없음                    (팀보다 세부적인 직무 필드가 제공되지 않는다)
  deploy     ↔ 마감 필드 없음 (Lever는 게시 중인 공고만 노출)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup

from common.http_utils import fetch
from common.job_classifier import classify_job
from common.store import save, build_posting

COMPANY_ID = "channeltalk"
COMPANY_NAME = "채널톡"
CAREERS_URL = "https://channel.io/kr/careers"


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")
    next_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    return next_data["props"]["pageProps"]["jobs"]


def to_processed(record):
    categories = record.get("categories") or {}
    title = record.get("text")
    occupation = categories.get("team")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("id"),
        title=title,
        # 마감 공고는 목록에 나오지 않는다. 마감일·상태 필드 자체가 없다.
        deploy=True,
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        # department는 법인 구분(Korea(HQ))이다. 계열사 필드가 아니다.
        group=categories.get("department"),
        url=record.get("hostedUrl"),
        team=occupation,
        country=record.get("country"),
        location=categories.get("location"),
        all_locations=categories.get("allLocations"),
        commitment=categories.get("commitment"),
        workplace_type=record.get("workplaceType"),
    )


def crawl():
    records = parse_jobs(fetch(CAREERS_URL))
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=CAREERS_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="__NEXT_DATA__ pageProps.jobs (Lever 원본)",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
