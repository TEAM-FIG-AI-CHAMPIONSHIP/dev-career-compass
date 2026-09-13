import argparse
import hashlib
import json
import re
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag

import requests
import trafilatura

from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta


SCRIPTS_DIR = Path(
    __file__
).resolve().parent.parent

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

from archive_collector import (
    collect_archive
)


PROJECT_ROOT = Path(__file__).resolve().parents[5]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "toss"
)

ARTICLES_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "collect_report.json"
)


BLOG_URL = "https://toss.tech/"

COMPANY = "토스"

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
MIN_CONTENT_LENGTH = 300

# 토스 게시글 상세 페이지는 Next.js App Router RSC 스트리밍
# 페이로드(self.__next_f.push(...))에 게시일이 들어 있다.
# JSON-LD, og:*, <time> 태그 전부 없어서 이 필드가 유일한
# 날짜 신호다. 페이로드가 HTML 안에서는 JS 문자열 리터럴로
# 이스케이프되어 있어 따옴표가 \" 형태로 들어온다.
PUBLISHED_TIME_PATTERN = re.compile(
    r'publishedTime\\":\\"([^\\]+)'
)


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


def normalize_url(url):
    url, _ = urldefrag(
        url.strip()
    )

    return url


def parse_date(value):
    if not value:
        return None

    try:
        parsed = date_parser.parse(
            value
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except (
        ValueError,
        TypeError,
        OverflowError
    ):
        return None


def create_article_id(url):
    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:16]


def create_content_hash(content):
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def extract_title(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    if soup.title:
        return soup.title.get_text(
            " ",
            strip=True
        )

    return ""


def extract_published_time(html):
    match = PUBLISHED_TIME_PATTERN.search(
        html
    )

    if not match:
        return None

    return parse_date(
        match.group(1)
    )


def extract_content(html):
    content = trafilatura.extract(
        html,
        output_format="txt",
        include_comments=False,
        include_tables=True,
        deduplicate=True,
        favor_precision=True
    )

    if not content:
        return None

    content = content.strip()

    return content or None


def fetch_article_page(
    session,
    url
):
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

    return response.text, None


def resolve_article(
    session,
    url,
    cutoff
):
    html, error = fetch_article_page(
        session,
        url
    )

    if error:
        return None, {
            "url": url,
            "reason": error
        }

    published_at = (
        extract_published_time(
            html
        )
    )

    if not published_at:
        return None, {
            "url": url,
            "reason": (
                "publishedTime을 페이지에서 "
                "찾지 못함"
            )
        }

    if published_at < cutoff:
        return None, {
            "url": url,
            "reason": (
                "게시일이 cutoff보다 오래됨: "
                + published_at.isoformat()
            )
        }

    content = extract_content(
        html
    )

    if not content:
        return None, {
            "url": url,
            "reason": "본문 추출 실패"
        }

    content_length = len(
        content
    )

    quality = (
        "ok"
        if content_length
        >= MIN_CONTENT_LENGTH
        else "short"
    )

    return {
        "article_id": (
            create_article_id(url)
        ),
        "company": COMPANY,
        "title": extract_title(
            html
        ),
        "published_at": (
            published_at.isoformat()
        ),
        "url": url,
        "discovered_by": [
            "custom_adapter:toss"
        ],
        "content": content,
        "content_length": (
            content_length
        ),
        "content_hash": (
            create_content_hash(
                content
            )
        ),
        "extraction_quality": (
            quality
        )
    }, None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--months",
        type=int,
        default=12
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.15
    )

    args = parser.parse_args()

    now = datetime.now(
        timezone.utc
    )

    cutoff = (
        now
        - relativedelta(
            months=args.months
        )
    )

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    print()
    print("=" * 60)
    print("TOSS CUSTOM ADAPTER")
    print("=" * 60)

    source = {
        "blog_url": BLOG_URL
    }

    candidates, archive_report = (
        collect_archive(
            session=session,
            source=source,
            cutoff=cutoff,
            already_found_urls=set(),
            normalize_url=normalize_url,
            parse_date=parse_date,
            # 목록 페이지에 날짜 신호가 전혀 없어
            # cutoff 기반 조기 종료가 불가능하다
            # (page_is_past_cutoff가 항상 False).
            # 12개월 경계에 실제로 닿았는지 확인하기
            # 위해 기본 20페이지보다 넉넉하게 늘린다.
            max_pages=60
        )
    )

    print(
        "archive 링크 탐색 결과:",
        len(candidates)
    )

    print(
        "working_pattern:",
        archive_report[
            "working_pattern"
        ]
    )

    print(
        "stop_reason:",
        archive_report[
            "stop_reason"
        ]
    )

    urls = sorted(
        candidates.keys()
    )

    articles = []
    failed = []

    for index, url in enumerate(
        urls,
        start=1
    ):
        print(
            f"[{index}/{len(urls)}]",
            url
        )

        article, failure = (
            resolve_article(
                session,
                url,
                cutoff
            )
        )

        if failure:
            failed.append(
                failure
            )

        else:
            articles.append(
                article
            )

        if args.delay > 0:
            time.sleep(
                args.delay
            )

    articles.sort(
        key=lambda article: (
            article["published_at"]
        ),
        reverse=True
    )

    quality_counts = {}

    for article in articles:
        quality = article[
            "extraction_quality"
        ]

        quality_counts[
            quality
        ] = (
            quality_counts.get(
                quality,
                0
            )
            + 1
        )

    failure_reasons = {}

    for failure in failed:
        reason_key = failure[
            "reason"
        ].split(":")[0]

        failure_reasons[
            reason_key
        ] = (
            failure_reasons.get(
                reason_key,
                0
            )
            + 1
        )

    save_json(
        ARTICLES_FILE,
        articles
    )

    report = {
        "generated_at": (
            now.isoformat()
        ),
        "cutoff": cutoff.isoformat(),
        "months": args.months,
        "archive": archive_report,
        "candidate_count": len(
            urls
        ),
        "extracted_count": len(
            articles
        ),
        "failed_count": len(
            failed
        ),
        "quality_counts": (
            quality_counts
        ),
        "failure_reasons": (
            failure_reasons
        ),
        "failures": failed
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    print(
        "후보:",
        len(urls)
    )

    print(
        "12개월 이내 + 본문 추출 성공:",
        len(articles)
    )

    print(
        "실패:",
        len(failed)
    )

    print(
        "실패 사유 분포:",
        failure_reasons
    )

    print(
        "품질 분포:",
        quality_counts
    )

    print(
        "저장:",
        ARTICLES_FILE
    )

    print(
        "리포트:",
        REPORT_FILE
    )


if __name__ == "__main__":
    main()
