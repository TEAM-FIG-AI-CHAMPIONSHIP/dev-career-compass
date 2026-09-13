import argparse
import gzip
import hashlib
import json
import time
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urldefrag

import feedparser
import requests

from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_FILE = (
    PROJECT_ROOT
    / "pipeline"
    / "experiments"
    / "tech_blog_areas"
    / "config"
    / "blogs.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "collected"
)

ARTICLES_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "collect_report.json"
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
MAX_SITEMAPS = 50


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


def normalize_url(url):
    url, _ = urldefrag(
        url.strip()
    )

    return url


def create_article_id(url):
    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:16]


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


def get_rss_candidates(source):
    blog_url = source[
        "blog_url"
    ]

    candidates = []

    configured_rss = source.get(
        "rss_url"
    )

    if configured_rss:
        candidates.append(
            configured_rss
        )

    candidates.extend(
        [
            urljoin(
                blog_url,
                "/feed/"
            ),
            urljoin(
                blog_url,
                "/rss.xml"
            ),
            urljoin(
                blog_url,
                "/feed.xml"
            ),
            urljoin(
                blog_url,
                "/atom.xml"
            )
        ]
    )

    return list(
        dict.fromkeys(
            candidates
        )
    )


def collect_rss(
    session,
    source,
    cutoff
):
    articles = {}
    working_rss_url = None
    total_entries = 0

    for rss_url in get_rss_candidates(
        source
    ):
        try:
            response = session.get(
                rss_url,
                timeout=TIMEOUT
            )

        except requests.RequestException:
            continue

        if not response.ok:
            continue

        feed = feedparser.parse(
            response.content
        )

        if not feed.entries:
            continue

        working_rss_url = rss_url
        total_entries = len(
            feed.entries
        )

        for entry in feed.entries:
            url = normalize_url(
                entry.get(
                    "link",
                    ""
                )
            )

            if not url:
                continue

            raw_date = (
                entry.get("published")
                or entry.get("updated")
            )

            published_at = parse_date(
                raw_date
            )

            if (
                published_at
                and published_at < cutoff
            ):
                continue

            articles[url] = {
                "url": url,
                "title": (
                    entry.get(
                        "title",
                        ""
                    ).strip()
                ),
                "published_at": (
                    published_at
                    .isoformat()
                    if published_at
                    else None
                ),
                "discovered_by": [
                    "rss"
                ]
            }

        # 첫 번째로 정상 동작하는 RSS만 사용
        break

    return (
        articles,
        {
            "rss_url": (
                working_rss_url
            ),
            "entry_count": (
                total_entries
            ),
            "recent_article_count": (
                len(articles)
            )
        }
    )


def discover_robots_sitemaps(
    session,
    blog_url
):
    robots_url = urljoin(
        blog_url,
        "/robots.txt"
    )

    sitemaps = []

    try:
        response = session.get(
            robots_url,
            timeout=TIMEOUT
        )

        if response.ok:
            for line in (
                response.text
                .splitlines()
            ):
                line = line.strip()

                if line.lower().startswith(
                    "sitemap:"
                ):
                    sitemap_url = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

                    if sitemap_url:
                        sitemaps.append(
                            sitemap_url
                        )

    except requests.RequestException:
        pass

    return sitemaps


def should_skip_leaf_sitemap(
    sitemap_url
):
    name = sitemap_url.lower()

    excluded_words = [
        "attachment",
        "image",
        "category",
        "tag-sitemap",
        "author",
        "page-sitemap"
    ]

    return any(
        word in name
        for word in excluded_words
    )


def decode_xml(content):
    if content.startswith(
        b"\x1f\x8b"
    ):
        return gzip.decompress(
            content
        )

    return content


