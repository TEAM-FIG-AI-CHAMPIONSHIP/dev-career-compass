"""RSS 항목 수 상한으로 12개월을 못 닫은 회사를 보강한다.

토스처럼 sitemap이 없으면 Wayback CDX로 URL을 모은 뒤 라이브 페이지에서
게시일을 읽는다. 가비아·한컴처럼 wp-json이 열려 있으면 CDX보다 WP를 먼저 탄다.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urlparse, urlunparse

import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, COMPANIES_FILE, WAYBACK_REPORT
from url_filters import looks_like_article

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 20
CDX_TIMEOUT = 120
CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
WAYBACK_PREFIX = "https://web.archive.org/web"

# 토스 Next.js RSC 페이로드. JSON-LD/<time>이 없어 이 필드가 게시일 신호다.
TOSS_PUBLISHED_PATTERN = re.compile(r'publishedTime\\":\\"([^\\]+)')

DATE_PATTERNS = [
    r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
    r'content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
    r'<time[^>]+datetime=["\']([^"\']+)',
]

TARGETS = {
    "비바리퍼블리카 / 토스": {
        "cdx_patterns": ["toss.tech/article/*"],
        "path_must_include": "/article/",
        "wp_json": None,
        "use_toss_date": True,
    },
    "가비아": {
        "cdx_patterns": ["library.gabia.com/contents/*"],
        "path_must_include": "/contents/",
        "wp_json": "https://library.gabia.com/wp-json/wp/v2/posts",
        "use_toss_date": False,
    },
    "한컴": {
        "cdx_patterns": ["tech.hancom.com/*"],
        "path_must_include": None,
        "wp_json": "https://tech.hancom.com/wp-json/wp/v2/posts",
        "use_toss_date": False,
    },
    "구름": {
        "cdx_patterns": [],
        "wp_json": "https://tech.goorm.io/wp-json/wp/v2/posts",
        "use_toss_date": False,
    },
    "컴투스": {
        "cdx_patterns": [],
        "wp_json": "https://on.com2us.com/wp-json/wp/v2/posts",
        "wp_params": {"categories": "13"},
        "use_toss_date": False,
    },
    "넥스트리": {
        "cdx_patterns": [],
        "sitemap": "https://www.nextree.io/sitemap-posts.xml",
        "skip_lang_prefixes": ["en", "ru", "uz", "ja"],
        "skip_path_prefixes": ["hire", "hire-2"],
        "use_toss_date": False,
    },
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_url(url: str) -> str:
    url, _ = urldefrag((url or "").strip())
    parsed = urlparse(url)
    if parsed.query:
        parsed = parsed._replace(query="")
    return urlunparse(parsed)


def article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def parse_date(value):
    if not value:
        return None
    try:
        parsed = date_parser.parse(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value or "")
    return html.unescape(text).strip()


def extract_published(html_text: str, use_toss_date: bool):
    if use_toss_date:
        match = TOSS_PUBLISHED_PATTERN.search(html_text)
        if match:
            published = parse_date(match.group(1))
            if published:
                return published
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, html_text, re.I)
        if match:
            published = parse_date(match.group(1))
            if published:
                return published
    return None


def extract_title(html_text: str) -> str:
    match = re.search(r"<title>([^<]+)</title>", html_text, re.I)
    return strip_html(match.group(1)) if match else ""


def cdx_urls(session: requests.Session, pattern: str) -> dict[str, str]:
    """url -> 최신 스냅샷 timestamp."""
    params = {
        "url": pattern,
        "fl": "original,timestamp,statuscode",
        "filter": "statuscode:200",
        "collapse": "urlkey",
    }
    print(f"  cdx request {pattern}", flush=True)
    response = session.get(CDX_ENDPOINT, params=params, timeout=CDX_TIMEOUT)
    response.raise_for_status()
    found = {}
    for line in response.text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        if parts[0] in {"original", "timestamp"}:
            continue
        original, timestamp = parts[0], parts[1]
        if timestamp == "timestamp":
            continue
        url = normalize_url(original)
        if url not in found or timestamp > found[url]:
            found[url] = timestamp
    return found


def wp_posts(session: requests.Session, endpoint: str, after_iso: str, extra=None) -> list[dict]:
    posts = []
    page = 1
    while page <= 50:
        params = {
            "after": after_iso,
            "per_page": 100,
            "page": page,
            "_fields": "id,date,date_gmt,link,title",
        }
        if extra:
            params.update(extra)
        response = session.get(endpoint, params=params, timeout=TIMEOUT)
        if response.status_code == 400:
            break
        response.raise_for_status()
        batch = response.json()
        if not isinstance(batch, list) or not batch:
            break
        posts.extend(batch)
        total_pages = response.headers.get("X-WP-TotalPages")
        if total_pages and page >= int(total_pages):
            break
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.08)
    return posts


def sitemap_locs(session: requests.Session, sitemap_url: str, skip_langs=None) -> list[str]:
    skip_langs = {item.lower() for item in (skip_langs or [])}
    response = session.get(sitemap_url, timeout=TIMEOUT)
    response.raise_for_status()
    content = response.content
    if content.startswith(b"\x1f\x8b"):
        content = gzip.decompress(content)
    root = ET.fromstring(content)
    found = []
    for element in root:
        if not element.tag.endswith("url"):
            continue
        loc = ""
        for node in element:
            if node.tag.endswith("loc") and node.text:
                loc = node.text.strip()
        if not loc:
            continue
        parts = [part.lower() for part in urlparse(loc).path.split("/") if part]
        if parts and parts[0] in skip_langs:
            continue
        found.append(normalize_url(loc))
    return found


def wp_has_older(session: requests.Session, endpoint: str, cutoff, extra=None) -> bool:
    params = {
        "before": cutoff.strftime("%Y-%m-%dT00:00:00"),
        "per_page": 1,
        "_fields": "id,date",
    }
    if extra:
        params.update(extra)
    try:
        response = session.get(endpoint, params=params, timeout=TIMEOUT)
        if not response.ok:
            return False
        batch = response.json()
    except requests.RequestException:
        return False
    return isinstance(batch, list) and len(batch) > 0


def fetch_html(session: requests.Session, url: str, wayback_ts: str | None):
    try:
        response = session.get(url, timeout=TIMEOUT)
        if response.ok and "text/html" in response.headers.get("content-type", ""):
            return response.text, "live", None
        live_error = f"HTTP {response.status_code}"
    except requests.RequestException as exc:
        live_error = str(exc)[:200]
    if not wayback_ts:
        return None, None, live_error
    snapshot = f"{WAYBACK_PREFIX}/{wayback_ts}id_/{url}"
    try:
        response = session.get(snapshot, timeout=TIMEOUT)
        if response.ok:
            return response.text, "wayback", None
        return None, None, f"{live_error}; wayback HTTP {response.status_code}"
    except requests.RequestException as exc:
        return None, None, f"{live_error}; wayback {str(exc)[:200]}"


def collect_one(session, source, target, cutoff, existing_urls, delay, use_cdx):
    name = source["name"]
    blog_url = source["url"]
    added = []
    discovered = {}
    sources_used = []
    html_checked = 0
    html_failed = 0
    skipped_old = 0
    skipped_filter = 0

    if target.get("wp_json"):
        after_iso = cutoff.strftime("%Y-%m-%dT00:00:00")
        extra = target.get("wp_params") or {}
        posts = wp_posts(session, target["wp_json"], after_iso, extra)
        sources_used.append("wp_json")
        print(f"  wp-json {len(posts)}", flush=True)
        for post in posts:
            url = normalize_url(post.get("link") or "")
            if not url or url.rstrip("/") in existing_urls or url in discovered:
                continue
            must = target.get("path_must_include")
            path = urlparse(url).path
            if must and must not in path:
                continue
            if not looks_like_article(url, blog_url) and not (must and must in path):
                continue
            published = parse_date(post.get("date_gmt") or post.get("date"))
            title = strip_html((post.get("title") or {}).get("rendered") or "")
            if not published:
                continue
            discovered[url] = {
                "title": title,
                "published": published,
                "by": ["wp_json"],
            }
        if wp_has_older(session, target["wp_json"], cutoff, extra):
            skipped_old += 1

    sitemap_count = 0
    if target.get("sitemap"):
        locs = sitemap_locs(session, target["sitemap"], target.get("skip_lang_prefixes"))
        skip_paths = {item.lower() for item in (target.get("skip_path_prefixes") or [])}
        sources_used.append("sitemap")
        sitemap_count = len(locs)
        print(f"  sitemap {sitemap_count}", flush=True)
        pending = []
        for url in locs:
            path_parts = [part.lower() for part in urlparse(url).path.split("/") if part]
            if path_parts and path_parts[0] in skip_paths:
                skipped_filter += 1
                continue
            if url.rstrip("/") in existing_urls or url in discovered:
                continue
            if not looks_like_article(url, blog_url) and not target.get("skip_lang_prefixes"):
                skipped_filter += 1
                continue
            pending.append(url)
        print(f"  sitemap new {len(pending)}", flush=True)
        for url in pending:
            html_text, origin, error = fetch_html(session, url, None)
            html_checked += 1
            if delay:
                time.sleep(delay)
            if error or not html_text:
                html_failed += 1
                continue
            published = extract_published(html_text, target.get("use_toss_date", False))
            if not published:
                html_failed += 1
                continue
            discovered[url] = {
                "title": extract_title(html_text),
                "published": published,
                "by": ["sitemap", origin],
            }
            if html_checked % 25 == 0:
                print(f"  html {html_checked}/{len(pending)} kept {len(discovered)}", flush=True)

    need_cdx = bool(target.get("cdx_patterns")) and (
        use_cdx or (not target.get("wp_json") and not target.get("sitemap"))
    )
    cdx_map = {}
    if need_cdx:
        for pattern in target["cdx_patterns"]:
            print(f"  cdx {pattern}", flush=True)
            cdx_map.update(cdx_urls(session, pattern))
        sources_used.append("wayback_cdx")
        print(f"  cdx unique {len(cdx_map)}", flush=True)

    for url, timestamp in cdx_map.items():
        path = urlparse(url).path
        must = target.get("path_must_include")
        if must and must not in path:
            skipped_filter += 1
            continue
        if not looks_like_article(url, blog_url) and not (must and must in path):
            skipped_filter += 1
            continue
        if url.rstrip("/") in existing_urls or url in discovered:
            continue
        html_text, origin, error = fetch_html(session, url, timestamp)
        html_checked += 1
        if delay:
            time.sleep(delay)
        if error or not html_text:
            html_failed += 1
            continue
        published = extract_published(html_text, target.get("use_toss_date", False))
        if not published:
            html_failed += 1
            continue
        discovered[url] = {
            "title": extract_title(html_text),
            "published": published,
            "by": ["wayback_cdx", origin],
        }
        if html_checked % 25 == 0:
            print(f"  html {html_checked}/{len(cdx_map)} kept {len(discovered)}", flush=True)

    oldest = None
    for url, item in discovered.items():
        published = item["published"]
        if oldest is None or published < oldest:
            oldest = published
        if published < cutoff:
            skipped_old += 1
            continue
        added.append(
            {
                "article_id": article_id(url),
                "company": name,
                "blog_url": blog_url,
                "title": item["title"],
                "published_at": published.isoformat(),
                "url": url,
                "discovered_by": item["by"],
            }
        )
    added.sort(key=lambda row: row["published_at"], reverse=True)
    closed = bool(skipped_old > 0 or (oldest and oldest <= cutoff))
    print(f"  added {len(added)} old {skipped_old} closed {closed}", flush=True)
    return added, {
        "company": name,
        "strategy": "+".join(sources_used) or "none",
        "sitemap_count": sitemap_count,
        "html_checked": html_checked,
        "html_failed": html_failed,
        "skipped_filter": skipped_filter,
        "skipped_old": skipped_old,
        "added": len(added),
        "oldest": oldest.isoformat() if oldest else None,
        "closed_by_wayback": closed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--companies",
        default="비바리퍼블리카 / 토스,가비아,한컴",
        help="쉼표로 구분한 회사명. 기본은 토스·가비아·한컴",
    )
    parser.add_argument("--delay", type=float, default=0.12)
    parser.add_argument(
        "--cdx",
        action="store_true",
        help="wp-json이 있는 회사에도 CDX URL을 추가로 훑는다",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="이미 wayback_report에 있는 회사도 다시 돈다",
    )
    args = parser.parse_args()
    names = [name.strip() for name in args.companies.split(",") if name.strip()]

    now = datetime.now(timezone.utc)
    cutoff = now - relativedelta(months=12)
    sources = {item["name"]: item for item in load_json(COMPANIES_FILE)}
    articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    collect_report = load_json(COLLECT_REPORT) if COLLECT_REPORT.exists() else {"companies": []}
    report_by_company = {row["company"]: row for row in collect_report.get("companies", [])}
    wayback = load_json(WAYBACK_REPORT) if WAYBACK_REPORT.exists() else {"companies": []}
    done = {row["company"] for row in wayback.get("companies", [])}
    if args.force:
        reports = [row for row in wayback.get("companies", []) if row["company"] not in names]
        done -= set(names)
    else:
        reports = [row for row in wayback.get("companies", []) if row["company"] in done]

    session = requests.Session()
    session.headers.update(HEADERS)

    for name in names:
        if name not in TARGETS:
            print("설정 없음", name)
            continue
        if name in done and not args.force:
            print("이미 완료", name)
            continue
        source = sources[name]
        existing = {
            normalize_url(item["url"]).rstrip("/")
            for item in articles
            if item["company"] == name
        }
        print(f"\n=== WAYBACK {name} already {len(existing)} ===", flush=True)
        try:
            found, report = collect_one(
                session,
                source,
                TARGETS[name],
                cutoff,
                existing,
                args.delay,
                args.cdx,
            )
        except Exception as exc:  # noqa: BLE001
            found, report = [], {
                "company": name,
                "strategy": "error",
                "error": str(exc)[:300],
                "added": 0,
                "closed_by_wayback": False,
            }
            print("실패", name, exc)
        articles.extend(found)
        reports.append(report)
        row = report_by_company.get(name)
        if row is not None:
            row["collected_count"] = row.get("collected_count", 0) + len(found)
            row["collectable"] = row["collected_count"] > 0
            if report.get("closed_by_wayback"):
                row["twelve_month_closed"] = True
            row["wayback"] = report
        save_json(ARTICLES_FILE, articles)
        save_json(COLLECT_REPORT, collect_report)
        save_json(WAYBACK_REPORT, {"generated_at": now.isoformat(), "companies": reports})

    print("wayback 완료", len(reports), "총 글", len(articles))


if __name__ == "__main__":
    main()
