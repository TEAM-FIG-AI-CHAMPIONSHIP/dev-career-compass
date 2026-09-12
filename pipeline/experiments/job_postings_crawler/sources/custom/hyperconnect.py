"""하이퍼커넥트 — career.hyperconnect.com/jobs

ATS는 Lever다(채널톡과 동일). 다만 채널톡처럼 런타임에 부르는 게 아니라,
Gatsby가 빌드 시점에 Lever를 긁어 static query 결과로 구워 넣는다.
그래서 `/page-data/sq/d/{hash}.json`이 유일한 데이터 소스다.
페이지 청크에는 API 호출부가 없다(런타임 요청 없음).

메타데이터: `generator: Gatsby 4.25.9`.

⚠️ 빌드 시점 스냅샷이라 사이트 재배포 전까지 값이 갱신되지 않는다.
라인(`page-data.json`)과 같은 성격의 한계다.

static query 해시는 재배포되면 바뀌므로 하드코딩하지 않고
`/page-data/jobs/page-data.json`의 `staticQueryHashes`를 훑어
`allLever` 키를 가진 것을 찾아 쓴다.

구조화 필드:
  occupation ↔ categories.team   (AI/ML / Engineering / PM / Management / Tinder Seoul)
  job        ↔ 없음               (team보다 세부적인 직무 필드가 없다)
  deploy     ↔ 마감 필드 없음 (Lever는 게시 중인 공고만 노출)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import save, build_posting

COMPANY_ID = "hyperconnect"
COMPANY_NAME = "하이퍼커넥트"
JOBS_URL = "https://career.hyperconnect.com/jobs"
PAGE_DATA = "https://career.hyperconnect.com/page-data/jobs/page-data.json"
STATIC_QUERY = "https://career.hyperconnect.com/page-data/sq/d/{}.json"


def fetch_lever_data():
    """staticQueryHashes 중 allLever를 담은 것을 찾아 반환한다."""
    hashes = fetch_json(PAGE_DATA).get("staticQueryHashes") or []
    for query_hash in hashes:
        url = STATIC_QUERY.format(query_hash)
        try:
            data = (fetch_json(url, delay=0.3).get("data") or {})
        except Exception:
            continue
        if "allLever" in data:
            return data["allLever"], url
    raise RuntimeError("staticQueryHashes에서 allLever를 찾지 못했다")


def to_processed(record):
    categories = record.get("categories") or {}
    title = record.get("text")
    occupation = categories.get("team")
    lever_id = record.get("lever_id")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("id"),
        title=title,
        # 마감일·상태 필드가 없다. 목록에 들어오면 진행 중인 공고다.
        deploy=True,
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        # department에 Hyperconnect / Match Group / Tinder가 섞여 있다. 필터링하지 않는다.
        group=categories.get("department"),
        url=f"https://jobs.lever.co/hyperconnect/{lever_id}" if lever_id else None,
        team=occupation,
        all_teams=categories.get("teams"),
        location=categories.get("location"),
        commitment=categories.get("commitment"),
        lever_id=lever_id,
    )


def crawl():
    lever, source_url = fetch_lever_data()
    records = lever["nodes"]
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=JOBS_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=f"Gatsby static query {source_url} (allLever, 빌드 시점 스냅샷)",
        extra={"lever_teams": lever.get("teams")},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
