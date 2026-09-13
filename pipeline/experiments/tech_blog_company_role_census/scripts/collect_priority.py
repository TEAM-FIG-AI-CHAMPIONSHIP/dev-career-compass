"""제품 가치가 높은 unknown 7곳을 archive/custom으로 보강한다.

게이트(직무당 기술글 8개)는 바꾸지 않는다. 모이지 않으면 pass를 주지 않는다.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, COMPANIES_FILE, PRIORITY_REPORT

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15
DELAY = 0.08

PRIORITY = [
    "우아한형제들 / 배달의민족",
    "카카오뱅크",
    "카카오페이",
    "카카오모빌리티",
    "무신사 / 29CM",
    "여기어때",
    "위대한상상 / 요기요",
]
MEDIUM_TITLES = {"", "medium"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def clean_title(raw: str) -> str:
    title = re.sub(r"\s+", " ", raw or "").strip()
    for suffix in (" | ", " - ", " — ", " · "):
        if suffix in title:
            title = title.split(suffix)[0].strip()
    return title


def title_from_slug(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1]
    slug = re.sub(r"-[0-9a-f]{8,}$", "", slug, flags=re.I)
    title = slug.replace("-", " ").strip()
    return title if len(title) >= 8 else ""


def html_title(html: str) -> str:
    for pattern in [
        r'property=["\']og:title["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']',
        r"<title>([^<]+)</title>",
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            title = clean_title(match.group(1))
            if title.lower() not in MEDIUM_TITLES:
                return title
    return ""


def html_published(html: str):
    for pattern in [
        r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time["\']',
        r'<time[^>]+datetime=["\']([^"\']+)',
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            published = parse_date(match.group(1))
            if published:
                return published
    return None


def make_article(name, blog_url, url, title, published, source):
    return {
        "article_id": article_id(url),
        "company": name,
        "blog_url": blog_url,
        "title": title or "",
        "published_at": published.isoformat(),
        "url": url,
        "discovered_by": [source],
    }


def collect_kakaobank(session, source, cutoff):
    blog_url = source["url"]
    response = session.get(urljoin(blog_url, "/index.xml"), timeout=TIMEOUT)
    parsed = feedparser.parse(response.content)
    added = []
    oldest = None
    saw_old = False
    for entry in parsed.entries:
        published = parse_date(entry.get("published") or entry.get("updated"))
        if not published:
            continue
        if oldest is None or published < oldest:
            oldest = published
        if published < cutoff:
            saw_old = True
            continue
        link = urljoin(blog_url, entry.get("link") or "")
        added.append(
            make_article(source["name"], blog_url, link, entry.get("title") or "", published, "kakaobank_xml")
        )
    return added, {"strategy": "index.xml", "feed_entries": len(parsed.entries), "added": len(added), "closed": saw_old}


def collect_kakaopay(session, source, cutoff):
    blog_url = source["url"]
    added = []
    seen = set()
    saw_old = False
    for page in range(1, 40):
        url = blog_url if page == 1 else urljoin(blog_url, f"/page/{page}")
        response = session.get(url, timeout=TIMEOUT)
        if not response.ok:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("a[href*='/post/']")
        page_new = 0
        for anchor in cards:
            href = urljoin(blog_url, anchor.get("href", ""))
            if href in seen or "/tag/" in href:
                continue
            seen.add(href)
            published = None
            parent = anchor.parent
            for _ in range(4):
                if parent is None:
                    break
                time_tag = parent.find("time")
                if time_tag:
                    published = parse_date(time_tag.get("datetime") or time_tag.get_text())
                    if published:
                        break
                parent = parent.parent
            title = clean_title(anchor.get_text(" ", strip=True))
            if not published:
                continue
            if published < cutoff:
                saw_old = True
                continue
            added.append(make_article(source["name"], blog_url, href, title, published, "kakaopay_pages"))
            page_new += 1
        print("  pay page", page, "new", page_new, "seen", len(seen))
        if page > 1 and page_new == 0 and saw_old:
            break
        time.sleep(DELAY)
    return added, {"strategy": "listing_pages", "pages": page, "added": len(added), "closed": saw_old}


def collect_kakaomobility(session, source, cutoff):
    blog_url = source["url"]
    response = session.get(blog_url, timeout=TIMEOUT)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(blog_url, anchor["href"])
        path = urlparse(href).path
        if path.startswith("/techblogs/") and path.endswith(".html") and path != "/techblogs/":
            links.append(href)
    links = list(dict.fromkeys(links))
    added = []
    saw_old = False
    for url in links:
        html_response = session.get(url, timeout=TIMEOUT)
        time.sleep(DELAY)
        if not html_response.ok:
            continue
        published = html_published(html_response.text)
        title = html_title(html_response.text)
        if not published:
            continue
        if published < cutoff:
            saw_old = True
            continue
        added.append(make_article(source["name"], blog_url, url, title, published, "kakaomobility_listing"))
    return added, {
        "strategy": "listing_html",
        "listing_links": len(links),
        "added": len(added),
        "closed": saw_old,
    }


def collect_woowahan(session, source, cutoff):
    blog_url = source["url"]
    try:
        response = session.get(blog_url, timeout=TIMEOUT)
        status = response.status_code
    except requests.RequestException as exc:
        return [], {"strategy": "blocked", "error": str(exc), "added": 0, "closed": False}
    return [], {
        "strategy": "blocked",
        "http": status,
        "reason": "HTML/RSS/sitemap/wp-json 모두 403. custom 브라우저 우회는 하지 않음",
        "added": 0,
        "closed": False,
    }


def refresh_medium_titles(session, articles, names):
    targets = [
        item
        for item in articles
        if item["company"] in names and (item.get("title") or "").strip().lower() in MEDIUM_TITLES
    ]
    filled = 0
    for index, article in enumerate(targets, start=1):
        try:
            response = session.get(article["url"], timeout=TIMEOUT)
        except requests.RequestException:
            continue
        title = html_title(response.text) if response.ok else ""
        if not title:
            title = title_from_slug(article["url"])
        if not title:
            print(f"  medium fail {article['company']} {article['url'][-50:]}")
            continue
        article["title"] = title
        article.setdefault("discovered_by", []).append("priority_title")
        filled += 1
        print(f"  medium {index}/{len(targets)} {title[:50]}")
        if index % 20 == 0:
            save_json(ARTICLES_FILE, articles)
        time.sleep(DELAY)
    return filled, len(targets)


def merge_articles(articles, found):
    existing = {item["url"] for item in articles}
    added = []
    for item in found:
        if item["url"] in existing:
            continue
        articles.append(item)
        existing.add(item["url"])
        added.append(item)
    return added


def update_collect_row(collect_report, name, added_count, closed):
    for row in collect_report.get("companies", []):
        if row["company"] != name:
            continue
        row["collected_count"] = row.get("collected_count", 0) + added_count
        row["collectable"] = row["collected_count"] > 0
        if closed:
            row["twelve_month_closed"] = True
        row["priority"] = True
        return


def main() -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - relativedelta(months=12)
    sources = {item["name"]: item for item in load_json(COMPANIES_FILE)}
    articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    collect_report = load_json(COLLECT_REPORT) if COLLECT_REPORT.exists() else {"companies": []}
    session = requests.Session()
    session.headers.update(HEADERS)
    reports = []

    collectors = {
        "카카오뱅크": collect_kakaobank,
        "카카오페이": collect_kakaopay,
        "카카오모빌리티": collect_kakaomobility,
        "우아한형제들 / 배달의민족": collect_woowahan,
    }

    for name in PRIORITY:
        print("\n===", name, "===")
        source = sources[name]
        if name in collectors:
            found, report = collectors[name](session, source, cutoff)
            added = merge_articles(articles, found)
            report["company"] = name
            report["merged"] = len(added)
            update_collect_row(collect_report, name, len(added), report.get("closed", False))
            print("added", len(added), "closed", report.get("closed"))
            reports.append(report)
            save_json(ARTICLES_FILE, articles)
            save_json(COLLECT_REPORT, collect_report)

    medium_names = ["무신사 / 29CM", "여기어때", "위대한상상 / 요기요"]
    filled, targets = refresh_medium_titles(session, articles, medium_names)
    save_json(ARTICLES_FILE, articles)
    reports.append({"company": "medium_title_refresh", "targets": targets, "filled": filled})
    print("medium titles", filled, "/", targets)

    save_json(PRIORITY_REPORT, {"generated_at": now.isoformat(), "companies": reports})
    print("priority 완료", len(articles))


if __name__ == "__main__":
    main()
