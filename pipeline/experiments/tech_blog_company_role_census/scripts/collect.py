"""111개 기술블로그에서 최근 12개월 메타데이터를 모은다. RSS 우선, 부족하면 sitemap."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import feedparser
import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, COMPANIES_FILE

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 12


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_url(url: str) -> str:
    url, _ = urldefrag(url.strip())
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


def rss_candidates(source: dict) -> list[str]:
    blog_url = source["url"]
    parsed = urlparse(blog_url)
    host = parsed.netloc
    path = parsed.path.rstrip("/")
    candidates = []
    if source.get("rss_url"):
        candidates.append(source["rss_url"])
    if "medium.com" in host:
        pub = path.split("/")[1] if path.count("/") >= 1 else ""
        if pub:
            candidates.append(f"https://medium.com/feed/{pub}")
    if host.endswith("tistory.com"):
        candidates.append(urljoin(blog_url, "/rss"))
    candidates.extend(
        [
            urljoin(blog_url, "/feed/"),
            urljoin(blog_url, "/rss.xml"),
            urljoin(blog_url, "/feed.xml"),
            urljoin(blog_url, "/atom.xml"),
            urljoin(blog_url, "/rss"),
            urljoin(f"{parsed.scheme}://{host}/", "d2.atom"),
        ]
    )
    return list(dict.fromkeys(candidates))


def collect_rss(session: requests.Session, source: dict, cutoff) -> tuple[dict, dict]:
    articles = {}
    working = None
    entry_count = 0
    oldest = None
    for rss_url in rss_candidates(source):
        try:
            response = session.get(rss_url, timeout=TIMEOUT)
        except requests.RequestException:
            continue
        if not response.ok:
            continue
        feed = feedparser.parse(response.content)
        if not feed.entries:
            continue
        working = rss_url
        entry_count = len(feed.entries)
        for entry in feed.entries:
            url = normalize_url(entry.get("link") or "")
            if not url:
                continue
            published = parse_date(entry.get("published") or entry.get("updated"))
            if published and (oldest is None or published < oldest):
                oldest = published
            if published and published < cutoff:
                continue
            articles[url] = {
                "url": url,
                "title": (entry.get("title") or "").strip(),
                "published_at": published.isoformat() if published else None,
                "discovered_by": ["rss"],
            }
        break
    coverage = "unknown"
    if working and oldest:
        coverage = "likely_sufficient" if oldest <= cutoff else "insufficient"
    elif working:
        coverage = "no_dates"
    return articles, {
        "rss_url": working,
        "entry_count": entry_count,
        "recent_count": len(articles),
        "oldest": oldest.isoformat() if oldest else None,
        "coverage": coverage,
    }


def collect_company(session: requests.Session, source: dict, cutoff, delay: float):
    name = source["name"]
    print(f"\n=== {name} ===")
    articles, rss_report = collect_rss(session, source, cutoff)
    print("RSS", rss_report["coverage"], rss_report["recent_count"], rss_report.get("rss_url"))
    if delay:
        time.sleep(delay)
    kept = []
    missing_date = 0
    for url, item in articles.items():
        published = parse_date(item.get("published_at"))
        if not published:
            missing_date += 1
            continue
        if published < cutoff:
            continue
        kept.append(
            {
                "article_id": article_id(url),
                "company": name,
                "blog_url": source["url"],
                "title": item["title"],
                "published_at": published.isoformat(),
                "url": url,
                "discovered_by": item["discovered_by"],
            }
        )
    kept.sort(key=lambda a: a["published_at"], reverse=True)
    report = {
        "company": name,
        "blog_url": source["url"],
        "rss": rss_report,
        "collected_count": len(kept),
        "missing_date": missing_date,
        "collectable": len(kept) > 0,
        "twelve_month_closed": rss_report["coverage"] == "likely_sufficient",
    }
    print("12개월 확정", len(kept), "closed", report["twelve_month_closed"])
    return kept, report


def main() -> None:
    months = 12
    delay = 0.1
    now = datetime.now(timezone.utc)
    cutoff = now - relativedelta(months=months)
    sources = load_json(COMPANIES_FILE)
    session = requests.Session()
    session.headers.update(HEADERS)

    existing_articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    existing_report = load_json(COLLECT_REPORT) if COLLECT_REPORT.exists() else {"companies": []}
    done = {row["company"] for row in existing_report.get("companies", [])}
    articles = [a for a in existing_articles if a["company"] in done]
    reports = [row for row in existing_report.get("companies", []) if row["company"] in done]

    for source in sources:
        if source["name"] in done:
            continue
        try:
            found, report = collect_company(session, source, cutoff, delay)
        except Exception as exc:  # noqa: BLE001 — 한 회사 실패가 전수를 멈추면 안 됨
            found, report = [], {
                "company": source["name"],
                "blog_url": source["url"],
                "error": str(exc)[:300],
                "collected_count": 0,
                "collectable": False,
                "twelve_month_closed": False,
            }
            print("실패", source["name"], exc)
        articles.extend(found)
        reports.append(report)
        save_json(ARTICLES_FILE, articles)
        save_json(
            COLLECT_REPORT,
            {"generated_at": now.isoformat(), "months": months, "companies": reports},
        )

    print("총 게시글", len(articles), "회사", len(reports))


if __name__ == "__main__":
    main()
