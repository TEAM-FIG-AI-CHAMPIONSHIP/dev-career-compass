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
from paths import ARTICLES_FILE, TITLE_BACKFILL_REPORT

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 12
DELAY = 0.08


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def html_title(html: str) -> str:
    match = re.search(r"<title>([^<]+)</title>", html, re.I)
    if not match:
        return ""
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    for suffix in (" | ", " - ", " — ", " · "):
        if suffix in title:
            title = title.split(suffix)[0].strip()
    return title


def main() -> None:
    articles = load_json(ARTICLES_FILE)
    targets = [item for item in articles if not (item.get("title") or "").strip()]
    print("빈 제목", len(targets), "/", len(articles))

    session = requests.Session()
    session.headers.update(HEADERS)
    filled = 0
    failures = []

    for index, article in enumerate(targets, start=1):
        try:
            response = session.get(article["url"], timeout=TIMEOUT)
        except requests.RequestException as exc:
            failures.append({"article_id": article["article_id"], "url": article["url"], "reason": str(exc)})
            continue
        if not response.ok:
            failures.append(
                {
                    "article_id": article["article_id"],
                    "url": article["url"],
                    "reason": f"HTTP {response.status_code}",
                }
            )
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
            continue
        article["title"] = title
        article.setdefault("discovered_by", [])
        if "title_backfill" not in article["discovered_by"]:
            article["discovered_by"].append("title_backfill")
        filled += 1
        print(f"[{index}/{len(targets)}] {article['company']} {title[:60]}")
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
