"""회사별로 12개월 커버리지와 날짜 신뢰도를 점검한다.

- gap_days: (오늘-12개월) 대비 가장 오래된 published_at이 얼마나
  부족한지. 회사별 예외 없이 전부 동일 계산.
- suspicious_dates: 같은 회사 안에서 동일 날짜가 SUSPICIOUS_MIN_REPEAT
  건 이상 반복되면 그 lastmod를 못 믿는 것으로 본다 (sitemap이 개별
  게시일 대신 "생성 시각"을 넣는 사이트가 있었음 — 삼성반도체에서
  383건이 전부 같은 날짜였던 사례).

이 스크립트는 census 데이터를 읽기 전용으로 쓰고, 결과는 별도 리포트
파일에만 쓴다. classified/extracted 원본은 건드리지 않는다.
"""

import json
import sys

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dateutil.relativedelta import relativedelta

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent)
)

from paths import (  # noqa: E402
    EXTRACTED_FILE,
    WORK
)


REPORT_FILE = (
    WORK
    / "coverage_report.json"
)

MONTHS = 12

SUSPICIOUS_MIN_REPEAT = 5

NORMAL_MAX_GAP_DAYS = 30

PARTIAL_MAX_GAP_DAYS = 180


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


def classify_gap(gap_days):
    if gap_days <= NORMAL_MAX_GAP_DAYS:
        return "정상"

    if gap_days <= PARTIAL_MAX_GAP_DAYS:
        return "부분"

    return "심각부분"


def main():
    articles = load_json(
        EXTRACTED_FILE
    )

    now = datetime.now(
        timezone.utc
    )

    cutoff_date = (
        now
        - relativedelta(
            months=MONTHS
        )
    ).date()

    by_company = defaultdict(
        list
    )

    for article in articles:
        published_at = article.get(
            "published_at"
        )

        if not published_at:
            continue

        by_company[
            article["company"]
        ].append(
            {
                "article_id": (
                    article[
                        "article_id"
                    ]
                ),
                "url": article["url"],
                "date": published_at[
                    :10
                ]
            }
        )

    report_rows = []

    for company, rows in sorted(
        by_company.items()
    ):
        dates = [
            r["date"]
            for r in rows
        ]

        oldest = min(dates)

        gap_days = (
            datetime.fromisoformat(
                oldest
            ).date()
            - cutoff_date
        ).days

        date_counts = defaultdict(
            int
        )

        for d in dates:
            date_counts[d] += 1

        suspicious = [
            {
                "date": d,
                "count": c
            }
            for d, c in (
                date_counts.items()
            )
            if c
            >= SUSPICIOUS_MIN_REPEAT
        ]

        suspicious.sort(
            key=lambda x: (
                -x["count"]
            )
        )

        suspicious_article_ids = [
            r["article_id"]
            for r in rows
            if r["date"]
            in {
                s["date"]
                for s in suspicious
            }
        ]

        row = {
            "company": company,
            "article_count": len(
                rows
            ),
            "oldest_published_at": (
                oldest
            ),
            "gap_days": gap_days,
            "status": classify_gap(
                gap_days
            ),
            "suspicious_dates": (
                suspicious
            ),
            "suspicious_article_count": len(
                suspicious_article_ids
            ),
            "suspicious_article_ids": (
                suspicious_article_ids
            )
        }

        report_rows.append(
            row
        )

    save_json(
        REPORT_FILE,
        {
            "generated_at": (
                now.isoformat()
            ),
            "cutoff_date": (
                cutoff_date.isoformat()
            ),
            "companies": report_rows
        }
    )

    print()
    print("=" * 60)
    print("COVERAGE CHECK")
    print("=" * 60)

    print(
        "cutoff:",
        cutoff_date
    )

    print()

    for row in sorted(
        report_rows,
        key=lambda r: r[
            "gap_days"
        ]
    ):
        flag = (
            " ⚠ 날짜 의심"
            if row[
                "suspicious_article_count"
            ]
            > 0
            else ""
        )

        print(
            f"{row['gap_days']:4d}일 부족  "
            f"[{row['status']}]  "
            f"{row['company']:30s}  "
            f"최고령 {row['oldest_published_at']}"
            f"{flag}"
        )

        if row["suspicious_dates"]:
            for s in row[
                "suspicious_dates"
            ]:
                print(
                    f"      -> {s['date']}에 "
                    f"{s['count']}건 몰림 "
                    "(sitemap lastmod 재검증 필요, "
                    "repair_dates.py 사용)"
                )

    print()
    print(
        "저장:",
        REPORT_FILE
    )


if __name__ == "__main__":
    main()
