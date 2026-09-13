import json
import sys

from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

from extract_engineering_focus import (  # noqa: E402
    CENSUS_CLASSIFIED_FILE,
    build_exclusion_reason
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

RESEARCH_DIR = (
    PROJECT_ROOT
    / "data"
    / "research"
    / "tech_blog_engineering_focus_29"
)

SUMMARY_JSON = (
    RESEARCH_DIR
    / "track_a_company_role_counts.json"
)

SUMMARY_MD = (
    RESEARCH_DIR
    / "track_a_company_role_counts.md"
)

ROLE_LABELS = {
    "backend": "서버·백엔드",
    "frontend": "웹 프론트엔드",
    "mobile": "모바일",
    "data-ai": "데이터·AI"
}


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():
    classified = load_json(
        CENSUS_CLASSIFIED_FILE
    )

    tech_articles = [
        item
        for item in classified
        if item.get("is_tech")
    ]

    kept = []
    excluded_count = 0

    for article in tech_articles:
        if build_exclusion_reason(
            article
        ):
            excluded_count += 1
            continue

        kept.append(
            article
        )

    company_role_counts = {}
    company_total = {}

    for article in kept:
        company = article["company"]

        company_total[
            company
        ] = (
            company_total.get(
                company,
                0
            )
            + 1
        )

        roles = article.get(
            "roles",
            []
        )

        for role in roles:
            key = (
                company,
                role
            )

            company_role_counts[
                key
            ] = (
                company_role_counts.get(
                    key,
                    0
                )
                + 1
            )

    companies = sorted(
        company_total.keys()
    )

    rows = []

    for company in companies:
        role_counts = {
            role: company_role_counts.get(
                (company, role),
                0
            )
            for role in ROLE_LABELS
        }

        rows.append(
            {
                "company": company,
                "tech_count_after_filter": (
                    company_total[
                        company
                    ]
                ),
                "role_counts": (
                    role_counts
                )
            }
        )

    save_json(
        SUMMARY_JSON,
        {
            "note": (
                "Track A: 가벼운 필터(카카오클라우드 "
                "글로서리 시리즈, 업스테이지 카테고리 "
                "목록 페이지, LG AI연구원 한/영 중복) "
                "적용 후 회사×직무 기술글 수 집계. "
                "census(#30, #40)의 1차 게이트 판정을 "
                "대체하지 않음 — engineering_focus/Area "
                "작업 전 참고용 재집계."
            ),
            "excluded_by_filter": (
                excluded_count
            ),
            "company_count": len(
                companies
            ),
            "companies": rows
        }
    )

    lines = [
        "# Track A: 필터 적용 후 회사×직무 기술글 집계",
        "",
        (
            "가벼운 필터(카카오클라우드 글로서리, "
            "업스테이지 카테고리 페이지, LG AI연구원 "
            "한/영 중복) 적용 후 재집계한 결과다. "
            "census(#30, #40)의 공식 1차 게이트 판정을 "
            "대체하지 않는다."
        ),
        "",
        f"필터로 제외: {excluded_count}건",
        f"회사 수: {len(companies)}",
        "",
        (
            "| 회사 | 필터 후 기술글 | 백엔드 | "
            "프론트엔드 | 모바일 | 데이터·AI |"
        ),
        "|---|---:|---:|---:|---:|---:|"
    ]

    for row in sorted(
        rows,
        key=lambda r: (
            -r["tech_count_after_filter"]
        )
    ):
        role_counts = row["role_counts"]

        lines.append(
            f"| {row['company']} "
            f"| {row['tech_count_after_filter']} "
            f"| {role_counts['backend']} "
            f"| {role_counts['frontend']} "
            f"| {role_counts['mobile']} "
            f"| {role_counts['data-ai']} |"
        )

    SUMMARY_MD.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SUMMARY_MD,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(lines)
            + "\n"
        )

    print()
    print("=" * 60)
    print("TRACK A 요약")
    print("=" * 60)

    print(
        "필터 제외:",
        excluded_count
    )

    print(
        "회사 수:",
        len(companies)
    )

    for row in sorted(
        rows,
        key=lambda r: (
            -r["tech_count_after_filter"]
        )
    ):
        print(
            f"{row['tech_count_after_filter']:4d}",
            row["company"]
        )

    print()
    print("저장:", SUMMARY_JSON)
    print("저장:", SUMMARY_MD)


if __name__ == "__main__":
    main()
