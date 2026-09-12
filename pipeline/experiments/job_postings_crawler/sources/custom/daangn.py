"""당근 채용 크롤러.

careers.daangn.com/jobs/는 공고 48건을 서버에서 그대로 렌더링하고,
각 카드의 <li>에 필터용 data 속성으로 구조화 정보가 붙어 있다.
목록 페이지 1회 요청으로 전량 수집이 가능하다.

robots.txt는 `/preview`, `/jobs/completed`, `/jobs/role/*/apply`를 막는다.
**`/jobs/completed`(마감 공고 목록)는 차단 대상이라 요청하지 않는다.**
따라서 이 크롤러가 보는 공고는 모두 열려 있는 공고다.

필드 대응:
  title      ↔ 카드 <h3>
  occupation ↔ data-division          (직군: tech / design / business ...)
  job        ↔ data-department-slugs  (세부 직무: software-engineer-backend ...)
  deploy     ↔ 항상 True (마감 공고는 별도 차단 경로에만 있다)

슬러그 → 표시 라벨 매핑은 하드코딩하지 않고 페이지의 필터 input에서 그대로 읽는다.
"""

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_utils import fetch  # noqa: E402
from common.job_classifier import classify_from_structured, classify_job  # noqa: E402
from common.store import build_posting, save  # noqa: E402

COMPANY_ID = "daangn"
COMPANY_NAME = "당근"
LIST_URL = "https://careers.daangn.com/jobs/"

TRAILING_COUNT = re.compile(r"\s*\d+\s*$")


def _label(tag):
    label = tag.find_parent("label")
    if not label:
        return None
    return TRAILING_COUNT.sub("", label.get_text(" ", strip=True)).strip() or None


def build_label_maps(soup):
    """필터 input에서 슬러그 → 라벨 매핑을 추출한다."""
    divisions, departments, corporates, employment = {}, {}, {}, {}
    for inp in soup.find_all("input"):
        value, name, label = inp.get("value"), inp.get("name"), _label(inp)
        if not value or not label:
            continue
        if name == "department" and ":" in value:
            departments[value.split(":", 1)[1]] = label
        elif name == "corp":
            corporates[value] = label
        elif name == "etype":
            employment[value] = label
        elif name is None:
            divisions[value] = label
    return divisions, departments, corporates, employment


def parse_cards(soup):
    divisions, departments, corporates, employment = build_label_maps(soup)
    records = []
    for card in soup.select("li[data-job-card]"):
        link = card.find("a", href=True)
        heading = card.find("h3")
        slugs = (card.get("data-department-slugs") or "").split()
        href = link["href"] if link else None
        records.append(
            {
                "job_id": href.rstrip("/").split("/")[-1] if href else None,
                "url": f"https://careers.daangn.com{href}" if href else None,
                "title": heading.get_text(" ", strip=True) if heading else None,
                "division_slug": card.get("data-division"),
                "division": divisions.get(card.get("data-division")),
                "department_slugs": slugs,
                "departments": [departments.get(s, s.replace("-", " ")) for s in slugs],
                "corporate_slug": card.get("data-corporate"),
                "corporate": corporates.get(card.get("data-corporate")),
                "employment_type_slug": card.get("data-employment-type"),
                "employment_type": employment.get(card.get("data-employment-type")),
                "keywords": card.get("data-keywords"),
            }
        )
    return records


def to_processed(record):
    occupation = record.get("division")
    labels = record.get("departments") or []
    job = next((d for d in labels if classify_from_structured(occupation, d)), labels[0] if labels else None)
    title = record.get("title")
    return build_posting(
        COMPANY_ID,
        opening_id=record.get("job_id"),
        title=title,
        # 마감 공고는 robots.txt가 막은 /jobs/completed에만 있다. 목록에 있으면 열려 있는 공고다.
        deploy=True,
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        group=record.get("corporate"),
        url=record.get("url"),
        all_departments=labels,
        employment_type=record.get("employment_type"),
    )


def crawl():
    soup = BeautifulSoup(fetch(LIST_URL), "html.parser")
    records = parse_cards(soup)
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=LIST_URL,
        raw_records=records,
        processed_records=[to_processed(r) for r in records],
        extracted_from="목록 페이지 HTML의 li[data-job-card] 속성",
    )


if __name__ == "__main__":
    print(crawl())
