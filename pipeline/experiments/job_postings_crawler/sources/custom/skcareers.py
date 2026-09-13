"""SK그룹 통합 채용(skcareers.com) 크롤러.

이 저장소에는 티맵모빌리티용 SK 크롤러가 없었다. skcareers.com의
공개 목록 API(`/Recruit/GetRecruitList`)를 공통으로 두고, corpCode만
바꿔 계열사를 추가한다.

corpCode는 `/Recruit/GetAutocomplete` (type=CorpCode)에서 확인한다.
  SK플래닛     10052
  티맵모빌리티 10084

목록 API가 내려주는 행은 현재 진행 중인 공고다. 마감분은 목록에 없다.
상세 페이지는 쓰지 않는다.

필드 대응:
  title      ↔ title
  occupation ↔ jobRole
  job        ↔ 없음
  deploy     ↔ 목록에 있으면 True (remainDay < 0 이면 False)
  group      ↔ corpName
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_job
from common.store import build_posting, save

LIST_URL = "https://www.skcareers.com/Recruit/GetRecruitList"
INDEX_URL = "https://www.skcareers.com/Recruit/Index"

SK_COMPANIES = {
    "skplanet": ("SK플래닛", "10052"),
}

FORM_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": INDEX_URL,
}


def fetch_list(corp_code):
    body = fetch_json(
        LIST_URL,
        method="POST",
        headers=FORM_HEADERS,
        data={
            "sort": "2",
            "searchText": "",
            "corpCode": corp_code,
            "jobRole": "",
            "recruitType": "",
            "workingType": "",
            "workingRegion": "",
        },
    )
    if not body.get("success"):
        raise RuntimeError(f"GetRecruitList 실패: {body}")
    return body.get("list") or [], body.get("totalCount")


def to_processed(company_id, record):
    title = record.get("title")
    occupation = record.get("jobRole")
    remain = record.get("remainDay")
    deploy = remain is None or remain >= 0
    return build_posting(
        company_id,
        opening_id=record.get("noticeID") or record.get("jobNoticeNo"),
        title=title,
        deploy=deploy,
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        open_date=record.get("start"),
        due_date=record.get("end"),
        group=record.get("corpName"),
        url=f"https://www.skcareers.com/Recruit/Detail/{record.get('noticeID')}"
        if record.get("noticeID")
        else None,
        job_notice_no=record.get("jobNoticeNo"),
        recruit_type=record.get("recruitType"),
        working_type=record.get("workingType"),
        working_area=record.get("workingArea"),
        remain_day=remain,
    )


def crawl_company(company_id, company_name, corp_code):
    records, total = fetch_list(corp_code)
    return save(
        company_id,
        company_name,
        source="custom",
        source_url=INDEX_URL,
        raw_records=records,
        processed_records=[to_processed(company_id, r) for r in records],
        extracted_from="POST /Recruit/GetRecruitList",
        extra={"corp_code": corp_code, "api_total": total},
    )


def crawl_all():
    results = []
    for company_id, (name, corp_code) in SK_COMPANIES.items():
        print(f"  수집 중: {company_id} ({name}, corpCode={corp_code}) ...", flush=True)
        results.append(crawl_company(company_id, name, corp_code))
    return results


if __name__ == "__main__":
    import json

    for row in crawl_all():
        print(json.dumps(row, ensure_ascii=False, indent=2))
