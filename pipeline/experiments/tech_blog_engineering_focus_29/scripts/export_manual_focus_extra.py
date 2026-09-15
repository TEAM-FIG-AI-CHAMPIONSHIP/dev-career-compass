"""census 표준 경로로 안 잡힌 네이버(D2)·당근을 위한 추가 manual prompt.

- 네이버: tech_blog_areas 실험에서 이미 확보한 D2 JSON API 수집분(69건)을
  재사용한다.
- 당근: Medium archive는 403으로 막혀 있어(직접 확인함) RSS만 사용한다.
  Medium RSS는 본문 전체(content:encoded)를 포함하지만 최근 10건뿐이라
  12개월 전체가 아니다 — 파일에 명시적으로 표시한다.

census의 classify_and_gate.classify_article()을 읽기 전용으로 재사용해
기술글 여부를 판정한다 (LLM 아님, 그쪽 파일은 건드리지 않음).
"""

import calendar
import hashlib
import html
import json
import re
import sys

from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

from bs4 import BeautifulSoup


SCRIPTS_DIR = Path(__file__).resolve().parent

CENSUS_SCRIPTS_DIR = (
    SCRIPTS_DIR.parents[1]
    / "tech_blog_company_role_census"
    / "scripts"
)

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

sys.path.insert(
    0,
    str(CENSUS_SCRIPTS_DIR)
)

from extract_engineering_focus import (  # noqa: E402
    SYSTEM_PROMPT,
    build_exclusion_reason
)

from classify_and_gate import (  # noqa: E402
    classify_article
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

MANUAL_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
    / "manual_prompts"
)

FOCUS_DIR = (
    MANUAL_DIR
    / "focus"
)

MANIFEST_FILE = (
    MANUAL_DIR
    / "focus_manifest_extra.json"
)

NAVER_D2_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "naver_d2"
    / "articles.json"
)

