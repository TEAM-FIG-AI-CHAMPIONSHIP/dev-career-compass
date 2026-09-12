"""수집 결과 저장 공통 모듈.

raw  : 수집처에서 받은 레코드를 가공 없이 그대로 보존 (분류 기준이 바뀌면 여기서 다시 돌린다)
processed : 분류·정제 결과
"""

import json
from datetime import datetime, timezone

from common.paths import PROCESSED_DIR, RAW_DIR


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save(company_id, company_name, source, source_url, raw_records, processed_records,
         extracted_from=None, extra=None):
    """raw / processed 두 파일을 저장하고 요약 dict를 반환."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    meta = {
        "company_id": company_id,
        "company_name": company_name,
        "source": source,
        "source_url": source_url,
        "fetched_at": fetched_at,
    }
    if extracted_from:
        meta["extracted_from"] = extracted_from

    _write(RAW_DIR / f"{company_id}.json", {**meta, **(extra or {}), "openings": raw_records})
    _write(PROCESSED_DIR / f"{company_id}.json", {**meta, "postings": processed_records})

    active = [p for p in processed_records if p["deploy"]]
    return {
        "company_id": company_id,
        "company_name": company_name,
        "url": source_url,
        "raw_count": len(raw_records),
        "deploy_true": len(active),
        "deploy_false": len(processed_records) - len(active),
        "classified_active": len([p for p in active if p["category"]]),
        "disagreements": [p for p in active if p["disagreement"]],
        "no_structured": len([p for p in active if not p["structured"]]),
    }


def build_posting(company_id, *, opening_id, title, deploy, occupation=None, job=None,
                  classification, open_date=None, due_date=None, group=None, url=None, **extra):
    """processed 레코드 공통 스키마."""
    return {
        "company_id": company_id,
        "opening_id": opening_id,
        "title": title,
        "deploy": deploy,
        "occupations": [occupation] if occupation else [],
        "jobs": [job] if job else [],
        "category": classification["category"],
        "category_source": classification["source"],
        "categories": [classification["category"]] if classification["category"] else [],
        "structured": classification["structured"],
        "title_based": classification["title_based"],
        "disagreement": classification["disagreement"],
        "open_date": open_date,
        "due_date": due_date,
        "group": group,
        "url": url,
        **extra,
    }
