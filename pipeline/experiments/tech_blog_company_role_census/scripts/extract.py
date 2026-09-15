"""수집된 글의 본문을 Trafilatura로 뽑는다. 실패해도 메타데이터 분류는 유지한다."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import trafilatura

sys.path.insert(0, str(Path(__file__).parent))
from paths import ARTICLES_FILE, EXTRACT_REPORT, EXTRACTED_FILE

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 15
MIN_LEN = 300


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--companies",
        default="",
        help="쉼표로 구분한 회사명. 비우면 전체",
    )
    args = parser.parse_args()
    names = {name.strip() for name in args.companies.split(",") if name.strip()}

    articles = load_json(ARTICLES_FILE) if ARTICLES_FILE.exists() else []
    if names:
        articles = [item for item in articles if item["company"] in names]
    extracted = load_json(EXTRACTED_FILE) if EXTRACTED_FILE.exists() else []
    done = {item["article_id"] for item in extracted}
    failures = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for index, article in enumerate(articles, start=1):
        if article["article_id"] in done:
            continue
        print(f"[{index}/{len(articles)}] {article['company']} {(article.get('title') or '')[:40]}")
        try:
            response = session.get(article["url"], timeout=TIMEOUT)
            html = response.text if response.ok else None
        except requests.RequestException as exc:
            html = None
            failures.append({"article_id": article["article_id"], "url": article["url"], "reason": str(exc)})
        content = trafilatura.extract(html, include_comments=False, favor_precision=True) if html else None
        content = (content or "").strip()
        if not content:
            failures.append(
                {
                    "article_id": article["article_id"],
                    "url": article["url"],
                    "reason": "content extraction failed",
                }
            )
            continue
        extracted.append(
            {
                **article,
                "content": content,
                "content_length": len(content),
                "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "extraction_quality": "ok" if len(content) >= MIN_LEN else "short",
            }
        )
        done.add(article["article_id"])
        if index % 20 == 0:
            save_json(EXTRACTED_FILE, extracted)
        time.sleep(0.12)

    save_json(EXTRACTED_FILE, extracted)
    save_json(
        EXTRACT_REPORT,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "input_count": len(articles),
            "success_count": len(extracted),
            "failure_count": len(failures),
            "failures": failures,
        },
    )
    print("추출 성공", len(extracted), "실패", len(failures))


if __name__ == "__main__":
    main()
