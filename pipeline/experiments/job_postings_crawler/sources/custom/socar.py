"""쏘카 — www.socarcorp.kr/careers/jobs

ATS는 그리팅이다(공고 상세가 `socar.career.greetinghr.com/ko/o/{id}`).
다만 마이리얼트립처럼 그리팅 원본 스키마를 그대로 노출하지 않고, 쏘카가
자체 스키마(코드값)로 변환해 Next.js SSR에 넣는다. 그래서 sources/greeting/crawler.py의
`extract_openings`로는 잡히지 않고(`["openings"]` 배열이 없다) 별도 처리한다.

⚠️ robots.txt: `Allow: /` + **`Disallow: /api/`**
쏘카 자체 API는 차단 대상이므로 요청하지 않는다. 공고 목록은
`__NEXT_DATA__`의 `pageProps.jobList.jsonResult.data`에 전량 들어 있어
페이지 요청 한 번으로 끝난다. 그리팅 상세 URL도 요청하지 않는다.

메타데이터: `og:site_name: 쏘카 | 채용공고`. generator·author 태그는 없고,
HTML에 `greetinghr` 문자열이 39번 나오는 것으로 ATS를 식별했다.

`pageProps.codeList.jsonResult`는 `null`이라 코드 라벨이 오지 않는다.
필터 UI(버튼 · 체크박스)에서 코드 → 라벨 매핑을 뽑아 쓴다.

구조화 필드:
  occupation ↔ job_group_code 라벨 (개발/데이터 · 사업/운영 · 디자인 ...)
  job        ↔ 없음 (세부 직무 필드가 제공되지 않는다)
  deploy     ↔ 마감 필드 없음 (목록에 있으면 진행 중)
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup

from common.http_utils import fetch
from common.job_classifier import classify_job
from common.store import save, build_posting

COMPANY_ID = "socar"
COMPANY_NAME = "쏘카"
LIST_URL = "https://www.socarcorp.kr/careers/jobs"

CODE_PATTERN = re.compile(r"^(JG|CR|ET|WA)\d+$")


def build_code_labels(soup):
    """필터 UI에서 코드 → 라벨 매핑을 추출한다.

    직군은 `<button value="JG01">개발/데이터</button>`,
    고용형태·근무지는 `<input value="ET01">` + 짝지어진 `<label>` 형태다.
    """
    labels = {}
    for button in soup.find_all("button"):
        code = (button.get("value") or "").strip()
        if CODE_PATTERN.match(code):
            labels[code] = button.get_text(" ", strip=True)
    for field in soup.find_all("input"):
        code = (field.get("value") or "").strip()
        if not CODE_PATTERN.match(code) or code in labels:
            continue
        label = soup.find("label", attrs={"for": field.get("id")})
        if label:
            labels[code] = label.get_text(" ", strip=True)
    return labels


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")
    next_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    payload = next_data["props"]["pageProps"]["jobList"]["jsonResult"]
    return payload["data"], build_code_labels(soup), payload.get("processedDateTime")


def to_processed(record, labels):
    title = record.get("title")
    occupation = labels.get(record.get("job_group_code"))
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("recruitment_id"),
        title=title,
        # 마감일·상태 필드가 없다. 목록에 있으면 진행 중인 공고다.
        deploy=True,
        occupation=occupation,
        job=None,
        classification=classify_job(title, occupation, None),
        # 나인투원 등 계열사가 섞여 있다. 보존만 하고 필터링하지 않는다.
        group=record.get("company_name"),
        url=record.get("notice_url"),
        job_group_code=record.get("job_group_code"),
        career=labels.get(record.get("career_code")),
        employment_type=labels.get(record.get("employment_type_code")),
        work_area=labels.get(record.get("work_area_code")),
    )


def crawl():
    records, labels, processed_at = parse_jobs(fetch(LIST_URL))
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r, labels) for r in records],
        extracted_from="__NEXT_DATA__ pageProps.jobList.jsonResult.data",
        extra={"code_labels": labels, "api_processed_at": processed_at},
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
