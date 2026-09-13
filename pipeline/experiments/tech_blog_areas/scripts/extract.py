import argparse
import hashlib
import json
import time

from datetime import datetime, timezone
from pathlib import Path

import requests
import trafilatura


PROJECT_ROOT = Path(__file__).resolve().parents[4]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "collected"
    / "articles.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "extracted"
)

ARTICLES_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "extract_report.json"
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

TIMEOUT = 20

MIN_CONTENT_LENGTH = 300


def load_json(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_json(
    file_path,
    data
):
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def create_content_hash(content):
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def fetch_html(
    session,
    url
):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT
        )

    except requests.RequestException as e:
        return None, str(e)

    if not response.ok:
        return (
            None,
            f"HTTP {response.status_code}"
        )

    content_type = (
        response.headers
        .get(
            "content-type",
            ""
        )
        .lower()
    )

    if "text/html" not in content_type:
        return (
            None,
            f"not html: {content_type}"
        )

    return response.text, None


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

    if not content:
        return None

    return content


def extract_article(
    session,
    article
):
    url = article[
        "url"
    ]

    html, error = fetch_html(
        session,
        url
    )

    if error:
        return None, {
            "article_id": (
                article["article_id"]
            ),
            "url": url,
            "reason": error
        }

    content = extract_content(
        html
    )

    if not content:
        return None, {
            "article_id": (
                article["article_id"]
            ),
            "url": url,
            "reason": (
                "content extraction failed"
            )
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

    result = {
        **article,
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
    }

    return result, None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--delay",
        type=float,
        default=0.2
    )

    args = parser.parse_args()

    articles = load_json(
        INPUT_FILE
    )

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    extracted = []
    failures = []

    print()
    print("=" * 60)
    print("EXTRACT 시작")
    print("=" * 60)

    for index, article in enumerate(
        articles,
        start=1
    ):
        print(
            f"[{index}/{len(articles)}]",
            article["title"]
        )

        result, failure = (
            extract_article(
                session,
                article
            )
        )

        if result:
            extracted.append(
                result
            )

            print(
                "  →",
                result[
                    "content_length"
                ],
                "chars",
                f"({result['extraction_quality']})"
            )

        if failure:
            failures.append(
                failure
            )

            print(
                "  → 실패:",
                failure["reason"]
            )

        if args.delay > 0:
            time.sleep(
                args.delay
            )

    extracted.sort(
        key=lambda article: (
            article[
                "published_at"
            ]
        ),
        reverse=True
    )

    lengths = [
        article[
            "content_length"
        ]
        for article in extracted
    ]

    short_count = sum(
        1
        for article in extracted
        if (
            article[
                "extraction_quality"
            ]
            == "short"
        )
    )

    report = {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "input_count": (
            len(articles)
        ),
        "success_count": (
            len(extracted)
        ),
        "failure_count": (
            len(failures)
        ),
        "short_count": (
            short_count
        ),
        "min_content_length": (
            min(lengths)
            if lengths
            else 0
        ),
        "max_content_length": (
            max(lengths)
            if lengths
            else 0
        ),
        "average_content_length": (
            round(
                sum(lengths)
                / len(lengths),
                2
            )
            if lengths
            else 0
        ),
        "failures": failures
    }

    save_json(
        ARTICLES_FILE,
        extracted
    )

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("EXTRACT 완료")
    print("=" * 60)

    print(
        "입력:",
        len(articles)
    )

    print(
        "성공:",
        len(extracted)
    )

    print(
        "실패:",
        len(failures)
    )

    print(
        "짧은 본문:",
        short_count
    )

    if lengths:
        print(
            "본문 길이:",
            f"min={min(lengths)}",
            f"avg={round(sum(lengths) / len(lengths), 2)}",
            f"max={max(lengths)}"
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
    