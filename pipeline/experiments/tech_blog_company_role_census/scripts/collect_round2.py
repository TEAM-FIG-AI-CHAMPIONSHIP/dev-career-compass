"""RSS로 12개월을 못 닫은 회사에 sitemap fallback을 적용한다.

RSS 0건과 RSS 부족 회사만 대상이다. Medium 전역 sitemap은 따라가지 않는다.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, COMPANIES_FILE, ROUND2_REPORT
from url_filters import looks_like_article

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 12
MAX_SITEMAPS = 25
MAX_HTML = 60
SKIP_SITEMAP_WORDS = ("attachment", "image", "category", "tag-sitemap", "author", "page-sitemap")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_url(url: str) -> str:
    url, _ = urldefrag((url or "").strip())
    return url


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


def under_blog(url: str, blog_url: str) -> bool:
    prefix = blog_url.rstrip("/") + "/"
    return url.rstrip("/") == blog_url.rstrip("/") or url.startswith(prefix)


def robots_sitemaps(session: requests.Session, blog_url: str) -> list[str]:
    found = []
    try:
        response = session.get(urljoin(blog_url, "/robots.txt"), timeout=TIMEOUT)
    except requests.RequestException:
        return found
    if not response.ok:
        return found
    for line in response.text.splitlines():
        if line.lower().startswith("sitemap:"):
            sitemap = line.split(":", 1)[1].strip()
            if sitemap:
                found.append(sitemap)
    return found


def decode_xml(content: bytes) -> bytes:
    if content.startswith(b"\x1f\x8b"):
        return gzip.decompress(content)
    return content


def parse_sitemap(session, sitemap_url, cutoff, visited, candidates, old_count, depth=0) -> None:
    if sitemap_url in visited or len(visited) >= MAX_SITEMAPS or depth > 4:
        return
    visited.add(sitemap_url)
    if any(word in sitemap_url.lower() for word in SKIP_SITEMAP_WORDS):
        return
    try:
        response = session.get(sitemap_url, timeout=TIMEOUT)
        if not response.ok:
            return
        root = ET.fromstring(decode_xml(response.content))
    except (requests.RequestException, ET.ParseError, OSError):
        return
    name = root.tag.split("}")[-1].lower()
    if name == "sitemapindex":
        for element in root:
            if element.tag.split("}")[-1].lower() != "sitemap":
                continue
            child = ""
            for node in element:
                if node.tag.split("}")[-1].lower() == "loc":
                    child = (node.text or "").strip()
            if child:
                parse_sitemap(session, child, cutoff, visited, candidates, old_count, depth + 1)
        return
    if name != "urlset":
        return
    for element in root:
        if element.tag.split("}")[-1].lower() != "url":
            continue
        loc = ""
        lastmod = None
        for node in element:
            tag = node.tag.split("}")[-1].lower()
            if tag == "loc":
                loc = (node.text or "").strip()
            elif tag == "lastmod":
                lastmod = parse_date((node.text or "").strip())
        if not loc:
            continue
        if lastmod and lastmod < cutoff:
            old_count[0] += 1
            continue
        url = normalize_url(loc)
        candidates[url] = lastmod.isoformat() if lastmod else None


def fetch_title_date(session: requests.Session, url: str):
    try:
        response = session.get(url, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return None, "", str(exc)
    if not response.ok or "text/html" not in response.headers.get("content-type", ""):
        return None, "", f"HTTP {response.status_code}"
    html = response.text
    published = None
    for pattern in [
        r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
        r'<time[^>]+datetime=["\']([^"\']+)',
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            published = parse_date(match.group(1))
            if published:
                break
    title_match = re.search(r"<title>([^<]+)</title>", html, re.I)
    title = title_match.group(1).strip() if title_match else ""
    return published, title, None


def needs_round2(row: dict) -> bool:
    if row.get("twelve_month_closed") and row.get("collected_count", 0) > 0:
        return False
    return True


def collect_one(session, source, cutoff, existing_urls, delay):
    name = source["name"]
    blog_url = source["url"]
    host = urlparse(blog_url).netloc
    print(f"\n=== R2 {name} ===")
    if "medium.com" in host:
        return [], {
            "company": name,
            "strategy": "skip_medium_sitemap",
            "reason": "Medium 전역 sitemap은 blog_url 밖 URL만 내려줌",
            "sitemap_under_blog": 0,
            "added": 0,
            "closed_by_sitemap": False,
        }

    roots = robots_sitemaps(session, blog_url)
    roots.extend(
        [
            urljoin(blog_url, "/sitemap.xml"),
            urljoin(blog_url, "/wp-sitemap.xml"),
            urljoin(blog_url, "/sitemap_index.xml"),
        ]
    )
    roots = list(dict.fromkeys(roots))
    visited = set()
    raw = {}
    old_count = [0]
    for root in roots:
        parse_sitemap(session, root, cutoff, visited, raw, old_count)
    under = {
        url: lastmod
        for url, lastmod in raw.items()
        if under_blog(url, blog_url) and looks_like_article(url, blog_url)
    }
    print("sitemap under blog", len(under), "outside", len(raw) - len(under), "visited", len(visited))

    added = []
    html_checked = 0
    missing_date = 0
    oldest = None
    for url, lastmod in list(under.items()):
        if url in existing_urls:
            published = parse_date(lastmod)
            if published and (oldest is None or published < oldest):
                oldest = published
            continue
        published = parse_date(lastmod)
        title = ""
        if not published and html_checked < MAX_HTML:
            published, title, error = fetch_title_date(session, url)
            html_checked += 1
            if delay:
                time.sleep(delay)
            if error:
                continue
        if not published:
            missing_date += 1
            continue
        if published < cutoff:
            continue
        if oldest is None or published < oldest:
            oldest = published
        added.append(
            {
                "article_id": article_id(url),
                "company": name,
                "blog_url": blog_url,
                "title": title,
                "published_at": published.isoformat(),
                "url": url,
                "discovered_by": ["sitemap"],
            }
        )
    closed = bool(old_count[0] > 0 or (oldest and oldest <= cutoff and under))
    print("added", len(added), "html", html_checked, "closed", closed)
    return added, {
        "company": name,
        "strategy": "sitemap",
        "root_sitemaps": roots,
        "visited_sitemap_count": len(visited),
        "sitemap_under_blog": len(under),
        "sitemap_outside_blog": len(raw) - len(under),
        "html_checked": html_checked,
        "missing_date": missing_date,
        "added": len(added),
        "oldest": oldest.isoformat() if oldest else None,
        "closed_by_sitemap": closed,
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - relativedelta(months=12)
    sources = {item["name"]: item for item in load_json(COMPANIES_FILE)}
    collect_report = load_json(COLLECT_REPORT)
    articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    round2 = load_json(ROUND2_REPORT) if ROUND2_REPORT.exists() else {"companies": []}
    done = {row["company"] for row in round2.get("companies", [])}

    session = requests.Session()
    session.headers.update(HEADERS)
    reports = [row for row in round2.get("companies", []) if row["company"] in done]

    targets = [
        row
        for row in collect_report["companies"]
        if needs_round2(row) and row["company"] not in done
    ]
    print("round2 대상", len(targets))

    for row in targets:
        source = sources[row["company"]]
        existing = {item["url"] for item in articles if item["company"] == row["company"]}
        try:
            found, report = collect_one(session, source, cutoff, existing, 0.08)
        except Exception as exc:  # noqa: BLE001
            found, report = [], {
                "company": row["company"],
                "strategy": "error",
                "error": str(exc)[:300],
                "added": 0,
                "closed_by_sitemap": False,
            }
            print("실패", row["company"], exc)
        articles.extend(found)
        reports.append(report)
        if report.get("closed_by_sitemap") or found:
            row["collected_count"] = row.get("collected_count", 0) + len(found)
            row["collectable"] = row["collected_count"] > 0
            if report.get("closed_by_sitemap"):
                row["twelve_month_closed"] = True
            row["round2"] = report
        save_json(ARTICLES_FILE, articles)
        save_json(COLLECT_REPORT, collect_report)
        save_json(ROUND2_REPORT, {"generated_at": now.isoformat(), "companies": reports})

    print("round2 완료", len(reports), "총 글", len(articles))


if __name__ == "__main__":
    main()
