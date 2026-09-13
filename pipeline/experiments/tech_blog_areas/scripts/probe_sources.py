import argparse
import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

import feedparser
import requests
from dateutil import parser as date_parser


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_FILE = (
    PROJECT_ROOT
    / "pipeline"
    / "experiments"
    / "tech_blog_areas"
    / "config"
    / "blogs.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "probe"
    / "source_probe.json"
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


def save_json(file_path, data):
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


def parse_date(value):
    if not value:
        return None

    try:
        parsed = date_parser.parse(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except (ValueError, TypeError):
        return None


def discover_robots_sitemaps(
    session,
    blog_url
):
    robots_url = urljoin(
        blog_url,
        "/robots.txt"
    )

    result = {
        "url": robots_url,
        "available": False,
        "status_code": None,
        "sitemaps": []
    }

    try:
        response = session.get(
            robots_url,
            timeout=TIMEOUT
        )

        result["status_code"] = (
            response.status_code
        )

        if response.ok:
            result["available"] = True

            for line in response.text.splitlines():
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
                        result[
                            "sitemaps"
                        ].append(
                            sitemap_url
                        )

    except requests.RequestException as e:
        result["error"] = str(e)

    return result


def get_rss_candidates(source):
    blog_url = source["blog_url"]

    candidates = []

    configured_rss = source.get(
        "rss_url"
    )

    if configured_rss:
        candidates.append(
            configured_rss
        )

    default_candidates = [
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

    candidates.extend(
        default_candidates
    )

    return list(
        dict.fromkeys(
            candidates
        )
    )


def probe_rss(
    session,
    rss_url,
    cutoff
):
    result = {
        "url": rss_url,
        "available": False,
        "status_code": None,
        "entry_count": 0,
        "oldest_date": None,
        "newest_date": None,
        "coverage": "unknown"
    }

    try:
        response = session.get(
            rss_url,
            timeout=TIMEOUT
        )

        result["status_code"] = (
            response.status_code
        )

        if not response.ok:
            return result

        feed = feedparser.parse(
            response.content
        )

        if not feed.entries:
            return result

        result["available"] = True
        result["entry_count"] = len(
            feed.entries
        )

        dates = []

        for entry in feed.entries:
            raw_date = (
                entry.get("published")
                or entry.get("updated")
            )

            parsed_date = parse_date(
                raw_date
            )

            if parsed_date:
                dates.append(
                    parsed_date
                )

        if not dates:
            return result

        oldest = min(dates)
        newest = max(dates)

        result["oldest_date"] = (
            oldest.isoformat()
        )

        result["newest_date"] = (
            newest.isoformat()
        )

        if oldest <= cutoff:
            result["coverage"] = (
                "likely_sufficient"
            )
        else:
            result["coverage"] = (
                "insufficient"
            )

    except requests.RequestException as e:
        result["error"] = str(e)

    return result


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
    visited,
    leaf_results,
    all_urls,
    lastmods,
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

            if child_url:
                parse_sitemap(
                    session=session,
                    sitemap_url=child_url,
                    visited=visited,
                    leaf_results=leaf_results,
                    all_urls=all_urls,
                    lastmods=lastmods,
                    depth=depth + 1
                )

        return

    if root_name != "urlset":
        return

    urls = []

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

        if loc:
            urls.append(
                loc
            )

            all_urls.add(
                loc
            )

        if lastmod:
            lastmods.append(
                lastmod
            )

    leaf_results.append(
        {
            "url": sitemap_url,
            "url_count": len(urls),
            "sample_urls": urls[:3]
        }
    )


def probe_sitemaps(
    session,
    source,
    robots_result
):
    blog_url = source[
        "blog_url"
    ]

    candidates = []

    candidates.extend(
        robots_result.get(
            "sitemaps",
            []
        )
    )

    candidates.extend(
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

    candidates = list(
        dict.fromkeys(
            candidates
        )
    )

    visited = set()
    leaf_results = []
    all_urls = set()
    lastmods = []

    for candidate in candidates:
        parse_sitemap(
            session=session,
            sitemap_url=candidate,
            visited=visited,
            leaf_results=leaf_results,
            all_urls=all_urls,
            lastmods=lastmods
        )

    result = {
        "root_candidates": candidates,
        "visited_sitemap_count": (
            len(visited)
        ),
        "total_unique_urls": (
            len(all_urls)
        ),
        "leaf_sitemaps": (
            leaf_results
        ),
        "oldest_lastmod": None,
        "newest_lastmod": None
    }

    if lastmods:
        result["oldest_lastmod"] = (
            min(
                lastmods
            ).isoformat()
        )

        result["newest_lastmod"] = (
            max(
                lastmods
            ).isoformat()
        )

    return result


def choose_strategy(
    rss_results,
    sitemap_result
):
    working_rss = [
        item
        for item in rss_results
        if item["available"]
    ]

    sufficient_rss = [
        item
        for item in working_rss
        if (
            item["coverage"]
            == "likely_sufficient"
        )
    ]

    if sufficient_rss:
        return "rss"

    if (
        working_rss
        and sitemap_result[
            "total_unique_urls"
        ] > 0
    ):
        return "rss+sitemap"

    if (
        sitemap_result[
            "total_unique_urls"
        ] > 0
    ):
        return "sitemap"

    if working_rss:
        return "rss_insufficient"

    return "custom_or_archive"


def probe_company(
    session,
    source,
    cutoff
):
    company = source[
        "company"
    ]

    print()
    print("=" * 60)
    print(company)
    print("=" * 60)

    robots_result = (
        discover_robots_sitemaps(
            session,
            source["blog_url"]
        )
    )

    print(
        "robots:",
        robots_result[
            "status_code"
        ]
    )

    rss_results = []

    for rss_url in (
        get_rss_candidates(
            source
        )
    ):
        rss_result = probe_rss(
            session=session,
            rss_url=rss_url,
            cutoff=cutoff
        )

        rss_results.append(
            rss_result
        )

        if rss_result[
            "available"
        ]:
            print(
                "RSS:",
                rss_url
            )

            print(
                "  entries:",
                rss_result[
                    "entry_count"
                ]
            )

            print(
                "  oldest:",
                rss_result[
                    "oldest_date"
                ]
            )

            print(
                "  coverage:",
                rss_result[
                    "coverage"
                ]
            )

    sitemap_result = (
        probe_sitemaps(
            session=session,
            source=source,
            robots_result=robots_result
        )
    )

    print(
        "sitemap URLs:",
        sitemap_result[
            "total_unique_urls"
        ]
    )

    strategy = choose_strategy(
        rss_results,
        sitemap_result
    )

    print(
        "recommended strategy:",
        strategy
    )

    return {
        "company": company,
        "blog_url": source[
            "blog_url"
        ],
        "cutoff": (
            cutoff.isoformat()
        ),
        "robots": robots_result,
        "rss": rss_results,
        "sitemap": sitemap_result,
        "recommended_strategy": (
            strategy
        )
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--days",
        type=int,
        default=365
    )

    args = parser.parse_args()

    cutoff = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=args.days
        )
    )

    sources = load_json(
        CONFIG_FILE
    )

    session = requests.Session()
    session.headers.update(
        HEADERS
    )

    results = []

    for source in sources:
        if not source.get(
            "enabled",
            True
        ):
            continue

        result = probe_company(
            session=session,
            source=source,
            cutoff=cutoff
        )

        results.append(
            result
        )

    output = {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "days": args.days,
        "companies": results
    }

    save_json(
        OUTPUT_FILE,
        output
    )

    print()
    print("=" * 60)
    print("PROBE 완료")
    print("=" * 60)

    print(
        "저장:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
    