"""네이버 채용 크롤러.

recruit.navercorp.com은 목록을 `/rcrt/loadJobList.do`(GET, JSON)로 내려준다.
페이지 크기는 서버가 10건으로 고정하고 있어 `firstIndex`로 페이지네이션한다.
robots.txt는 404(제한 없음)이며 공고 상세 페이지는 받지 않는다.

필드 대응:
  title      ↔ annoSubject
  occupation ↔ classCdNm     (직군: Tech / Design / Corporate / Service & Business)
  job        ↔ subJobCdNm    (세부 직무: Backend / Data Engineering / AI/ML ...)
  deploy     ↔ stateCd == "0040" (채용진행중)

주의: 응답에는 계열사 공고가 섞여 있다(NAVER WEBTOON, NAVER Cloud, SNOW 등).
소속은 sysCompanyCdNm에 그대로 보존해 나중에 필터링할 수 있게 한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json  # noqa: E402
from common.job_classifier import classify_job  # noqa: E402
from common.store import build_posting, save  # noqa: E402

COMPANY_ID = "naver"
COMPANY_NAME = "네이버"
LIST_API = "https://recruit.navercorp.com/rcrt/loadJobList.do"
REFERER = "https://recruit.navercorp.com/rcrt/list.do"

STATE_IN_PROGRESS = "0040"


def fetch_all():
    collected, first_index = [], 0
    while True:
        body = fetch_json(
            LIST_API,
            params={"firstIndex": first_index},
            headers={"Referer": REFERER},
        )
        batch = body.get("list") or []
        collected.extend(batch)
        total = body.get("totalSize") or 0
        if not batch or len(collected) >= total:
            break
        first_index += len(batch)

    # annoId 기준 중복 제거 (페이지네이션 중 목록이 밀릴 경우 대비)
    seen, unique = set(), []
    for record in collected:
        if record.get("annoId") in seen:
            continue
        seen.add(record.get("annoId"))
        unique.append(record)
    return unique


def to_processed(record):
    occupation = record.get("classCdNm")
    job = record.get("subJobCdNm")
    title = record.get("annoSubject")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("annoId"),
        title=title,
        deploy=record.get("stateCd") == STATE_IN_PROGRESS,
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("staYmd"),
        due_date=record.get("endYmd"),
        group=record.get("sysCompanyCdNm"),
        url=record.get("jobDetailLink"),
        state=record.get("stateCdNm"),
    )


def crawl():
    records = fetch_all()
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_API,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="rcrt/loadJobList.do (JSON)",
    )


if __name__ == "__main__":
    print(crawl())