def parse_sitemap(
    session,
    sitemap_url,
    cutoff,
    visited,
    candidates,
    leaf_reports,
    depth=0
):
    if sitemap_url in visited:
        return

    if len(visited) >= MAX_SITEMAPS:
        return

    if depth > 5:
        return

    visited.add(
        sitemap_url
    )

    try:
        response = session.get(
            sitemap_url,
            timeout=TIMEOUT
        )

        if not response.ok:
            return

        xml_content = decode_xml(
            response.content
        )

        root = ET.fromstring(
            xml_content
        )

    except (
        requests.RequestException,
        ET.ParseError,
        OSError
    ):
        return

    root_name = (
        root.tag
        .split("}")[-1]
        .lower()
    )

    if root_name == "sitemapindex":
        for element in root:
            if (
                element.tag
                .split("}")[-1]
                .lower()
                != "sitemap"
            ):
                continue

            child_url = None

            for child in element:
                tag_name = (
                    child.tag
                    .split("}")[-1]
                    .lower()
                )

                if tag_name == "loc":
                    child_url = (
                        child.text or ""
                    ).strip()

            if not child_url:
                continue

            if should_skip_leaf_sitemap(
                child_url
            ):
                continue

            parse_sitemap(
                session=session,
                sitemap_url=child_url,
                cutoff=cutoff,
                visited=visited,
                candidates=candidates,
                leaf_reports=leaf_reports,
                depth=depth + 1
            )

        return

    if root_name != "urlset":
        return

    if should_skip_leaf_sitemap(
        sitemap_url
    ):
        return

    total_urls = 0
    recent_candidates = 0

    for element in root:
        if (
            element.tag
            .split("}")[-1]
            .lower()
            != "url"
        ):
            continue

        loc = None
        lastmod = None

        for child in element:
            tag_name = (
                child.tag
                .split("}")[-1]
                .lower()
            )

            if tag_name == "loc":
                loc = (
                    child.text or ""
                ).strip()

            elif tag_name == "lastmod":
                lastmod = parse_date(
                    (
                        child.text
                        or ""
                    ).strip()
                )

        if not loc:
            continue

        total_urls += 1

        # lastmod가 cutoff보다 오래됐다면
        # 최근 게시글일 가능성이 없다고 보고 사전 제외.
        #
        # lastmod가 최근이라고 해서 최근 게시글이라고
        # 확정하지는 않는다.
        if (
            lastmod
            and lastmod < cutoff
        ):
            continue

        url = normalize_url(
            loc
        )

        candidates[url] = {
            "url": url,
            "sitemap_lastmod": (
                lastmod.isoformat()
                if lastmod
                else None
            )
        }

        recent_candidates += 1

    leaf_reports.append(
        {
            "url": sitemap_url,
            "total_urls": total_urls,
            "candidate_urls": (
                recent_candidates
            )
        }
    )


def collect_sitemap_candidates(
    session,
    source,
    cutoff
):
    blog_url = source[
        "blog_url"
    ]

    root_candidates = (
        discover_robots_sitemaps(
            session,
            blog_url
        )
    )

    root_candidates.extend(
        [
            urljoin(
                blog_url,
                "/sitemap.xml"
            ),
            urljoin(
                blog_url,
                "/wp-sitemap.xml"
            )
        ]
    )

    root_candidates = list(
        dict.fromkeys(
            root_candidates
        )
    )

    visited = set()
    candidates = {}
    leaf_reports = []

    for sitemap_url in root_candidates:
        parse_sitemap(
            session=session,
            sitemap_url=sitemap_url,
            cutoff=cutoff,
            visited=visited,
            candidates=candidates,
            leaf_reports=leaf_reports
        )

    report = {
        "root_sitemaps": (
            root_candidates
        ),
        "visited_sitemap_count": (
            len(visited)
        ),
        "candidate_count": (
            len(candidates)
        ),
        "leaf_sitemaps": (
            leaf_reports
        )
    }

    return (
        candidates,
        report
    )


def find_json_ld_article(
    value
):
    if isinstance(
        value,
        list
    ):
        for item in value:
            result = (
                find_json_ld_article(
                    item
                )
            )

            if result:
                return result

        return None

    if not isinstance(
        value,
        dict
    ):
        return None

    item_type = value.get(
        "@type"
    )

    if isinstance(
        item_type,
        list
    ):
        types = {
            str(item).lower()
            for item in item_type
        }

    else:
        types = {
            str(item_type).lower()
        }

    article_types = {
        "article",
        "blogposting",
        "newsarticle",
        "techarticle"
    }

    if (
        types
        & article_types
    ):
        return value

    for child in value.values():
        result = (
            find_json_ld_article(
                child
            )
        )

        if result:
            return result

    return None


