"""check_coverage.py가 "날짜 의심"으로 표시한 글만, 실제 URL에서
날짜를 다시 확인한다.

census의 다른 스크립트(collect.py 등)는 건드리지 않는다. 결과는
별도 파일(date_repairs.json)에만 쓰고, extracted/classified 원본은
그대로 둔다 — 이 결과를 반영할지는 사람이 검토 후 판단한다.

날짜 재확인 순서 (회사별 분기 없이 전부 동일):
  JSON-LD article.datePublished
  -> og:article:published_time 메타 태그
  -> <time datetime="..."> 태그
  -> 그래도 없으면 null (원래 sitemap lastmod로 되돌리지 않는다)
"""

import argparse
import json
import re
import sys
import time

from pathlib import Path

import requests

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent)
)

from paths import WORK  # noqa: E402


COVERAGE_REPORT_FILE = (
    WORK
    / "coverage_report.json"
)

OUTPUT_FILE = (
    WORK
    / "date_repairs.json"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 15
DELAY = 0.1


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


def parse_date_safe(value):
    if not value:
        return None

    try:
        return date_parser.parse(
            value
        ).date().isoformat()

    except (
        ValueError,
        TypeError,
        OverflowError
    ):
        return None


def find_json_ld_date(soup):
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        text = script.string

        if not text:
            continue

        try:
            data = json.loads(
                text
            )

        except json.JSONDecodeError:
            continue

        candidates = (
            data
            if isinstance(data, list)
            else [data]
        )

        for item in candidates:
            date = extract_date_published(
                item
            )

            if date:
                return date

    return None


def extract_date_published(value):
    if isinstance(value, list):
        for item in value:
            result = (
                extract_date_published(
                    item
                )
            )

            if result:
                return result

        return None

    if not isinstance(value, dict):
        return None

    date_published = value.get(
        "datePublished"
    )

    if isinstance(
        date_published,
        str
    ):
        parsed = parse_date_safe(
            date_published
        )

        if parsed:
            return parsed

    for child in value.values():
        result = (
            extract_date_published(
                child
            )
        )

        if result:
            return result

    return None


def find_meta_published_time(
    soup
):
    meta = soup.find(
        "meta",
        attrs={
            "property": (
                "article:published_time"
            )
        }
    )

    if meta and meta.get("content"):
        return parse_date_safe(
            meta["content"]
        )

    return None


def find_time_tag(soup):
    time_tag = soup.find(
        "time",
        attrs={"datetime": True}
    )

    if time_tag:
        return parse_date_safe(
            time_tag["datetime"]
        )

    return None


def resolve_real_date(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    date = find_json_ld_date(
        soup
    )

    if date:
        return date, "json_ld"

    date = find_meta_published_time(
        soup
    )

    if date:
        return date, "og_published_time"

    date = find_time_tag(
        soup
    )

    if date:
        return date, "time_tag"

    return None, None


def fetch_html(session, url):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        return None, str(error)

    if not response.ok:
        return (
            None,
            f"HTTP {response.status_code}"
        )

    content_type = response.headers.get(
        "content-type",
        ""
    ).lower()

    if "charset" not in content_type:
        response.encoding = (
            response.apparent_encoding
        )

    return response.text, None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--companies",
        type=str,
        default="",
        help=(
            "쉼표로 구분된 회사명. 비우면 "
            "coverage_report.json에서 날짜 "
            "의심으로 표시된 회사 전체를 처리."
        )
    )

    args = parser.parse_args()

    company_allowlist = None

    if args.companies.strip():
        company_allowlist = {
            name.strip()
            for name in (
                args.companies.split(",")
            )
            if name.strip()
        }

    coverage = load_json(
        COVERAGE_REPORT_FILE
    )

    targets = []

    for row in coverage["companies"]:
        if (
            company_allowlist
            and row["company"]
            not in company_allowlist
        ):
            continue

        if not row.get(
            "suspicious_article_ids"
        ):
            continue

        targets.append(row)

    total_ids = sum(
        len(
            row[
                "suspicious_article_ids"
            ]
        )
        for row in targets
    )

    print()
    print("=" * 60)
    print("DATE REPAIR")
    print("=" * 60)

    print(
        "대상 회사:",
        len(targets)
    )

    print(
        "대상 글:",
        total_ids
    )

    if not targets:
        print(
            "재확인할 글이 없습니다 "
            "(check_coverage.py를 먼저 "
            "돌렸는지 확인하세요)."
        )

        return

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    from paths import (  # noqa: E402
        EXTRACTED_FILE
    )

    all_articles = {
        a["article_id"]: a
        for a in load_json(
            EXTRACTED_FILE
        )
    }

    results = {}
    source_counts = {}
    failed = 0
    processed = 0

    for row in targets:
        for article_id in row[
            "suspicious_article_ids"
        ]:
            article = all_articles.get(
                article_id
            )

            if not article:
                continue

            processed += 1

            html, error = fetch_html(
                session,
                article["url"]
            )

            if error:
                failed += 1

                results[article_id] = {
                    "company": row[
                        "company"
                    ],
                    "old_date": article.get(
                        "published_at",
                        ""
                    )[:10],
                    "new_date": None,
                    "source": None,
                    "error": error
                }

                continue

            new_date, source = (
                resolve_real_date(
                    html
                )
            )

            results[article_id] = {
                "company": row[
                    "company"
                ],
                "old_date": article.get(
                    "published_at",
                    ""
                )[:10],
                "new_date": new_date,
                "source": source,
                "error": None
            }

            if source:
                source_counts[
                    source
                ] = (
                    source_counts.get(
                        source,
                        0
                    )
                    + 1
                )

            print(
                f"[{processed}/{total_ids}]",
                f"[{row['company']}]",
                article["url"],
                "->",
                new_date or "미상"
            )

            if processed % 20 == 0:
                save_json(
                    OUTPUT_FILE,
                    results
                )

            if DELAY > 0:
                time.sleep(
                    DELAY
                )

    save_json(
        OUTPUT_FILE,
        results
    )

    unresolved = sum(
        1
        for r in results.values()
        if not r["new_date"]
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    print(
        "재확인 시도:",
        processed
    )

    print(
        "실패(요청 오류):",
        failed
    )

    print(
        "날짜 못 찾음(미상):",
        unresolved
    )

    print(
        "출처 분포:",
        source_counts
    )

    print(
        "저장:",
        OUTPUT_FILE
    )

    print()
    print(
        "이 결과는 date_repairs.json에만 "
        "저장됩니다. classified/extracted "
        "원본에 반영할지는 검토 후 "
        "직접 병합하세요."
    )


if __name__ == "__main__":
    main()
