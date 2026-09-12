"""뱅크샐러드 — corp.banksalad.com/jobs/

ATS는 그리팅이지만 sources/greeting/crawler.py 방식을 쓸 수 없다.

  - 그리팅 워크스페이스(`banksalad.career.greetinghr.com`)는 커리어 페이지가
    비활성 상태다(`/ko/` 404, API 응답의 `activatedAtCareerPage`가 전건 false).
  - ⚠️ 더 중요한 이유: 그 도메인의 robots.txt는 Cloudflare 관리 블록 뒤에
    사이트 자체 규칙으로 `User-agent: *` / `Disallow: /`를 붙여 **전면 차단**한다.
    다른 그리팅 11곳(`Allow: /` + `/o/*/apply`만 차단)과 다르다.
    따라서 이 도메인은 어떤 경로도 요청하지 않는다.
    processed 레코드의 `url`은 원본 값 보존용이며 크롤 대상이 아니다.

대신 뱅크샐러드가 자체 도메인에 띄운 프록시 API를 쓴다. corp 사이트의 채용공고
페이지가 실제로 호출하는 것과 같은 엔드포인트다.

메타데이터: `generator: Gatsby 4.21.1`. 공고는 빌드 데이터(`page-data.json`)에
없고 런타임에 프록시 API로 가져온다. 페이지 청크에 빌드 시점 스냅샷 JSON이
하드코딩돼 있지만 낡을 수 있어 쓰지 않는다.

robots.txt:
  - corp.banksalad.com → `Allow: /`
  - www.banksalad.com  → Disallow 목록에 `/proxy`·`/api` 관련 규칙 없음

구조화 필드:
  occupation ↔ 응답의 그룹 키 `department` (직군)
  job        ↔ `data[].job` — 현재 데이터에서는 department와 값이 항상 같다
  deploy     ↔ 마감 필드 없음 (진행 중 공고만 응답에 들어온다)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import save, build_posting

COMPANY_ID = "banksalad"
COMPANY_NAME = "뱅크샐러드"
CAREERS_URL = "https://corp.banksalad.com/jobs/"
PROXY_API = "https://www.banksalad.com/proxy/api/greeting/openings"


def fetch_openings():
    body = fetch_json(
        PROXY_API,
        headers={"Accept": "application/json", "Referer": CAREERS_URL},
    )
    return [
        dict(record, department=group["department"])
        for group in body["jobs"]
        for record in group["data"]
    ]


def to_processed(record):
    title = record.get("title")
    occupation = record.get("department")
    job = record.get("job")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("id"),
        title=title,
        # 마감일·상태 필드가 없다. 응답에 들어오면 진행 중인 공고다.
        deploy=True,
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        url=record.get("url"),
        employment_type=record.get("employmentType"),
        career_info=record.get("careerInfo"),
        activated_at_career_page=record.get("activatedAtCareerPage"),
    )


def crawl():
    records = fetch_openings()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=CAREERS_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=f"{PROXY_API} (그리팅 프록시)",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
