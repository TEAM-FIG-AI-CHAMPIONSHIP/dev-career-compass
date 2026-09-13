"""과소 집계 unknown을 D2 API / Medium stream / Kakao sitemap으로 보강한다.

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
from urllib.parse import unquote, urljoin, urlparse

import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, COMPANIES_FILE, EXPAND_REPORT
from url_filters import looks_like_article

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15
DELAY = 0.08

D2_API = "https://d2.naver.com/api/v1/contents"
D2_BASE = "https://d2.naver.com"
KAKAO_SITEMAP = "https://tech.kakao.com/sitemap.xml"

MEDIUM_TARGETS = [
    {
        "name": "당근마켓 / 당근",
        "collection_id": "4505f82a2dbd",
        "url_prefix": "https://medium.com/daangn/",
    },
    {
        "name": "위대한상상 / 요기요",
        "collection_id": "c1b33ccbbc42",
        "url_prefix": "https://techblog.yogiyo.co.kr/",
    },
    {
        "name": "딜라이트룸",
        "collection_id": "47cd81ed863",
        "url_prefix": "https://medium.com/delightroom/",
    },
    {
        "name": "SSG.COM",
        "collection_id": "9feb3a520331",
        "url_prefix": "https://medium.com/ssgtech/",
    },
    {
        "name": "미리디",
        "collection_id": "79ed61a9dcb1",
        "url_prefix": "https://medium.com/miridih/",
    },
]


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


def epoch_ms(value):
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (ValueError, TypeError, OSError, OverflowError):
        return None


def clean_title(raw: str) -> str:
    title = re.sub(r"\s+", " ", raw or "").strip()
    for suffix in (" | ", " - ", " — ", " · "):
        if suffix in title:
            title = title.split(suffix)[0].strip()
    return title


def html_title(html: str) -> str:
    for pattern in [
        r'property=["\']og:title["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']',
        r'"headline"\s*:\s*"([^"]+)"',
        r"<title>([^<]+)</title>",
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            title = clean_title(match.group(1))
            if title and title.lower() not in {"medium", "tech.kakao.com"}:
                return title
    return ""


def html_published(html: str):
    for pattern in [
        r'"datePublished"\s*:\s*"([^"]+)"',
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


def update_collect_row(collect_report, name, total_count, closed, extra=None):
    for row in collect_report.get("companies", []):
        if row["company"] != name:
            continue
        row["collected_count"] = total_count
        row["collectable"] = total_count > 0
        if closed:
            row["twelve_month_closed"] = True
        row["expand"] = True
        if extra:
            row["expand_detail"] = extra
        return
    row = {
        "company": name,
        "collected_count": total_count,
        "collectable": total_count > 0,
        "twelve_month_closed": closed,
        "expand": True,
    }
    if extra:
        row["expand_detail"] = extra
    collect_report.setdefault("companies", []).append(row)


def company_count(articles, name):
    return sum(1 for item in articles if item.get("company") == name)


def normalized_path(url: str) -> tuple[str, str, str]:
    parsed = urlparse(unquote(url or ""))
    return (parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query)


def source_rank(item: dict) -> tuple[int, int]:
    discovered = set(item.get("discovered_by") or [])
    preferred = {"d2_api", "medium_stream", "kakao_sitemap", "yogiyo_sitemap"}
    return (1 if discovered & preferred else 0, len((item.get("title") or "").strip()))


def dedupe_articles(articles: list) -> tuple[list, int]:
    best = {}
    order = []
    for item in articles:
        key = (item.get("company"), *normalized_path(item.get("url", "")))
        if key not in best:
            best[key] = item
            order.append(key)
            continue
        if source_rank(item) > source_rank(best[key]):
            best[key] = item
    return [best[key] for key in order], len(articles) - len(best)


def decode_medium(text: str):
    if text.startswith("])}while(1);</x>"):
        text = text[len("])}while(1);</x>") :]
    return json.loads(text)


def collect_d2(session, source, cutoff):
    added = []
    saw_old = False
    pages = 0
    listed = 0
    for page in range(0, 40):
        response = session.get(D2_API, params={"page": page, "size": 30}, timeout=TIMEOUT)
        if not response.ok:
            return added, {
                "strategy": "d2_api",
                "error": f"HTTP {response.status_code}",
                "added": 0,
                "closed": False,
            }
        payload = response.json()
        items = payload.get("content") or []
        pages += 1
        if not items:
            break
        page_old = 0
        for item in items:
            listed += 1
            published = epoch_ms(item.get("postPublishedAt"))
            if not published:
                continue
            if published < cutoff:
                saw_old = True
                page_old += 1
                continue
            url = urljoin(D2_BASE, item.get("url") or "")
            if not url:
                continue
            added.append(
                make_article(
                    source["name"],
                    source["url"],
                    url,
                    clean_title(item.get("postTitle") or ""),
                    published,
                    "d2_api",
                )
            )
        print(f"  d2 page {page} items={len(items)} kept={len(added)} old={page_old}")
        if page_old == len(items):
            break
        time.sleep(DELAY)
    return added, {
        "strategy": "d2_api",
        "pages": pages,
        "listed": listed,
        "added": len(added),
        "closed": saw_old,
    }


def collect_kakao(session, source, cutoff):
    response = session.get(KAKAO_SITEMAP, timeout=TIMEOUT)
    blocks = re.findall(r"<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", response.text)
    lastmod_map = {}
    candidates = []
    sitemap_old = 0
    for loc, lastmod in blocks:
        if "/posts/" not in loc:
            continue
        lastmod_map[loc] = lastmod
        modified = parse_date(lastmod)
        if not modified:
            continue
        if modified < cutoff:
            sitemap_old += 1
            continue
        candidates.append(loc)
    print(f"  kakao sitemap posts lastmod>=12m {len(candidates)} older {sitemap_old}")

    added = []
    saw_old = sitemap_old > 0
    failed = 0
    for index, url in enumerate(candidates, start=1):
        try:
            html_response = session.get(url, timeout=TIMEOUT)
        except requests.RequestException:
            failed += 1
            continue
        if not html_response.ok:
            failed += 1
            continue
        published = html_published(html_response.text) or parse_date(lastmod_map.get(url))
        title = html_title(html_response.text)
        if not published:
            failed += 1
            continue
        if published < cutoff:
            saw_old = True
            continue
        added.append(
            make_article(source["name"], source["url"], url, title, published, "kakao_sitemap")
        )
        if index % 20 == 0:
            print(f"  kakao {index}/{len(candidates)} kept={len(added)}")
        time.sleep(DELAY)
    return added, {
        "strategy": "kakao_sitemap_html",
        "candidates": len(candidates),
        "added": len(added),
        "failed": failed,
        "closed": saw_old,
    }


def collect_medium_stream(session, source, cutoff, collection_id, url_prefix):
    added = []
    seen = set()
    saw_old = False
    to = None
    page = 1
    ignored = []
    pages = 0
    for _ in range(25):
        params = {}
        if to:
            params["to"] = to
            params["page"] = page
            for index, item_id in enumerate(ignored):
                params[f"ignoredIds[{index}]"] = item_id
        response = session.get(
            f"https://medium.com/_/api/collections/{collection_id}/stream",
            params=params,
            timeout=TIMEOUT,
        )
        if not response.ok:
            break
        try:
            payload = decode_medium(response.text).get("payload") or {}
        except ValueError:
            break
        posts = ((payload.get("references") or {}).get("Post") or {})
        pages += 1
        page_new = 0
        page_old = 0
        for post_id, post in posts.items():
            if post_id in seen:
                continue
            seen.add(post_id)
            published = epoch_ms(post.get("firstPublishedAt"))
            slug = post.get("uniqueSlug") or ""
            title = clean_title(post.get("title") or "")
            url = urljoin(url_prefix, slug)
            if not published or not slug:
                continue
            if published < cutoff:
                saw_old = True
                page_old += 1
                continue
            added.append(
                make_article(source["name"], source["url"], url, title, published, "medium_stream")
            )
            page_new += 1
        nxt = (payload.get("paging") or {}).get("next") or {}
        print(
            f"  medium {source['name']} page={page} posts={len(posts)} "
            f"new={page_new} old={page_old} kept={len(added)}"
        )
        if not nxt:
            break
        to = nxt.get("to")
        page = nxt.get("page", page + 1)
        ignored = nxt.get("ignoredIds") or []
        if pages > 1 and page_new == 0 and page_old == 0 and not posts:
            break
        time.sleep(DELAY)
    return added, {
        "strategy": "medium_stream",
        "collection_id": collection_id,
        "pages": pages,
        "seen": len(seen),
        "added": len(added),
        "closed": saw_old,
    }


def collect_lg_ai(session, source, cutoff):
    response = session.get("https://www.lgresearch.ai/sitemap.xml", timeout=TIMEOUT)
    locs = re.findall(r"<loc>([^<]+)</loc>", response.text)
    targets = [loc for loc in locs if "/blog/view" in loc and "seq=" in loc]
    print(f"  lg ai sitemap blog/view {len(targets)}")
    added = []
    saw_old = False
    failed = 0
    for index, url in enumerate(targets, start=1):
        try:
            html_response = session.get(url, timeout=TIMEOUT)
        except requests.RequestException:
            failed += 1
            continue
        if not html_response.ok:
            failed += 1
            continue
        published = html_published(html_response.text)
        title = html_title(html_response.text)
        if not published:
            failed += 1
            continue
        if published < cutoff:
            saw_old = True
            continue
        added.append(
            make_article(source["name"], source["url"], url, title, published, "lg_ai_sitemap")
        )
        if index % 40 == 0:
            print(f"  lg ai {index}/{len(targets)} kept={len(added)} old={saw_old}")
        time.sleep(DELAY)
    return added, {
        "strategy": "lg_ai_sitemap_html",
        "targets": len(targets),
        "added": len(added),
        "failed": failed,
        "closed": saw_old,
    }


def collect_yogiyo_sitemap(session, source, cutoff, already_urls):
    response = session.get("https://techblog.yogiyo.co.kr/sitemap/sitemap.xml", timeout=TIMEOUT)
    locs = re.findall(r"<loc>([^<]+)</loc>", response.text)
    lastmods = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", response.text))
    targets = []
    for loc in locs:
        if "/tagged/" in loc:
            continue
        path = urlparse(loc).path.strip("/")
        if not path or not looks_like_article(loc, source["url"]):
            continue
        if loc in already_urls:
            continue
        targets.append(loc)
    added = []
    saw_old = False
    for index, url in enumerate(targets, start=1):
        try:
            html_response = session.get(url, timeout=TIMEOUT)
        except requests.RequestException:
            continue
        if not html_response.ok:
            continue
        published = html_published(html_response.text) or parse_date(lastmods.get(url))
        title = html_title(html_response.text)
        if not published:
            continue
        if published < cutoff:
            saw_old = True
            continue
        added.append(
            make_article(source["name"], source["url"], url, title, published, "yogiyo_sitemap")
        )
        if index % 20 == 0:
            print(f"  yogiyo sitemap {index}/{len(targets)} kept={len(added)}")
        time.sleep(DELAY)
    return added, {
        "strategy": "yogiyo_sitemap_leftover",
        "targets": len(targets),
        "added": len(added),
        "closed": saw_old,
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - relativedelta(months=12)
    sources = {item["name"]: item for item in load_json(COMPANIES_FILE)}
    articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    collect_report = load_json(COLLECT_REPORT) if COLLECT_REPORT.exists() else {"companies": []}
    session = requests.Session()
    session.headers.update(HEADERS)
    reports = []

    print("\n=== 네이버 D2 ===")
    found, report = collect_d2(session, sources["네이버"], cutoff)
    added = merge_articles(articles, found)
    report.update({"company": "네이버", "merged": len(added)})
    update_collect_row(
        collect_report,
        "네이버",
        company_count(articles, "네이버"),
        report["closed"],
        report,
    )
    print("merged", len(added), "closed", report["closed"], "total", company_count(articles, "네이버"))
    reports.append(report)
    save_json(ARTICLES_FILE, articles)
    save_json(COLLECT_REPORT, collect_report)

    print("\n=== 카카오 ===")
    found, report = collect_kakao(session, sources["카카오"], cutoff)
    added = merge_articles(articles, found)
    report.update({"company": "카카오", "merged": len(added)})
    update_collect_row(
        collect_report,
        "카카오",
        company_count(articles, "카카오"),
        report["closed"],
        report,
    )
    print("merged", len(added), "closed", report["closed"], "total", company_count(articles, "카카오"))
    reports.append(report)
    save_json(ARTICLES_FILE, articles)
    save_json(COLLECT_REPORT, collect_report)

    for target in MEDIUM_TARGETS:
        name = target["name"]
        print("\n===", name, "medium stream ===")
        found, report = collect_medium_stream(
            session,
            sources[name],
            cutoff,
            target["collection_id"],
            target["url_prefix"],
        )
        added = merge_articles(articles, found)
        report.update({"company": name, "merged": len(added)})
        update_collect_row(
            collect_report,
            name,
            company_count(articles, name),
            report["closed"],
            report,
        )
        print("merged", len(added), "closed", report["closed"], "total", company_count(articles, name))
        reports.append(report)
        save_json(ARTICLES_FILE, articles)
        save_json(COLLECT_REPORT, collect_report)

    print("\n=== LG AI연구원 ===")
    found, report = collect_lg_ai(session, sources["LG AI연구원"], cutoff)
    added = merge_articles(articles, found)
    report.update({"company": "LG AI연구원", "merged": len(added)})
    update_collect_row(
        collect_report,
        "LG AI연구원",
        company_count(articles, "LG AI연구원"),
        report["closed"],
        report,
    )
    print("merged", len(added), "closed", report["closed"], "total", company_count(articles, "LG AI연구원"))
    reports.append(report)
    save_json(ARTICLES_FILE, articles)
    save_json(COLLECT_REPORT, collect_report)

    print("\n=== 요기요 sitemap leftover ===")
    already = {item["url"] for item in articles if item.get("company") == "위대한상상 / 요기요"}
    found, report = collect_yogiyo_sitemap(session, sources["위대한상상 / 요기요"], cutoff, already)
    added = merge_articles(articles, found)
    closed = report["closed"] or any(
        row.get("expand_detail", {}).get("closed")
        for row in collect_report.get("companies", [])
        if row.get("company") == "위대한상상 / 요기요"
    )
    report.update({"company": "위대한상상 / 요기요", "merged": len(added)})
    update_collect_row(
        collect_report,
        "위대한상상 / 요기요",
        company_count(articles, "위대한상상 / 요기요"),
        closed,
        report,
    )
    print("merged", len(added), "closed", closed, "total", company_count(articles, "위대한상상 / 요기요"))
    reports.append(report)
    save_json(ARTICLES_FILE, articles)
    save_json(COLLECT_REPORT, collect_report)

    articles, dropped = dedupe_articles(articles)
    print("중복 경로 제거", dropped, "남김", len(articles))
    counts = {}
    for item in articles:
        counts[item["company"]] = counts.get(item["company"], 0) + 1
    for row in collect_report.get("companies", []):
        if row["company"] in counts:
            row["collected_count"] = counts[row["company"]]
            row["collectable"] = row["collected_count"] > 0
    save_json(ARTICLES_FILE, articles)
    save_json(COLLECT_REPORT, collect_report)
    save_json(EXPAND_REPORT, {"generated_at": now.isoformat(), "dropped_duplicate_paths": dropped, "companies": reports})
    print("expand 완료", len(articles))


if __name__ == "__main__":
    main()