def extract_page_metadata(
    html,
    requested_url
):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title = None
    published_at = None
    canonical_url = requested_url

    # JSON-LD 우선
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

        article = (
            find_json_ld_article(
                data
            )
        )

        if not article:
            continue

        if not title:
            headline = article.get(
                "headline"
            )

            if isinstance(
                headline,
                str
            ):
                title = headline.strip()

        if not published_at:
            published_at = parse_date(
                article.get(
                    "datePublished"
                )
            )

        if (
            title
            and published_at
        ):
            break

    # Open Graph / meta fallback
    if not title:
        meta_title = soup.find(
            "meta",
            attrs={
                "property": "og:title"
            }
        )

        if (
            meta_title
            and meta_title.get(
                "content"
            )
        ):
            title = (
                meta_title[
                    "content"
                ].strip()
            )

    if not published_at:
        date_meta_candidates = [
            (
                "property",
                "article:published_time"
            ),
            (
                "name",
                "datePublished"
            ),
            (
                "name",
                "publish_date"
            ),
            (
                "name",
                "pubdate"
            ),
            (
                "name",
                "date"
            )
        ]

        for attr_name, attr_value in (
            date_meta_candidates
        ):
            meta = soup.find(
                "meta",
                attrs={
                    attr_name: attr_value
                }
            )

            if (
                meta
                and meta.get(
                    "content"
                )
            ):
                published_at = parse_date(
                    meta["content"]
                )

                if published_at:
                    break

    # 마지막 fallback
    if not published_at:
        time_tag = soup.find(
            "time",
            attrs={
                "datetime": True
            }
        )

        if time_tag:
            published_at = parse_date(
                time_tag.get(
                    "datetime"
                )
            )

    if not title:
        h1 = soup.find(
            "h1"
        )

        if h1:
            title = (
                h1.get_text(
                    " ",
                    strip=True
                )
            )

    if (
        not title
        and soup.title
    ):
        title = (
            soup.title
            .get_text(
                " ",
                strip=True
            )
        )

    canonical = soup.find(
        "link",
        attrs={
            "rel": "canonical"
        }
    )

    if (
        canonical
        and canonical.get(
            "href"
        )
    ):
        canonical_url = normalize_url(
            canonical["href"]
        )

    return {
        "title": (
            title or ""
        ),
        "published_at": (
            published_at
        ),
        "url": (
            canonical_url
        )
    }


def fetch_page_metadata(
    session,
    url
):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT
        )

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }

    if not response.ok:
        return {
            "success": False,
            "error": (
                f"HTTP {response.status_code}"
            )
        }

    content_type = (
        response.headers
        .get(
            "content-type",
            ""
        )
        .lower()
    )

    if (
        "text/html"
        not in content_type
    ):
        return {
            "success": False,
            "error": (
                f"not html: {content_type}"
            )
        }

    metadata = extract_page_metadata(
        response.text,
        url
    )

    metadata["success"] = True

    return metadata


def merge_candidates(
    rss_articles,
    sitemap_candidates
):
    merged = {}

    for url, article in (
        sitemap_candidates.items()
    ):
        merged[url] = {
            "url": url,
            "title": "",
            "published_at": None,
            "sitemap_lastmod": (
                article.get(
                    "sitemap_lastmod"
                )
            ),
            "discovered_by": [
                "sitemap"
            ]
        }

    for url, article in (
        rss_articles.items()
    ):
        if url not in merged:
            merged[url] = article.copy()

        else:
            merged[url][
                "title"
            ] = article.get(
                "title",
                ""
            )

            merged[url][
                "published_at"
            ] = article.get(
                "published_at"
            )

            merged[url][
                "discovered_by"
            ].append(
                "rss"
            )

    return merged


