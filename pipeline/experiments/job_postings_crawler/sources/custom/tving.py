"""티빙 — team.tving.com

oopy(lazyrockets)로 만든 Notion 기반 사이트다. ATS가 아니라 Notion 데이터베이스가
공고 목록이고, `__NEXT_DATA__`의 `pageProps.recordMap` / `queryCollectionResult`에
Notion 원본 레코드가 그대로 SSR된다. 요청 한 번으로 전부 얻는다.

메타데이터: generator·author 태그 없음. oopy는 인라인 스크립트의
`oopy.lazyrockets.com` CDN URL로 식별했다.

robots.txt: `Allow: /` + `Disallow: /_private/`.
공고 상세는 `/{blockId}` 경로라 차단 대상이 아니지만, 목록 레코드에 필요한
필드가 다 있으므로 상세 페이지는 요청하지 않는다.

구조화 필드:
  occupation ↔ 컬렉션 이름 ("💻 개발직군" / "📋 일반직군")
  job        ↔ "기술스택" / "주요스킬" multi_select
  deploy     ↔ "접수 마감일" >= 오늘
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup

from common.http_utils import fetch
from common.job_classifier import classify_job, classify_from_structured
from common.store import save, build_posting

COMPANY_ID = "tving"
COMPANY_NAME = "티빙"
JOBS_URL = "https://team.tving.com/1572d1a8-9f4c-818b-beaf-ea42984678c6"

DEADLINE_FIELD = "접수 마감일"
JOB_FIELDS = ("기술스택", "주요스킬")
# 컬렉션 이름 앞에 붙는 이모지를 떼어낸다. ("💻 개발직군" → "개발직군")
LEADING_EMOJI = re.compile(r"^[^\w가-힣]+\s*")


def plain_text(value):
    """Notion rich text 배열을 문자열로 편다. 날짜는 start_date를 꺼낸다."""
    if not value:
        return None
    parts = []
    for segment in value:
        text = segment[0]
        annotations = segment[1] if len(segment) > 1 else []
        if text == "‣":
            for annotation in annotations or []:
                if annotation[0] == "d":
                    parts.append(annotation[1].get("start_date"))
        else:
            parts.append(text)
    # Notion은 multi_select도 "A,B" 한 덩어리로 주므로 세그먼트는 그냥 이어 붙인다.
    joined = "".join(p for p in parts if p)
    return joined or None


def parse_rows(next_data):
    """recordMap의 컬렉션 행(page 블록)을 평평한 dict 목록으로 만든다."""
    props = next_data["props"]["pageProps"]
    record_map = props["recordMap"]

    collections = {}
    for collection_id, entry in record_map["collection"].items():
        value = entry.get("value", entry)
        name = plain_text(value.get("name")) or ""
        collections[collection_id] = {
            "name": name,
            "clean_name": LEADING_EMOJI.sub("", name).strip(),
            "schema": value.get("schema") or {},
        }

    rows = []
    for view_id, view in (props.get("queryCollectionResult") or {}).items():
        shown = set(
            view["result"]["reducerResults"]["collection_group_results"]["blockIds"]
        )
        for block in view["recordMap"]["block"].values():
            value = block.get("value", block)
            collection_id = value.get("parent_id")
            # 컬렉션 행이 아닌 일반 페이지 블록(사이트 루트 등)이 섞여 있다.
            if value.get("type") != "page" or collection_id not in collections:
                continue
            collection = collections[collection_id]
            fields = {
                collection["schema"].get(key, {}).get("name", key): plain_text(raw)
                for key, raw in (value.get("properties") or {}).items()
            }
            rows.append(
                {
                    "block_id": value["id"],
                    "collection_id": collection_id,
                    "collection_name": collection["name"],
                    "occupation": collection["clean_name"],
                    "view_id": view_id,
                    "listed_in_view": value["id"] in shown,
                    "fields": fields,
                }
            )
    return rows


def is_open(record, today=None):
    """접수 마감일이 지나지 않았으면 열려 있는 공고로 본다."""
    today = today or date.today()
    deadline = (record["fields"] or {}).get(DEADLINE_FIELD)
    if not deadline:
        # 마감일 미기재는 상시 모집으로 보고 열린 것으로 둔다.
        return True
    try:
        return date.fromisoformat(deadline.split(",")[0]) >= today
    except ValueError:
        return True


def to_processed(record):
    fields = record["fields"] or {}
    title = fields.get("이름")
    occupation = record["occupation"]
    skills = [fields.get(name) for name in JOB_FIELDS]
    skills = [s for s in skills if s]
    job = next(
        (s for s in skills if classify_from_structured(occupation, s)),
        skills[0] if skills else None,
    )
    return build_posting(
        COMPANY_ID,
        opening_id=record["block_id"],
        title=title,
        deploy=is_open(record) and record["listed_in_view"],
        occupation=occupation,
        job=job,
        classification=classify_job(title, occupation, job),
        due_date=fields.get(DEADLINE_FIELD),
        url=f"https://team.tving.com/{record['block_id'].replace('-', '')}",
        all_skills=skills,
        career=fields.get("경력"),
        employment_type=fields.get("고용형태"),
    )


def crawl():
    soup = BeautifulSoup(fetch(JOBS_URL), "html.parser")
    next_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
    rows = parse_rows(next_data)
    return save(
        COMPANY_ID,
        COMPANY_NAME,
        source="custom",
        source_url=JOBS_URL,
        raw_records=rows,
        processed_records=[to_processed(r) for r in rows],
        extracted_from="__NEXT_DATA__ pageProps.recordMap / queryCollectionResult (Notion)",
    )


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
