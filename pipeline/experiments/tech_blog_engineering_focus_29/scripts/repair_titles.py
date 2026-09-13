"""census가 채운 title 중 무효한 것을 자체적으로 다시 보강한다.

census의 backfill_titles.py는 건드리지 않는다 (다른 실험 소유).
여기서는 census 결과를 읽기 전용으로 재사용하고, 결과는
이 실험 폴더(data/work/tech_blog_engineering_focus_29)에만 저장한다.

무효 title 판정 (회사별 조건분기 없이 전부 동일한 규칙):
  1. 빈 문자열
  2. 같은 회사 안에서 동일한 제목이 서로 다른 article_id에
     3번 이상 반복됨 (사이트 공통 타이틀 — 예: 배너 문구,
     "OO Tech Blog" 같은 사이트 전체 타이틀이 개별 글의
     og:title/<title>에도 그대로 박혀 있는 경우)

보강 순서 (generic, 사이트별 분기 없음):
  JSON-LD headline -> og:title -> twitter:title -> <h1> -> <title>
"""

import argparse
import html as html_module
import json
import re
import time

from pathlib import Path
from urllib.parse import urlparse

import requests

from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CENSUS_EXTRACTED_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_company_role_census"
    / "extracted"
    / "articles.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
)

REPAIRED_TITLES_FILE = (
    OUTPUT_DIR
    / "repaired_titles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "repair_titles_report.json"
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

# 같은 회사 안에서 이 횟수 이상 반복되는 제목은
# 개별 글 제목이 아니라 사이트 공통 타이틀로 본다.
BOILERPLATE_MIN_REPEAT = 3


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


def normalize_title(text):
    if not text:
        return ""

    text = html_module.unescape(
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def find_json_ld_headline(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

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
            headline = extract_headline(
                item
            )

            if headline:
                return headline

    return None


def extract_headline(value):
    if isinstance(value, list):
        for item in value:
            result = extract_headline(
                item
            )

            if result:
                return result

        return None

    if not isinstance(value, dict):
        return None

    headline = value.get(
        "headline"
    )

    if (
        isinstance(headline, str)
        and headline.strip()
    ):
        return headline

    for child in value.values():
        result = extract_headline(
            child
        )

        if result:
            return result

    return None


def find_meta_content(
    soup,
    attr_name,
    attr_value
):
    meta = soup.find(
        "meta",
        attrs={
            attr_name: attr_value
        }
    )

    if meta and meta.get("content"):
        return meta["content"]

    return None


def find_h1(soup):
    h1 = soup.find("h1")

    if h1:
        text = h1.get_text(
            " ",
            strip=True
        )

        if text:
            return text

    return None


def find_title_tag(soup):
    if soup.title:
        text = soup.title.get_text(
            " ",
            strip=True
        )

        if text:
            return text

    return None


def extract_best_title(html):
    headline = find_json_ld_headline(
        html
    )

    if headline:
        return (
            normalize_title(headline),
            "json_ld_headline"
        )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    og_title = find_meta_content(
        soup,
        "property",
        "og:title"
    )

    if og_title:
        return (
            normalize_title(og_title),
            "og_title"
        )

    twitter_title = find_meta_content(
        soup,
        "name",
        "twitter:title"
    )

    if twitter_title:
        return (
            normalize_title(
                twitter_title
            ),
            "twitter_title"
        )

    h1_text = find_h1(soup)

    if h1_text:
        return (
            normalize_title(h1_text),
            "h1"
        )

    title_text = find_title_tag(
        soup
    )

    if title_text:
        return (
            normalize_title(
                title_text
            ),
            "title_tag"
        )

    return (None, None)


def find_boilerplate_titles(
    articles
):
    by_company = {}

    for article in articles:
        title = normalize_title(
            article.get("title", "")
        )

        if not title:
            continue

        by_company.setdefault(
            article["company"],
            {}
        ).setdefault(
            title,
            set()
        ).add(
            article["article_id"]
        )

    boilerplate = set()

    for company, titles in (
        by_company.items()
    ):
        for title, ids in (
            titles.items()
        ):
            if (
                len(ids)
                >= BOILERPLATE_MIN_REPEAT
            ):
                boilerplate.add(
                    (company, title)
                )

    return boilerplate


def is_invalid_title(
    article,
    boilerplate_titles
):
    title = normalize_title(
        article.get("title", "")
    )

    if not title:
        return True

    return (
        article["company"],
        title
    ) in boilerplate_titles


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

    # Content-Type 헤더에 charset이 없으면 requests가
    # ISO-8859-1로 잘못 추정해 한글이 깨진다(라인플러스
    # 사이트에서 실제로 관측됨). charset이 명시 안 됐을
    # 때만 chardet 기반 추정치로 바꾼다.
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
        default=""
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

    articles = load_json(
        CENSUS_EXTRACTED_FILE
    )

    if company_allowlist:
        articles = [
            a
            for a in articles
            if a["company"]
            in company_allowlist
        ]

    boilerplate_titles = (
        find_boilerplate_titles(
            articles
        )
    )

    print()
    print("=" * 60)
    print("TITLE REPAIR")
    print("=" * 60)

    print(
        "대상 회사 공통(무효) 제목 패턴:",
        len(boilerplate_titles)
    )

    for company, title in sorted(
        boilerplate_titles
    ):
        print(
            f"  [{company}] "
            f"'{title}'"
        )

    targets = [
        a
        for a in articles
        if is_invalid_title(
            a,
            boilerplate_titles
        )
    ]

    print(
        "재보강 대상:",
        len(targets),
        "/",
        len(articles)
    )

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    fetched = {}
    failures = []

    for index, article in enumerate(
        targets,
        start=1
    ):
        html, error = fetch_html(
            session,
            article["url"]
        )

        if error:
            failures.append(
                {
                    "article_id": (
                        article[
                            "article_id"
                        ]
                    ),
                    "url": article["url"],
                    "reason": error
                }
            )

            continue

        title, source = (
            extract_best_title(html)
        )

        if (
            not title
            or (
                article["company"],
                title
            )
            in boilerplate_titles
        ):
            failures.append(
                {
                    "article_id": (
                        article[
                            "article_id"
                        ]
                    ),
                    "url": article["url"],
                    "reason": (
                        "유효한 제목을 찾지 못함"
                    )
                }
            )

            continue

        fetched[
            article["article_id"]
        ] = {
            "company": article[
                "company"
            ],
            "title": title,
            "source": source
        }

        print(
            f"[{index}/{len(targets)}]",
            f"[{article['company']}]",
            f"({source})",
            title[:60]
        )

        if index % 30 == 0:
            save_json(
                REPAIRED_TITLES_FILE,
                {
                    aid: {
                        "title": entry[
                            "title"
                        ],
                        "source": entry[
                            "source"
                        ]
                    }
                    for aid, entry in (
                        fetched.items()
                    )
                }
            )

        time.sleep(DELAY)

    # 방금 새로 뽑은 title들 사이에서도 사이트 공통
    # 문구가 반복될 수 있다 (예: h1이 실제 글 제목이
    # 아니라 사이트 배너 텍스트인 템플릿). 원본
    # boilerplate_titles와 같은 기준(같은 회사에서
    # BOILERPLATE_MIN_REPEAT번 이상 반복)으로 한 번 더
    # 걸러낸다.
    new_title_counts = {}

    for entry in fetched.values():
        key = (
            entry["company"],
            entry["title"]
        )

        new_title_counts[key] = (
            new_title_counts.get(
                key,
                0
            )
            + 1
        )

    new_boilerplate = {
        key
        for key, count in (
            new_title_counts.items()
        )
        if count
        >= BOILERPLATE_MIN_REPEAT
    }

    repaired = {}
    source_counts = {}

    for article_id, entry in (
        fetched.items()
    ):
        key = (
            entry["company"],
            entry["title"]
        )

        if key in new_boilerplate:
            failures.append(
                {
                    "article_id": (
                        article_id
                    ),
                    "reason": (
                        "재보강 결과가 사이트 공통 "
                        "문구로 반복됨: "
                        f"'{entry['title']}'"
                    )
                }
            )

            continue

        repaired[article_id] = {
            "title": entry["title"],
            "source": entry["source"]
        }

        source_counts[
            entry["source"]
        ] = (
            source_counts.get(
                entry["source"],
                0
            )
            + 1
        )

    if new_boilerplate:
        print()
        print(
            "재보강 중 새로 발견된 사이트 공통 "
            "문구(제외됨):"
        )

        for company, title in sorted(
            new_boilerplate
        ):
            print(
                f"  [{company}] '{title}'"
            )

    save_json(
        REPAIRED_TITLES_FILE,
        repaired
    )

    save_json(
        REPORT_FILE,
        {
            "input_count": len(
                articles
            ),
            "boilerplate_patterns": [
                {
                    "company": company,
                    "title": title
                }
                for company, title in (
                    sorted(
                        boilerplate_titles
                    )
                )
            ],
            "new_boilerplate_found_during_repair": [
                {
                    "company": company,
                    "title": title
                }
                for company, title in (
                    sorted(
                        new_boilerplate
                    )
                )
            ],
            "target_count": len(
                targets
            ),
            "repaired_count": len(
                repaired
            ),
            "failed_count": len(
                failures
            ),
            "source_counts": (
                source_counts
            ),
            "failures": failures
        }
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    print(
        "재보강 성공:",
        len(repaired)
    )

    print(
        "실패:",
        len(failures)
    )

    print(
        "출처 분포:",
        source_counts
    )

    print(
        "저장:",
        REPAIRED_TITLES_FILE
    )


if __name__ == "__main__":
    main()
