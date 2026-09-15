#!/usr/bin/env python3
"""확정 Area area_name 토큰과 채용공고 텍스트 겹침으로 공고를 Area에 붙인다.

- Area를 새로 만들거나 이름·keywords를 바꾸지 않는다.
- area_name을 ·/공백 등으로 쪼갠 토큰(2자+, 불용어 제외) ↔ 공고 title·occupation·job·skills.
- 매칭·카운트는 Python만 사용한다.
- 공고 raw/processed는 data/work에만 둔다.
- 산출은 data/research/area_postings_match/{json,md}/.
  Area 원본은 tech_blog_engineering_focus_29 (실험 시작 당시 29개사. 지금은 33곳).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENT_ROOT.parents[2]

sys.path.insert(0, str(REPO_ROOT / "pipeline" / "experiments" / "job_postings_crawler"))
sys.path.insert(0, str(REPO_ROOT / "pipeline" / "experiments" / "job_postings_crawler" / "scripts"))

from build_keyword_audit import occupation_bleed_rows  # noqa: E402
from common.paths import PROCESSED_DIR  # noqa: E402

CONFIG_DIR = EXPERIMENT_ROOT / "config"
COMPANY_IDS_FILE = CONFIG_DIR / "company_job_posting_ids.json"
RESEARCH_DIR = REPO_ROOT / "data" / "research"
SELECTED_COMPANIES_FILE = RESEARCH_DIR / "tech_blog_company_role_census" / "selected_companies.json"
AREA_RESEARCH_DIR = RESEARCH_DIR / "tech_blog_engineering_focus_29"
OUTPUT_ROOT = RESEARCH_DIR / "area_postings_match"

AREA_CATALOG_PATHS = [
    AREA_RESEARCH_DIR / "group1_areas.json",
    AREA_RESEARCH_DIR / "group2_areas.json",
    AREA_RESEARCH_DIR / "group3_areas.json",
    AREA_RESEARCH_DIR / "group4_areas.json",
    AREA_RESEARCH_DIR / "track_b_pilot_areas.json",
    RESEARCH_DIR / "tech_blog_areas" / "final_areas_with_roles.json",
]
WORK_AREA_DIRS = [
    REPO_ROOT / "data/work/tech_blog_engineering_focus_29/areas_per_company_group24",
    REPO_ROOT / "data/work/tech_blog_engineering_focus_29/areas_per_company_group1",
]

SKIP_COMPANIES = {"구름"}
KAKAO_HQ_GROUP = "카카오"
SKILL_FIELDS = (
    "skill_sets",
    "all_skills",
    "all_job_fields",
    "job_groups",
)

_ASCII_KEYWORD = re.compile(r"^[A-Za-z][A-Za-z\s\-/().]*$")

NAME_STOP = frozenset(
    {
        "및",
        "와",
        "과",
        "의",
        "을",
        "를",
        "이",
        "가",
        "에",
        "로",
        "에서",
        "으로",
        "하기",
        "위한",
        "통한",
        "기반",
        "중심",
        "운영",
        "개발",
        "설계",
        "구축",
        "시스템",
        "문제",
        "다룬다",
    }
)

MATCH_RULE = "area_name_tokens"


def output_dirs(root: Path) -> tuple[Path, Path]:
    return root / "json", root / "md"


def load_company_ids() -> dict[str, str]:
    data = json.loads(COMPANY_IDS_FILE.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_area_company(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_selected_companies() -> list[str]:
    data = json.loads(SELECTED_COMPANIES_FILE.read_text(encoding="utf-8"))
    return [c["name"] for c in data["companies"] if c["name"] not in SKIP_COMPANIES]


def _companies_from_area_file(path: Path) -> list[dict]:
    data = load_area_company(path)
    if isinstance(data, dict) and "areas" in data:
        return [data]
    if isinstance(data, list):
        return data
    return []


def find_area_company(company: str) -> tuple[dict, str]:
    for path in AREA_CATALOG_PATHS:
        if not path.exists():
            continue
        for doc in _companies_from_area_file(path):
            if doc.get("company") == company:
                return doc, str(path.relative_to(REPO_ROOT))

    for area_dir in WORK_AREA_DIRS:
        if not area_dir.exists():
            continue
        for path in area_dir.glob("*.json"):
            doc = load_area_company(path)
            if doc.get("company") == company:
                return doc, str(path.relative_to(REPO_ROOT))

    raise FileNotFoundError(f"Area JSON 없음: {company}")


def blog_count(area: dict) -> int:
    ids = {ev["article_id"] for ev in area.get("evidence") or [] if ev.get("article_id")}
    return len(ids)


def name_tokens(area_name: str) -> list[str]:
    parts = re.split(r"[\s·/\-–—(),]+", area_name or "")
    tokens: list[str] = []
    for part in parts:
        part = part.strip()
        if len(part) < 2 or part in NAME_STOP:
            continue
        if part not in tokens:
            tokens.append(part)
    return tokens


def _matches(keyword: str, text: str) -> bool:
    if not keyword or not text:
        return False
    if _ASCII_KEYWORD.match(keyword):
        return re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) is not None
    return keyword.lower() in text.lower()


def posting_text(posting: dict) -> str:
    parts: list[str] = []
    if posting.get("title"):
        parts.append(posting["title"])
    parts.extend(v for v in (posting.get("occupations") or []) if v)
    parts.extend(v for v in (posting.get("jobs") or []) if v)
    for field in SKILL_FIELDS:
        value = posting.get(field)
        if isinstance(value, str) and value:
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(v for v in value if v)
    return " ".join(parts)


def kakao_hq_only(postings: list[dict], company_id: str) -> list[dict]:
    if company_id != "kakao":
        return postings
    return [p for p in postings if p.get("group") == KAKAO_HQ_GROUP]


def unrelated_bleed_ids(postings: list[dict]) -> set:
    drop: set = set()
    for posting, occupation, _kws, _job, verdict in occupation_bleed_rows(postings):
        if verdict == "무관":
            drop.add(posting["opening_id"])
    return drop


def filter_postings(doc: dict | None, company_id: str) -> tuple[list[dict], dict]:
    if not doc:
        return [], {"source": None, "fetched_at": None}
    raw_active = [p for p in doc.get("postings") or [] if p.get("deploy")]
    active = kakao_hq_only(raw_active, company_id)
    drop = unrelated_bleed_ids(active)
    filtered = [p for p in active if p["opening_id"] not in drop]
    meta = {
        "source": doc.get("source"),
        "fetched_at": doc.get("fetched_at"),
        "raw_active": len(raw_active),
        "active_after_step6": len(filtered),
        "kakao_excluded": len(raw_active) - len(active) if company_id == "kakao" else 0,
        "bleed_dropped": len(drop),
    }
    return filtered, meta


def match_company(area_doc: dict, postings: list[dict]) -> dict:
    area_rows = []
    matched_ids: set = set()
    per_area_matches: dict[str, set] = defaultdict(set)
    per_area_tokens: dict[str, set] = defaultdict(set)

    for area in area_doc.get("areas") or []:
        area_id = area.get("id") or area.get("area_name")
        tokens = name_tokens(area.get("area_name") or "")
        for posting in postings:
            text = posting_text(posting)
            hit_tokens = [tok for tok in tokens if _matches(tok, text)]
            if not hit_tokens:
                continue
            opening_id = posting["opening_id"]
            matched_ids.add(opening_id)
            per_area_matches[area_id].add(opening_id)
            per_area_tokens[area_id].update(hit_tokens)

    for area in area_doc.get("areas") or []:
        area_id = area.get("id") or area.get("area_name")
        opening_ids_set = per_area_matches.get(area_id, set())
        area_rows.append(
            {
                "area_id": area.get("id"),
                "area_name": area["area_name"],
                "blog_count": blog_count(area),
                "posting_count": len(opening_ids_set),
                "matched_name_tokens": sorted(per_area_tokens.get(area_id, set())),
                "matched_opening_ids": sorted(opening_ids_set, key=str),
            }
        )

    unmatched = len(postings) - len(matched_ids)
    return {
        "areas": area_rows,
        "active_postings": len(postings),
        "matched_postings": len(matched_ids),
        "unmatched_postings": unmatched,
    }


def to_markdown(result: dict) -> str:
    lines = [
        f"# {result['company']} — Area × 공고 매칭",
        "",
        f"활성 공고 {result['active_postings']}건 · "
        f"매칭 {result['matched_postings']}건 · "
        f"미매칭 {result['unmatched_postings']}건",
        "",
        "| Area | 블로그 | 공고 |",
        "|---|---:|---:|",
    ]
    for area in result["areas"]:
        lines.append(
            f"| {area['area_name']} | {area['blog_count']} | {area['posting_count']} |"
        )
    lines.extend(["", "## Area별", ""])
    for area in result["areas"]:
        lines.append(
            f"- {area['area_name']} — 블로그 {area['blog_count']} · 공고 {area['posting_count']}"
        )
        if area["matched_name_tokens"]:
            lines.append(f"  - 걸린 name 토큰: {', '.join(area['matched_name_tokens'])}")
    if result["unmatched_postings"]:
        lines.extend(
            [
                "",
                "## 미매칭",
                "",
                f"Area name 토큰과 겹치지 않아 버린 공고 {result['unmatched_postings']}건.",
            ]
        )
    return "\n".join(lines) + "\n"


def to_index_markdown(index: dict) -> str:
    totals = index["totals"]
    lines = [
        "# Area × 공고 매칭",
        "",
        f"회사 {index['company_count']}곳 · "
        f"활성 {totals['active_postings']}건 · "
        f"매칭 {totals['matched_postings']}건 · "
        f"미매칭 {totals['unmatched_postings']}건",
        "",
        "구름은 F-01에서 빠져 이 목록에 없다.",
        "",
        "| 회사 | 활성 | 매칭 | 미매칭 |",
        "|---|---:|---:|---:|",
    ]
    for row in index["companies"]:
        lines.append(
            f"| {row['company']} | {row['active_postings']} | "
            f"{row['matched_postings']} | {row['unmatched_postings']} |"
        )
    if index["skipped"]:
        lines.extend(["", "## 건너뜀", ""])
        for row in index["skipped"]:
            lines.append(f"- {row['company']}: {row['reason']}")
    return "\n".join(lines) + "\n"


def process_company(
    company: str,
    *,
    company_ids: dict[str, str],
    processed_dir: Path,
    json_dir: Path,
    md_dir: Path,
) -> dict:
    if company in SKIP_COMPANIES:
        raise ValueError(f"제외 회사: {company}")

    area_doc, area_source = find_area_company(company)

    company_id = company_ids.get(company)
    if not company_id:
        raise KeyError(f"company_job_posting_ids.json에 없음: {company}")

    processed_path = processed_dir / f"{company_id}.json"
    processed_doc = (
        json.loads(processed_path.read_text(encoding="utf-8"))
        if processed_path.exists()
        else None
    )
    postings, posting_meta = filter_postings(processed_doc, company_id)
    match = match_company(area_doc, postings)

    result = {
        "company": company,
        "company_id": company_id,
        "match_rule": MATCH_RULE,
        "area_source": area_source,
        "posting_source": (
            str(processed_path.relative_to(REPO_ROOT)) if processed_path.exists() else None
        ),
        "posting_meta": posting_meta,
        **match,
    }

    json_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / f"{company_id}.json"
    md_path = md_dir / f"{company_id}.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(result), encoding="utf-8")
    result["_output_json"] = str(json_path.relative_to(REPO_ROOT))
    result["_output_md"] = str(md_path.relative_to(REPO_ROOT))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Area name 토큰 ↔ 채용공고 매칭")
    parser.add_argument(
        "--company",
        action="append",
        help="처리할 회사 표시명 (여러 번 지정 가능). 미지정 시 selected_companies 전체(구름 제외).",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=PROCESSED_DIR,
        help="processed 공고 디렉터리 (data/work)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_ROOT,
        help="산출 루트. 회사 JSON은 json/, MD는 md/ (data/research/area_postings_match)",
    )
    args = parser.parse_args()

    company_ids = load_company_ids()
    companies = args.company or load_selected_companies()
    json_dir, md_dir = output_dirs(args.output_dir)

    rows = []
    skipped: list[dict] = []
    for company in companies:
        try:
            result = process_company(
                company,
                company_ids=company_ids,
                processed_dir=args.processed_dir,
                json_dir=json_dir,
                md_dir=md_dir,
            )
        except FileNotFoundError as exc:
            skipped.append({"company": company, "reason": str(exc)})
            print(f"{company}: SKIP — {exc}")
            continue
        except KeyError as exc:
            skipped.append({"company": company, "reason": str(exc)})
            print(f"{company}: SKIP — {exc}")
            continue
        rows.append(result)
        print(
            f"{company}: 활성 {result['active_postings']} · "
            f"매칭 {result['matched_postings']} · "
            f"미매칭 {result['unmatched_postings']} → {result['_output_md']}"
        )

    index = {
        "match_rule": MATCH_RULE,
        "selected_companies_source": str(SELECTED_COMPANIES_FILE.relative_to(REPO_ROOT)),
        "excluded_companies": sorted(SKIP_COMPANIES),
        "processed_dir": str(args.processed_dir.relative_to(REPO_ROOT)),
        "company_count": len(rows),
        "skipped_count": len(skipped),
        "totals": {
            "active_postings": sum(r["active_postings"] for r in rows),
            "matched_postings": sum(r["matched_postings"] for r in rows),
            "unmatched_postings": sum(r["unmatched_postings"] for r in rows),
        },
        "skipped": skipped,
        "companies": [
            {
                "company": r["company"],
                "company_id": r["company_id"],
                "active_postings": r["active_postings"],
                "matched_postings": r["matched_postings"],
                "unmatched_postings": r["unmatched_postings"],
                "output_json": r["_output_json"],
                "output_md": r["_output_md"],
            }
            for r in rows
        ],
    }
    json_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)
    index_json_path = json_dir / "index.json"
    index_md_path = md_dir / "index.md"
    index_json_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    index_md_path.write_text(to_index_markdown(index), encoding="utf-8")
    print(f"\nindex → {index_json_path.relative_to(REPO_ROOT)}")
    print(f"index → {index_md_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
