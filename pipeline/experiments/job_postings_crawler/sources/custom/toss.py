"""토스 — toss.im/career/jobs (Greenhouse 목록 API)

부분 가능 등급. toss.im robots.txt:

  Allow: /career/jobs
  Disallow: /career/jobs?*
  Disallow: /career/job-detail?gh_jid=5599901003   (특정 상세 1건)
  Disallow: /career/apply-admin/
  Crawl-delay: 없음

목록 페이지만 허용되고 쿼리스트링은 막혀 있다. `__NEXT_DATA__`의
`job-list-container`는 SSR에서 null이라 공고가 없다.

실제 목록은 페이지가 부르는 공개 API에 있다.

  GET https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs

응답 `success`는 Greenhouse Job 배열이다. 상세 페이지·지원 경로는
요청하지 않는다 (목록 메타데이터에 직군·계열사·고용형태가 들어 있다).

구조화 필드:
  occupation ↔ metadata \"커리어 페이지 노출 Job Category\"
  job        ↔ metadata \"세부 포지션 명\"
  group      ↔ metadata \"포지션의 소속 자회사\"
  deploy     ↔ 미노출 플래그가 true가 아니면 진행 중
               (application_deadline 필드는 전부 null)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import save, build_posting

COMPANY_ID = "toss"
COMPANY_NAME = "토스"
LIST_URL = "https://toss.im/career/jobs"
JOBS_API = "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs"
REFERER = {"Accept": "application/json", "Origin": "https://toss.im", "Referer": LIST_URL}

META_SUBSIDIARY = "포지션의 소속 자회사를 선택해 주세요."
META_CATEGORY = "커리어 페이지 노출 Job Category 값을 선택해주세요"
META_POSITION = "세부 포지션 명을 작성해주세요."
META_HIDDEN = '커리어페이지 메뉴에 "미노출" 되어야 하는 Job인가요?'
META_CLOSE_DATE = "커리어페이지 채용공고 클로징 일자 (서류접수 마감일이 정해진 경우)"
META_EMPLOYMENT = "Employment_Type"


def meta_value(record, name):
    for item in record.get("metadata") or []:
        if item.get("name") == name:
            return item.get("value")
    return None


def is_open(record):
    hidden = meta_value(record, META_HIDDEN)
    if hidden is True or hidden == "true":
        return False
    return True


def to_processed(record):
    occupation = meta_value(record, META_CATEGORY)
    job = meta_value(record, META_POSITION)
    title = record.get("title")
    opening_id = str(record.get("id") or record.get("internal_job_id"))
    return build_posting(
        COMPANY_ID,
        opening_id=opening_id,
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("first_published"),
        due_date=meta_value(record, META_CLOSE_DATE) or record.get("application_deadline"),
        group=meta_value(record, META_SUBSIDIARY),
        url=None,  # job-detail은 robots/명세상 요청하지 않음. 목록 URL만 기록
        list_url=LIST_URL,
        greenhouse_id=record.get("id"),
        company_name_field=record.get("company_name"),
        employee_type=meta_value(record, META_EMPLOYMENT),
        location=(record.get("location") or {}).get("name"),
        hidden=meta_value(record, META_HIDDEN),
    )


def crawl():
    payload = fetch_json(JOBS_API, headers=REFERER)
    records = payload.get("success") or []
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=JOBS_API,
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
