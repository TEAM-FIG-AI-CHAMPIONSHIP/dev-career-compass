#!/usr/bin/env python3
"""Area evidence 고유 article_id × roles로 회사×직무를 센다. 직무당 4건 이상만 연다."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

THRESHOLD = 4
ROLE_ORDER = [
    ("backend", "서버·백엔드"),
    ("frontend", "웹 프론트엔드"),
    ("mobile", "모바일"),
    ("data-ai", "데이터·AI"),
]
SKIP_COMPANIES = {"구름"}


def load_companies(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "areas" in data:
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"회사 객체 또는 회사 배열 JSON이어야 함: {path}")


def jobs_for_company(company_obj: dict) -> dict:
    by_id: dict[str, set[str]] = {}
    for area in company_obj.get("areas") or []:
        for ev in area.get("evidence") or []:
            aid = ev.get("article_id")
            if not aid:
                continue
            by_id.setdefault(aid, set()).update(ev.get("roles") or [])

    counts: dict[str, int] = defaultdict(int)
    for roles in by_id.values():
        for rid in roles:
            counts[rid] += 1

    jobs, below = [], []
    for rid, name in ROLE_ORDER:
        n = counts.get(rid, 0)
        row = {"id": rid, "name": name, "evidence_count": n}
        if n >= THRESHOLD:
            jobs.append(row)
        elif n > 0:
            below.append(row)

    return {
        "company": company_obj["company"],
        "source_file": company_obj.get("source_file"),
        "area_count": len(company_obj.get("areas") or []),
        "evidence_article_count": len(by_id),
        "unassigned_count": company_obj.get("unassigned_count"),
        "jobs": jobs,
        "job_count": len(jobs),
        "below_threshold": below,
    }


def to_markdown(rows: list[dict]) -> str:
    lines = [
        "| 회사 | evidence 글 | 열리는 직무 수 | 열리는 직무 (건수) | 4건 미만이라 안 연 직무 |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        jobs = ", ".join(f"{j['name']} {j['evidence_count']}" for j in row["jobs"]) or "-"
        below = ", ".join(
            f"{j['name']} {j['evidence_count']}" for j in row["below_threshold"]
        ) or "-"
        lines.append(
            f"| {row['company']} | {row['evidence_article_count']} | "
            f"{row['job_count']} | {jobs} | {below} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Area evidence 기준 회사×직무 (직무당 4건)"
    )
    parser.add_argument("area_json", type=Path, help="회사 Area JSON (단건 또는 배열)")
    parser.add_argument("-o", "--output", type=Path, help="JSON 저장 경로")
    args = parser.parse_args()

    rows = [
        jobs_for_company(company)
        for company in load_companies(args.area_json)
        if company.get("company") not in SKIP_COMPANIES
    ]
    payload = {
        "source": str(args.area_json),
        "threshold": THRESHOLD,
        "company_count": len(rows),
        "pair_count": sum(r["job_count"] for r in rows),
        "companies": rows,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    print(to_markdown(rows), end="")


if __name__ == "__main__":
    main()