DAANGN_RSS_URL = (
    "https://medium.com/feed/daangn"
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


def html_to_text(raw_html):
    soup = BeautifulSoup(
        raw_html,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    text = html.unescape(
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def rss_entry_published_iso(entry):
    """feedparser가 RFC822 문자열(예: "Thu, 20 Aug 2026 02:25:36 GMT")을
    그대로 published_at에 저장하면 datetime.fromisoformat()으로 파싱이
    안 돼서 extract_engineering_focus.py의 12개월 cutoff 체크가 조용히
    무시된다(#91). feedparser가 같이 주는 published_parsed(UTC
    struct_time)를 ISO 문자열로 변환해서 저장한다."""

    parsed = entry.get("published_parsed")

    if not parsed:
        return entry.get("published", "")

    timestamp = calendar.timegm(parsed)

    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat()
    )


def load_naver_d2_articles():
    articles = load_json(
        NAVER_D2_FILE
    )

    out = []

    for article in articles:
        out.append(
            {
                "article_id": (
                    article["article_id"]
                ),
                "company": "네이버",
                "title": article["title"],
                "url": article["url"],
                "published_at": (
                    article["published_at"]
                ),
                "content": (
                    article["content"]
                )
            }
        )

    return out


def fetch_daangn_articles():
    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    response = session.get(
        DAANGN_RSS_URL,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    feed = feedparser.parse(
        response.content
    )

    out = []

    for entry in feed.entries:
        url = entry.get(
            "link",
            ""
        )

        if not url:
            continue

        raw_content = ""

        if entry.get("content"):
            raw_content = entry[
                "content"
            ][0].get(
                "value",
                ""
            )

        if not raw_content:
            raw_content = entry.get(
                "summary",
                ""
            )

        content = html_to_text(
            raw_content
        )

        if not content:
            continue

        article_id = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()[:16]

        out.append(
            {
                "article_id": article_id,
                "company": (
                    "당근마켓 / 당근"
                ),
                "title": entry.get(
                    "title",
                    ""
                ),
                "url": url,
                "published_at": (
                    rss_entry_published_iso(entry)
                ),
                "content": content
            }
        )

    return out


def build_prompt_text(
    company,
    articles,
    caveat
):
    payload = [
        {
            "article_id": (
                article["article_id"]
            ),
            "title": article["title"],
            "excerpt": (
                article["content"][
                    :3600
                ]
            )
        }
        for article in articles
    ]

    header_lines = [
        (
            "아래는 기술블로그 게시글에서 "
            "engineering_focus를 뽑는 작업입니다."
        ),
        f"회사: {company} ({len(articles)}건)",
        ""
    ]

    if caveat:
        header_lines.extend(
            [
                f"[참고] {caveat}",
                ""
            ]
        )

    header_lines.extend(
        [
            (
                "지시사항: 아래 SYSTEM 규칙을 따라 "
                "DATA의 각 게시글마다 "
                "engineering_focus를 작성하세요."
            ),
            (
                "출력은 다른 설명 없이 JSON 배열 "
                "하나만 출력하세요. 코드블록(```) "
                "없이, 다음 형식 그대로:"
            ),
            (
                '[{"article_id": "...", '
                '"engineering_focus": "..."}, ...]'
            ),
            (
                "DATA에 있는 article_id를 빠짐없이, "
                "정확히 한 번씩만 포함하세요."
            ),
            "",
            "=== SYSTEM ===",
            SYSTEM_PROMPT.strip(),
            "",
            "=== DATA ===",
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2
            )
        ]
    )

    return "\n".join(
        header_lines
    )


def process_company(
    company_label,
    raw_articles,
    caveat
):
    classified = [
        classify_article(article)
        for article in raw_articles
    ]

    classified_by_id = {
        c["article_id"]: c
        for c in classified
    }

    tech_articles = []

    for article in raw_articles:
        classification = (
            classified_by_id[
                article["article_id"]
            ]
        )

        if not classification["is_tech"]:
            continue

        # census 표준 경로를 안 타는 회사라 roles가 원래 없다.
        # classify_article()이 이미 계산해 둔 값(map_roles() 기반,
        # 회사명 분기 없는 동일 로직)을 그대로 가져와 붙인다.
        article_with_roles = {
            **article,
            "roles": classification.get(
                "roles",
                []
            )
        }

        with_hash = {
            **article_with_roles,
            "content_hash": (
                hashlib.sha256(
                    article["content"]
                    .encode("utf-8")
                ).hexdigest()
            )
        }

        if build_exclusion_reason(
            with_hash
        ):
            continue

        tech_articles.append(
            article_with_roles
        )

    print(
        f"{company_label}: 수집 "
        f"{len(raw_articles)}건 -> "
        f"기술글 {len(tech_articles)}건"
    )

    if not tech_articles:
        return None

    text = build_prompt_text(
        company_label,
        tech_articles,
        caveat
    )

    safe_name = (
        company_label
        .replace("/", "_")
        .replace(" ", "_")
    )

    filename = (
        f"{safe_name}__part1of1.txt"
    )

    file_path = (
        FOCUS_DIR / filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

    return {
        "company": company_label,
        "part_index": 1,
        "part_count": 1,
        "article_count": len(
            tech_articles
        ),
        "article_ids": [
            a["article_id"]
            for a in tech_articles
        ],
        "prompt_file": str(
            file_path.relative_to(
                PROJECT_ROOT
            )
        ),
        "expected_response_file": (
            f"focus_responses/{safe_name}"
            f"__part1of1.json"
        ),
        "caveat": caveat
    }


def main():
    FOCUS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    manifest = []

    naver_articles = (
        load_naver_d2_articles()
    )

    entry = process_company(
        "네이버",
        naver_articles,
        caveat=None
    )

    if entry:
        manifest.append(entry)

    print(
        "당근 Medium RSS 수집 중..."
    )

    daangn_articles = (
        fetch_daangn_articles()
    )

    entry = process_company(
        "당근마켓 / 당근",
        daangn_articles,
        caveat=(
            "Medium archive 페이지가 403으로 막혀 "
            "RSS만 사용함. 최근 10건, 최근 약 4개월 "
            "분량만 있고 12개월 전체가 아님."
        )
    )

    if entry:
        manifest.append(entry)

    save_json(
        MANIFEST_FILE,
        manifest
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    for item in manifest:
        print(
            item["company"],
            "->",
            item["prompt_file"],
            f"({item['article_count']}건)"
        )

    print(
        "매니페스트:",
        MANIFEST_FILE
    )


if __name__ == "__main__":
    main()
