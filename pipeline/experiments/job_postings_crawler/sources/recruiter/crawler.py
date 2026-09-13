"""리크루터(recruiter.co.kr / Jobflex) 공통 크롤러.

GS리테일·컴투스 등 `*.recruiter.co.kr` 커리어 사이트는 Next.js App Router라
목록 HTML에는 공고가 없다. 브라우저가 부르는 공개 API는 아래다.

  POST https://api-recruiter.recruiter.co.kr/position/v1/jobflex
  POST https://api-recruiter.recruiter.co.kr/position/v2/jobflex/setting

회사 구분은 헤더 `prefix: {host}` 로 한다. 본문 호스트의 `/app` 은
robots.txt가 막으므로 요청하지 않는다. 첨부(`/attachFile`)도 받지 않는다.

필드 대응:
  title      ↔ title
  occupation ↔ 직군 필터명(있으면) 또는 classificationCode
  job        ↔ 없음
  deploy     ↔ openStatus == OPEN 이고 submissionStatus == IN_SUBMISSION
  group      ↔ classificationCode가 계열사 태그일 때 그 값
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch_json
from common.job_classifier import classify_from_structured, classify_job
from common.store import build_posting, save

LIST_API = "https://api-recruiter.recruiter.co.kr/position/v1/jobflex"
SETTING_API = "https://api-recruiter.recruiter.co.kr/position/v2/jobflex/setting"
PAGE_SIZE = 100

# 신입/경력/공채처럼 직무가 아닌 분류 코드. occupation으로 쓰지 않는다.
CAREER_CODES = {"신입", "경력", "인턴", "공채", "상시", "신입/경력"}

RECRUITER_COMPANIES = {
    "gsretail": ("GS리테일", "https://gsretail.recruiter.co.kr/career/job"),
    "com2us": ("컴투스", "https://com2us.recruiter.co.kr/career/career"),
}


def _host(source_url):
    return urlparse(source_url).netloc


def _headers(host):
    return {
        "prefix": host,
        "Referer": f"https://{host}/",
        "Origin": f"https://{host}",
        "Content-Type": "application/json",
    }


def _empty_filter(**overrides):
    body = {
        "keyword": "",
        "tagSnList": [],
        "jobGroupSnList": [],
        "careerTypeList": [],
        "regionSnList": [],
        "submissionStatusList": [],
        "openStatusList": [],
        "resumeLanguageTypeList": [],
    }
    body.update(overrides)
    return body


def fetch_settings(host):
    return fetch_json(
        SETTING_API,
        method="POST",
        headers=_headers(host),
        json_body={"filter": {"resumeLanguageTypeList": ["KOR"]}},
    )


def fetch_page(host, page, job_group_sn=None):
    filt = _empty_filter(jobGroupSnList=[job_group_sn] if job_group_sn else [])
    return fetch_json(
        LIST_API,
        method="POST",
        headers=_headers(host),
        json_body={
            "pageableRq": {"page": page, "size": PAGE_SIZE, "sort": ["CREATED_DATE_TIME"]},
            "filter": filt,
        },
    )


def fetch_all(host):
    collected, page, total = [], 1, None
    while True:
        body = fetch_page(host, page)
        batch = body.get("list") or []
        if total is None:
            total = (body.get("pagination") or {}).get("totalCount") or 0
        collected.extend(batch)
        if not batch or len(collected) >= total:
            break
        page += 1
    return collected, total


def fetch_job_group_map(host, settings):
    """직군 필터가 있으면 직군별로 다시 받아 positionSn → 직군명 목록을 만든다."""
    groups = ((settings.get("filterOption") or {}).get("jobGroupList")) or []
    mapping = {}
    for group in groups:
        sn, name = group.get("sn"), group.get("name")
        if not sn or not name:
            continue
        page, seen = 1, 0
        while True:
            body = fetch_page(host, page, job_group_sn=sn)
            batch = body.get("list") or []
            total = (body.get("pagination") or {}).get("totalCount") or 0
            for row in batch:
                mapping.setdefault(row.get("positionSn"), []).append(name)
            seen += len(batch)
            if not batch or seen >= total:
                break
            page += 1
    return mapping


def _is_job_code(code):
    if not code or code in CAREER_CODES:
        return False
    if _group_name(code):
        return False
    return True


def _group_name(name):
    if not name:
        return None
    if name.startswith("GS") or "네트웍스" in name or "넷비전" in name:
        return name
    return None


def _occupation(record, job_groups):
    """classificationCode가 직무면 그걸 쓰고, 신입/경력·계열사 태그면 직군 필터명을 쓴다."""
    code = record.get("classificationCode")
    if _is_job_code(code):
        return code
    for name in job_groups or []:
        if classify_from_structured(name, None):
            return name
    if job_groups:
        return job_groups[0]
    return None


def _group(record):
    """GS네트웍스·GS넷비전처럼 분류 코드가 계열사명일 때만 group으로 남긴다."""
    names = [record.get("classificationCode")]
    names.extend(t.get("tagName") for t in (record.get("tagList") or []))
    for name in names:
        found = _group_name(name)
        if found:
            return found
    return None


def to_processed(company_id, record, source_url, job_groups):
    title = record.get("title")
    occupation = _occupation(record, job_groups)
    deploy = record.get("openStatus") == "OPEN" and record.get("submissionStatus") == "IN_SUBMISSION"
    position_sn = record.get("positionSn")
    host = _host(source_url)
    return build_posting(
        company_id,
        opening_id=position_sn,
        title=title,
        deploy=deploy,
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        open_date=record.get("startDateTime"),
        due_date=record.get("endDateTime"),
        group=_group(record),
        url=f"https://{host}/career/jobs/{position_sn}" if position_sn else None,
        job_groups=job_groups,
        classification_code=record.get("classificationCode"),
        career_type=record.get("careerType"),
        submission_status=record.get("submissionStatus"),
        open_status=record.get("openStatus"),
        dday=record.get("dday"),
    )


def crawl_company(company_id, company_name, source_url):
    host = _host(source_url)
    settings = fetch_settings(host)
    records, total = fetch_all(host)
    group_map = fetch_job_group_map(host, settings)
    processed = [
        to_processed(company_id, row, source_url, group_map.get(row.get("positionSn")) or [])
        for row in records
    ]
    return save(
        company_id,
        company_name,
        source="recruiter",
        source_url=source_url,
        raw_records=records,
        processed_records=processed,
        extracted_from="POST api-recruiter.recruiter.co.kr/position/v1/jobflex",
        extra={
            "api_total": total,
            "job_group_map_size": len(group_map),
            "settings_tag_count": len(((settings.get("tag") or {}).get("tagList")) or []),
        },
    )


def crawl_all():
    results = []
    for company_id, (name, url) in RECRUITER_COMPANIES.items():
        print(f"  수집 중: {company_id} ({name}) ...", flush=True)
        try:
            results.append(crawl_company(company_id, name, url))
        except Exception as exc:
            results.append({"company_id": company_id, "company_name": name, "error": str(exc), "url": url})
    return results


if __name__ == "__main__":
    import json

    for row in crawl_all():
        print(json.dumps({k: v for k, v in row.items() if k != "disagreements"}, ensure_ascii=False, indent=2))
