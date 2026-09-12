"""카카오 — careers.kakao.com/jobs

순수 클라이언트 렌더링 React SPA다. requests로 HTML을 받으면 `#root` 로더만
있고 공고가 없다. window.__INITIAL_STATE__ 같은 임베디드 JSON도 없다
(확인된 dunder는 `__SENTRY__`, `__reactRouterVersion`뿐).

대신 페이지가 부르는 공개 API가 있다.

  GET /public/api/jobs-attribute   직군·고용형태·스킬셋 코드
  GET /public/api/job-list         공고 목록
      ?part=TECHNOLOGY|BUSINESS_SERVICES|DESIGN|STAFF
      &company=ALL|KAKAO|SUBSIDIARY
      &page=N                      (페이지당 15건)

UI 기본값은 `company=KAKAO&part=TECHNOLOGY`라 본사 테크만 보인다.
`company=ALL`이면 관계사가 섞이지만 이 응답은 `skillSetList`가 비어 있다.
그래서 본사는 `KAKAO`, 관계사는 `SUBSIDIARY`로 나눠 받고 `realId`로 합친다.
관계사 공고는 `[공동체]` 접두어가 붙는다. 필터링하지 않고 전량 수집한다.

playwright로 페이지를 연 뒤 같은 오리진에서 위 공개 API만 호출한다.
지원·이력서·로그인 경로(`/api/applicant`, `/api/resume`, `/api/jobApply`,
`/api/v2/user-info`, `/public/api/join`, `/pool`)는 요청하지 않는다.

robots.txt: careers.kakao.com/robots.txt 는 401(빈 본문)이라
kakaocorp.com의 `Allow: /`가 이 호스트에 적용되지 않는다.
공개 채용 API만 쓰고, 401이 난 경로(`/robots.txt`, `/sitemap.xml`)는 재요청하지 않는다.

구조화 필드:
  occupation ↔ jobTypeName (테크 / 서비스비즈 / 디자인 / 스태프)
  job        ↔ skillSetList[].skillSetName (Server / Android / Algorithm/ML / Web front …)
  deploy     ↔ closeFlag == false (endDate는 상시 모집이 null)
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from playwright.sync_api import sync_playwright

from common.http_utils import USER_AGENT
from common.job_classifier import classify_job, classify_from_structured
from common.store import save, build_posting

COMPANY_ID = "kakao"
COMPANY_NAME = "카카오"
LIST_URL = "https://careers.kakao.com/jobs"
JOB_LIST_API = "https://careers.kakao.com/public/api/job-list"
ATTR_API = "https://careers.kakao.com/public/api/jobs-attribute"
PARTS = ("TECHNOLOGY", "BUSINESS_SERVICES", "DESIGN", "STAFF")
# UI 하드코딩: ALL=전체, KAKAO=본사, SUBSIDIARY=관계사.
# ALL/SUBSIDIARY 응답은 skillSetList가 비어 있으므로, 본사는 KAKAO 필터로
# 따로 받아 스킬셋을 살리고 관계사는 SUBSIDIARY로 받는다.
COMPANY_FILTERS = ("KAKAO", "SUBSIDIARY")
DELAY = 1.0


def _get_json(request, url, params=None):
    time.sleep(DELAY)
    response = request.get(url, params=params or {}, timeout=20000)
    if not response.ok:
        raise RuntimeError(f"{response.status} {url}")
    return response.json()


def fetch_all(request):
    attributes = _get_json(request, ATTR_API)
    records = []
    seen = set()
    page_meta = {}
    for company in COMPANY_FILTERS:
        for part in PARTS:
            page = 1
            while True:
                body = _get_json(
                    request,
                    JOB_LIST_API,
                    params={
                        "skillSet": "",
                        "part": part,
                        "company": company,
                        "keyword": "",
                        "employeeType": "",
                        "page": page,
                    },
                )
                page_meta[f"{company}:{part}"] = {
                    "totalJobCount": body.get("totalJobCount"),
                    "totalPage": body.get("totalPage"),
                }
                batch = body.get("jobList") or []
                for record in batch:
                    real_id = record.get("realId")
                    if not real_id or real_id in seen:
                        continue
                    seen.add(real_id)
                    records.append(record)
                total_page = body.get("totalPage") or 1
                if page >= total_page or not batch:
                    break
                page += 1
    return records, attributes, page_meta


def pick_job(occupation, skill_sets):
    names = [s.get("skillSetName") for s in (skill_sets or []) if s.get("skillSetName")]
    return next(
        (name for name in names if classify_from_structured(occupation, name)),
        names[0] if names else None,
    )


def is_open(record):
    if record.get("closeFlag"):
        return False
    if record.get("useFlag") is False:
        return False
    return True


def to_processed(record):
    occupation = record.get("jobTypeName")
    skills = record.get("skillSetList") or []
    job = pick_job(occupation, skills)
    title = record.get("jobOfferTitle")
    real_id = record.get("realId")
    return build_posting(
        COMPANY_ID,
        opening_id=real_id,
        title=title,
        deploy=is_open(record),
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        open_date=record.get("regDate"),
        due_date=record.get("endDate") or record.get("resumeSubmissionEndDatetime"),
        group=record.get("companyName"),
        url=f"https://careers.kakao.com/jobs/{real_id}" if real_id else None,
        company_code=record.get("companyCodeId"),
        skill_sets=[s.get("skillSetName") for s in skills],
        employee_type=record.get("employeeTypeName"),
        location=record.get("locationName"),
        close_flag=record.get("closeFlag"),
        main_company=record.get("mainCompanyJobOfferFlag"),
        subsidiary_real_id=str(real_id or "").startswith("S-"),
    )


def crawl():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, locale="ko-KR")
        page = context.new_page()
        page.goto(LIST_URL, wait_until="networkidle", timeout=60000)
        embedded = page.evaluate(
            """() => Object.keys(window).filter(k =>
                k.startsWith('__') && !['__SENTRY__','__reactRouterVersion'].includes(k)
            )"""
        )
        records, attributes, page_meta = fetch_all(context.request)
        browser.close()

    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from=(
            f"playwright 후 {JOB_LIST_API} (company=KAKAO+SUBSIDIARY, 임베디드 JSON={embedded or '없음'})"
        ),
        extra={
            "jobs_attribute": attributes,
            "page_meta": page_meta,
            "embedded_state_keys": embedded,
        },
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
