"""sitemap lastmod만으로 넣은 글의 빈 제목을 HTML에서 채운다.

제목이 없으면 classify가 전부 non-tech로 떨어져 게이트가 과소 집계된다.
본문 추출은 extract.py가 이어서 한다.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, COLLECT_REPORT, TITLE_BACKFILL_REPORT
from url_filters import looks_like_article

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = (5, 12)
DELAY = 0.08


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_title(raw: str) -> str:
    title = re.sub(r"\s+", " ", raw).strip()
    for suffix in (" | ", " - ", " — ", " · "):
        if suffix in title:
            title = title.split(suffix)[0].strip()
    return title


def html_title(html: str) -> str:
    for pattern in [
        r'property=["\']og:title["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']',
        r"<title>([^<]+)</title>",
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            title = clean_title(match.group(1))
            if title:
                return title
    return ""


def main() -> None:
    raw_articles = load_json(ARTICLES_FILE)
    articles = [item for item in raw_articles if looks_like_article(item["url"], item.get("blog_url", ""))]
    dropped = len(raw_articles) - len(articles)
    targets = [item for item in articles if not (item.get("title") or "").strip()]
    print("목록 URL 제외", dropped, "남김", len(articles), "빈 제목", len(targets), flush=True)
    save_json(ARTICLES_FILE, articles)
    if COLLECT_REPORT.exists():
        collect_report = load_json(COLLECT_REPORT)
        counts = {}
        for item in articles:
            counts[item["company"]] = counts.get(item["company"], 0) + 1
        for row in collect_report.get("companies", []):
            row["collected_count"] = counts.get(row["company"], 0)
            row["collectable"] = row["collected_count"] > 0
        save_json(COLLECT_REPORT, collect_report)

    session = requests.Session()
    session.headers.update(HEADERS)
    filled = 0
    failures = []

    for index, article in enumerate(targets, start=1):
        print(f"[{index}/{len(targets)}] {article['company']}", flush=True)
        try:
            response = session.get(article["url"], timeout=TIMEOUT)
        except requests.RequestException as exc:
            failures.append({"article_id": article["article_id"], "url": article["url"], "reason": str(exc)})
            print("    fail", exc, flush=True)
            continue
        if not response.ok:
            failures.append(
                {
                    "article_id": article["article_id"],
                    "url": article["url"],
                    "reason": f"HTTP {response.status_code}",
                }
            )
            print("    fail", f"HTTP {response.status_code}", flush=True)
            continue
        title = html_title(response.text)
        if not title:
            failures.append(
                {
                    "article_id": article["article_id"],
                    "url": article["url"],
                    "reason": "title missing",
                }
            )
            print("    fail title missing", flush=True)
            continue
        article["title"] = title
        article.setdefault("discovered_by", [])
        if "title_backfill" not in article["discovered_by"]:
            article["discovered_by"].append("title_backfill")
        filled += 1
        print(f"    ok {title[:60]}", flush=True)
        if index % 20 == 0:
            save_json(ARTICLES_FILE, articles)
        time.sleep(DELAY)

    save_json(ARTICLES_FILE, articles)
    save_json(
        TITLE_BACKFILL_REPORT,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "empty_before": len(targets),
            "filled": filled,
            "failed": len(failures),
            "failures": failures[:200],
        },
    )
    print("채움", filled, "실패", len(failures))


if __name__ == "__main__":
    main()