def collect_company(
    session,
    source,
    cutoff,
    delay
):
    company = source[
        "company"
    ]

    print()
    print("=" * 60)
    print(company)
    print("=" * 60)

    rss_articles, rss_report = (
        collect_rss(
            session=session,
            source=source,
            cutoff=cutoff
        )
    )

    print(
        "RSS 최근 후보:",
        len(rss_articles)
    )

    (
        sitemap_candidates,
        sitemap_report
    ) = collect_sitemap_candidates(
        session=session,
        source=source,
        cutoff=cutoff
    )

    print(
        "Sitemap 최근 lastmod 후보:",
        len(
            sitemap_candidates
        )
    )

    candidates = merge_candidates(
        rss_articles,
        sitemap_candidates
    )

    print(
        "중복 제거 후 후보:",
        len(candidates)
    )

    articles = []
    failed = []
    filtered_old = 0
    missing_date = 0
    html_checked = 0

    for index, (
        original_url,
        candidate
    ) in enumerate(
        candidates.items(),
        start=1
    ):
        print(
            f"[{index}/{len(candidates)}]",
            original_url
        )

        published_at = parse_date(
            candidate.get(
                "published_at"
            )
        )

        title = candidate.get(
            "title",
            ""
        )

        final_url = original_url

        # RSS에 실제 게시일이 있으면
        # 페이지 요청을 생략할 수 있다.
        if not published_at:
            metadata = fetch_page_metadata(
                session,
                original_url
            )

            html_checked += 1

            if not metadata[
                "success"
            ]:
                failed.append(
                    {
                        "url": (
                            original_url
                        ),
                        "reason": (
                            metadata[
                                "error"
                            ]
                        )
                    }
                )

                continue

            title = (
                metadata["title"]
                or title
            )

            published_at = (
                metadata[
                    "published_at"
                ]
            )

            final_url = (
                metadata["url"]
                or original_url
            )

            if delay > 0:
                time.sleep(
                    delay
                )

        if not published_at:
            missing_date += 1

            failed.append(
                {
                    "url": (
                        original_url
                    ),
                    "reason": (
                        "published date not found"
                    )
                }
            )

            continue

        if published_at < cutoff:
            filtered_old += 1
            continue

        final_url = normalize_url(
            final_url
        )

        articles.append(
            {
                "article_id": (
                    create_article_id(
                        final_url
                    )
                ),
                "company": company,
                "title": title,
                "published_at": (
                    published_at
                    .isoformat()
                ),
                "url": final_url,
                "discovered_by": sorted(
                    set(
                        candidate[
                            "discovered_by"
                        ]
                    )
                )
            }
        )

    deduped = {}

    for article in articles:
        deduped[
            article["url"]
        ] = article

    articles = list(
        deduped.values()
    )

    articles.sort(
        key=lambda article: (
            article["published_at"]
        ),
        reverse=True
    )

    report = {
        "company": company,
        "cutoff": cutoff.isoformat(),
        "rss": rss_report,
        "sitemap": sitemap_report,
        "merged_candidate_count": (
            len(candidates)
        ),
        "html_checked": (
            html_checked
        ),
        "filtered_old": (
            filtered_old
        ),
        "missing_date": (
            missing_date
        ),
        "failed_count": (
            len(failed)
        ),
        "collected_count": (
            len(articles)
        ),
        "failures": failed
    }

    print()
    print(
        "최근 12개월 확정:",
        len(articles)
    )

    print(
        "실제 게시일이 오래되어 제외:",
        filtered_old
    )

    print(
        "게시일 확인 실패:",
        missing_date
    )

    print(
        "요청 실패:",
        len(failed)
    )

    return (
        articles,
        report
    )


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

    sources = load_json(
        CONFIG_FILE
    )

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    all_articles = []
    reports = []

    print()
    print("=" * 60)
    print("COLLECT 시작")
    print("=" * 60)

    for source in sources:
        if not source.get(
            "enabled",
            True
        ):
            continue

        (
            articles,
            report
        ) = collect_company(
            session=session,
            source=source,
            cutoff=cutoff,
            delay=args.delay
        )

        all_articles.extend(
            articles
        )

        reports.append(
            report
        )

    all_articles.sort(
        key=lambda article: (
            article[
                "published_at"
            ]
        ),
        reverse=True
    )

    save_json(
        ARTICLES_FILE,
        all_articles
    )

    save_json(
        REPORT_FILE,
        {
            "generated_at": (
                now.isoformat()
            ),
            "months": (
                args.months
            ),
            "companies": (
                reports
            )
        }
    )

    print()
    print("=" * 60)
    print("COLLECT 완료")
    print("=" * 60)

    print(
        "총 게시글:",
        len(all_articles)
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
    