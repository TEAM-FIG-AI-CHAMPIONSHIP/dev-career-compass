import argparse
import hashlib
import json
import re
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

import requests

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


PROJECT_ROOT = Path(__file__).resolve().parents[5]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "naver_d2"
)

ARTICLES_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "collect_report.json"
)


BASE_URL = "https://d2.naver.com"

API_URL = (
    BASE_URL
    + "/api/v1/contents"
)

COMPANY = "네이버"

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
PAGE_SIZE = 30
MAX_PAGES = 500

MIN_CONTENT_LENGTH = 300

# D2 목록 API는 helloworld(개발 글)와 news(공지·행사성 글)를
# 같은 피드에 섞어서 반환한다. 여기서는 걸러내지 않고 전부
# 수집하고, 기술 관련성 판단은 기존 classify_relevance 단계에
# 맡긴다.


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


def create_article_id(url):
    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:16]


def create_content_hash(content):
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def normalize_text(text):
    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def parse_page_param(href):
    # 목록 API가 돌려주는 links의 href는
    # "http://localhost:8080/..."로 호스트가 내부용으로
    # 박혀 있어 그대로 따라가면 안 된다. page 쿼리값만
    # 뽑아서 실제 API_URL에 다시 붙인다.
    query = parse_qs(
        urlparse(href).query
    )

    values = query.get(
        "page"
    )

    if not values:
        return None

    try:
        return int(
            values[0]
        )

    except ValueError:
        return None


def fetch_content_page(
    session,
    page,
    size
):
    try:
        response = session.get(
            API_URL,
            params={
                "page": page,
                "size": size
            },
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        return None, str(error)

    if not response.ok:
        return (
            None,
            f"HTTP {response.status_code}"
        )

    try:
        return response.json(), None

    except ValueError as error:
        return None, str(error)


def epoch_ms_to_datetime(value):
    if value is None:
        return None

    return datetime.fromtimestamp(
        value / 1000,
        tz=timezone.utc
    )


def collect_candidates(
    session,
    cutoff,
    page_size,
    delay
):
    candidates = []
    pages_visited = 0
    stop_reason = None
    last_page_index = None

    page = 0

    while page <= MAX_PAGES:
        payload, error = (
            fetch_content_page(
                session,
                page,
                page_size
            )
        )

        if payload is None:
            stop_reason = (
                f"page {page} 요청 실패: {error}"
            )

            break

        pages_visited += 1

        items = payload.get(
            "content",
            []
        )

        if not items:
            stop_reason = (
                "목록이 비어 있음 (마지막 페이지 지남)"
            )

            break

        page_dates = []

        for item in items:
            published_at = (
                epoch_ms_to_datetime(
                    item.get(
                        "postPublishedAt"
                    )
                )
            )

            page_dates.append(
                published_at
            )

            if (
                published_at
                and published_at < cutoff
            ):
                continue

            url = urljoin(
                BASE_URL,
                item.get(
                    "url",
                    ""
                )
            )

            candidates.append(
                {
                    "url": url,
                    "title": normalize_text(
                        item.get(
                            "postTitle",
                            ""
                        )
                    ),
                    "published_at": (
                        published_at
                        .isoformat()
                        if published_at
                        else None
                    )
                }
            )

        # 날짜순 정렬(최신 우선)이 전제이므로,
        # 이 페이지의 모든 글이 cutoff보다 오래됐다면
        # 더 넘길 필요가 없다.
        resolved_dates = [
            date
            for date in page_dates
            if date is not None
        ]

        if (
            resolved_dates
            and all(
                date < cutoff
                for date in resolved_dates
            )
        ):
            stop_reason = (
                "페이지 내 게시일이 모두 cutoff 이전"
            )

            last_page_index = page

            break

        links = {
            link.get("rel"): link.get("href")
            for link in payload.get(
                "links",
                []
            )
        }

        next_href = links.get(
            "next"
        )

        if not next_href:
            stop_reason = (
                "next 링크 없음 (마지막 페이지)"
            )

            last_page_index = page

            break

        next_page = parse_page_param(
            next_href
        )

        if (
            next_page is None
            or next_page <= page
        ):
            stop_reason = (
                "next page 값을 해석할 수 없음"
            )

            break

        page = next_page

        if delay > 0:
            time.sleep(
                delay
            )

    else:
        stop_reason = (
            f"안전 상한({MAX_PAGES}페이지) 도달"
        )

    return (
        candidates,
        {
            "pages_visited": (
                pages_visited
            ),
            "last_page_index": (
                last_page_index
            ),
            "candidate_count": len(
                candidates
            ),
            "stop_reason": stop_reason
        }
    )


def extract_id_from_url(url):
    path = urlparse(
        url
    ).path

    segments = [
        segment
        for segment in path.split("/")
        if segment
    ]

    if not segments:
        return None

    return segments[-1]


def html_to_text(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    return normalize_text(
        text
    )


def fetch_full_content(
    session,
    candidate
):
    content_id = extract_id_from_url(
        candidate["url"]
    )

    if not content_id:
        return None, "content id를 URL에서 못 찾음"

    detail_url = (
        f"{API_URL}/{content_id}"
    )

    try:
        response = session.get(
            detail_url,
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        return None, str(error)

    if not response.ok:
        return (
            None,
            f"HTTP {response.status_code}"
        )

    try:
        detail = response.json()

    except ValueError as error:
        return None, str(error)

    html = detail.get(
        "postHtml",
        ""
    )

    content = html_to_text(
        html
    )

    if not content:
        return None, "본문이 비어 있음"

    return content, None


def build_article(
    candidate,
    content
):
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
            create_article_id(
                candidate["url"]
            )
        ),
        "company": COMPANY,
        "title": candidate["title"],
        "published_at": (
            candidate["published_at"]
        ),
        "url": candidate["url"],
        "discovered_by": [
            "custom_adapter:naver_d2"
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
    }


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
    print("NAVER D2 CUSTOM ADAPTER")
    print("=" * 60)

    candidates, list_report = (
        collect_candidates(
            session=session,
            cutoff=cutoff,
            page_size=PAGE_SIZE,
            delay=args.delay
        )
    )

    print(
        "목록 API 페이지 방문:",
        list_report["pages_visited"]
    )

    print(
        "중단 사유:",
        list_report["stop_reason"]
    )

    print(
        "최근 12개월 후보:",
        len(candidates)
    )

    articles = []
    failed = []

    for index, candidate in enumerate(
        candidates,
        start=1
    ):
        print(
            f"[{index}/{len(candidates)}]",
            candidate["title"]
        )

        content, error = (
            fetch_full_content(
                session,
                candidate
            )
        )

        if error:
            failed.append(
                {
                    "url": candidate["url"],
                    "reason": error
                }
            )

            continue

        articles.append(
            build_article(
                candidate,
                content
            )
        )

        if args.delay > 0:
            time.sleep(
                args.delay
            )

    articles.sort(
        key=lambda article: (
            article["published_at"]
            or ""
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
        "listing": list_report,
        "candidate_count": len(
            candidates
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
        len(candidates)
    )

    print(
        "본문 추출 성공:",
        len(articles)
    )

    print(
        "본문 추출 실패:",
        len(failed)
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
