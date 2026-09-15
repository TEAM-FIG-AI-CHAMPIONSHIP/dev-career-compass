"""당근(Medium) 재작업용 — Wayback Machine 아카이브를 통해 본문을 확보한다.

배경: medium.com/daangn 개별 글 페이지를 직접 요청하면 Cloudflare
봇 차단(403)에 상당수 걸린다(직접 확인함, 4건 중 3건 실패). RSS는
최근 10건만 준다. 반면 Wayback Machine(web.archive.org)에 저장된
사본은 Cloudflare를 거치지 않고 archive.org 서버에서 직접 받아올 수
있어 안정적으로 본문을 확보할 수 있다.

절차:
1. Wayback CDX API로 medium.com/daangn/* 전체 크롤 이력을 가져온다
   (쿼리 파라미터가 다른 같은 글은 canonical URL 기준으로 묶는다).
2. 각 글의 최신 스냅샷을 Wayback에서 원본 HTML 그대로(`id_` 모드,
   Wayback 툴바 미주입) 받아온다.
3. 페이지에 실제로 표시되는 byline 날짜("Apr 15, 2024" 형식)를
   파싱한다 — meta article:published_time은 이 글에서 실제로
   확인해보니 재편집 시각과 섞여 있어 신뢰할 수 없었다(예: 본문
   byline은 2024-04-15인데 meta는 2025-05-15로 다름). 화면에 실제
   보이는 날짜가 진짜 발행일이라고 판단해 그쪽을 쓴다.
4. 12개월 cutoff를 여기서 직접 적용한다(census 표준 cutoff와 동일
   기준). extract_engineering_focus.py의 cutoff는 이후 병합
   단계에서 다시 한번 적용되므로 이중 필터링이지만 안전한 쪽이다.

이 스크립트는 당근 재작업 전용 1회성 백필이다. 다른 회사에는
재사용하지 않는다(회사마다 차단 양상이 달라 일반화 위험).
"""

import functools
import hashlib
import json
import re
import socket
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

print = functools.partial(print, flush=True)  # noqa: A001

# requests의 timeout 파라미터는 소켓 connect/read만 보장하고, DNS
# 조회 단계가 무한정 걸리는 경우를 막지 못할 때가 있었다(실제로
# archive.org 요청 하나가 CPU 0%, 네트워크 연결 없이 9분 넘게
# 멈춰 있는 걸 확인함). 프로세스 전역 소켓 타임아웃을 걸어서
# DNS 단계까지 포함해 강제로 끊어지게 한다.
socket.setdefaulttimeout(45)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
    / "daangn_wayback"
)

CDX_CACHE_FILE = OUTPUT_DIR / "cdx_urls_cache.json"

OUTPUT_FILE = OUTPUT_DIR / "articles.json"

FAILED_FILE = OUTPUT_DIR / "failed.json"

# url -> 처리 결과 기록. 중간에 프로세스가 멈춰도(archive.org DNS
# 행 등) 이미 처리한 URL은 다시 안 긁도록 재개 지점으로 쓴다.
PROGRESS_FILE = OUTPUT_DIR / "progress.json"

SAVE_EVERY = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 30

REQUEST_DELAY_SECONDS = 0.5

COVERAGE_MONTHS = 12

MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
)

BYLINE_DATE_PATTERN = re.compile(
    r"(" + "|".join(MONTH_NAMES) + r")\s+(\d{1,2}),\s+(\d{4})"
)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_cdx_urls():
    if CDX_CACHE_FILE.exists():
        print(f"CDX 캐시 재사용: {CDX_CACHE_FILE}")

        return json.loads(CDX_CACHE_FILE.read_text(encoding="utf-8"))

    params = {
        "url": "medium.com/daangn/*",
        "output": "json",
        "filter": "statuscode:200",
        "fl": "original,timestamp"
    }

    last_error = None

    for attempt in range(5):
        try:
            r = requests.get(
                "https://web.archive.org/cdx/search/cdx",
                params=params,
                headers=HEADERS,
                timeout=60
            )

            r.raise_for_status()

            rows = json.loads(r.text)[1:]

            break

        except requests.RequestException as error:
            last_error = error

            print(
                f"CDX 요청 실패(시도 {attempt + 1}/5): {error} "
                f"-- {10 * (attempt + 1)}초 후 재시도"
            )

            time.sleep(10 * (attempt + 1))

    else:
        raise last_error

    canonical = {}

    for original, timestamp in rows:
        base = original.split("?")[0].rstrip("/")

        path = urlparse(base).path

        if not is_real_article_path(path):
            continue

        if base not in canonical or timestamp > canonical[base]:
            canonical[base] = timestamp

    save_json(CDX_CACHE_FILE, canonical)

    return canonical


# Medium 글 URL은 마지막 경로 조각이 6~16자리 hex id로 끝난다
# (예: ".../mvp를-빠르고-dc481bd03b88"). 이 패턴이 없는 건 태그
# 페이지, 홈, 다른 사람 프로필 도메인 크로스링크 같은 글이 아닌
# 경로라 후보에서 제외한다.
ARTICLE_ID_SUFFIX = re.compile(r"-?[0-9a-f]{6,16}$")

JUNK_PATH_SEGMENTS = (
    "home", "tagged", "subpage", "latest", "archive",
    "search-home", "working", "startup", "marketing",
    "machine-learning"
)


def is_real_article_path(path):
    segments = [s for s in path.split("/") if s]

    if len(segments) < 2:
        return False

    if any(s in JUNK_PATH_SEGMENTS for s in segments):
        return False

    last = segments[-1]

    if "." in last:
        return False

    if not ARTICLE_ID_SUFFIX.search(last):
        return False

    return True


def parse_byline_date(soup):
    text = soup.get_text(" ", strip=True)

    match = BYLINE_DATE_PATTERN.search(text)

    if not match:
        return None

    month_str, day_str, year_str = match.groups()

    month = MONTH_NAMES.index(month_str) + 1

    try:
        return datetime(
            int(year_str), month, int(day_str),
            tzinfo=timezone.utc
        ).date()
    except ValueError:
        return None


def fetch_snapshot(original_url, timestamp):
    wayback_url = (
        f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    )

    r = None

    for attempt in range(5):
        try:
            r = requests.get(
                wayback_url, headers=HEADERS, timeout=TIMEOUT
            )

        except requests.RequestException:
            time.sleep(15 * (attempt + 1))

            continue

        if r.status_code != 503:
            break

        time.sleep(5 * (attempt + 1))

    if r is None or r.status_code != 200:
        return None

    soup = BeautifulSoup(r.content, "html.parser")

    article = soup.find("article")

    if not article:
        return None

    title_meta = soup.find("meta", {"property": "og:title"})
    title = title_meta.get("content") if title_meta else None

    if not title:
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

    content = article.get_text(" ", strip=True)

    published_date = parse_byline_date(article) or parse_byline_date(soup)

    date_source = "byline"

    if not published_date:
        meta_pub = soup.find(
            "meta", {"property": "article:published_time"}
        )

        if meta_pub and meta_pub.get("content"):
            try:
                published_date = datetime.fromisoformat(
                    meta_pub["content"].replace("Z", "+00:00")
                ).date()

                date_source = "meta_published_time"

            except ValueError:
                published_date = None

    return {
        "title": title,
        "content": content,
        "published_date": published_date,
        "date_source": date_source
    }


def load_progress():
    if not PROGRESS_FILE.exists():
        return {}, [], []

    progress = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))

    articles = progress.get("articles", [])
    failed = progress.get("failed", [])
    done_urls = progress.get("done_urls", [])

    return {u: True for u in done_urls}, articles, failed


def save_progress(done_urls, articles, failed):
    save_json(
        PROGRESS_FILE,
        {
            "done_urls": list(done_urls),
            "articles": articles,
            "failed": failed
        }
    )

    save_json(OUTPUT_FILE, articles)
    save_json(FAILED_FILE, failed)


def main():
    print("Wayback CDX에서 당근 글 목록 수집 중...")

    canonical = fetch_cdx_urls()

    print(f"canonical article 후보: {len(canonical)}건")

    cutoff = (
        datetime.now(timezone.utc) - relativedelta(months=COVERAGE_MONTHS)
    ).date()

    print(f"12개월 cutoff: {cutoff} 이후만 채택")

    done, articles, failed = load_progress()

    if done:
        print(f"이전 진행 상황 재개: {len(done)}건 이미 처리됨")

    items = sorted(canonical.items())

    remaining = [
        (url, ts) for url, ts in items if url not in done
    ]

    print(f"이번에 처리할 건: {len(remaining)}건")

    since_save = 0

    for index, (url, timestamp) in enumerate(remaining, start=1):
        print(
            f"[{index}/{len(remaining)}] {url[:70]}",
            end=" "
        )

        try:
            result = fetch_snapshot(url, timestamp)
        except requests.RequestException as error:
            print("ERROR", error)
            failed.append({"url": url, "reason": str(error)})
            done[url] = True
            since_save += 1
            time.sleep(REQUEST_DELAY_SECONDS)

        else:
            if not result:
                print("스냅샷 없음/파싱 실패")
                failed.append(
                    {"url": url, "reason": "no_snapshot_or_no_article_tag"}
                )

            elif not result["published_date"]:
                print("날짜 파싱 실패")
                failed.append({"url": url, "reason": "date_parse_failed"})

            elif result["published_date"] < cutoff:
                print(f"제외(12개월 밖, {result['published_date']})")

            else:
                article_id = hashlib.sha256(
                    url.encode("utf-8")
                ).hexdigest()[:16]

                articles.append({
                    "article_id": article_id,
                    "company": "당근마켓 / 당근",
                    "title": result["title"],
                    "url": url,
                    "published_at": result["published_date"].isoformat(),
                    "date_source": result["date_source"],
                    "content": result["content"]
                })

                print(
                    f"OK ({result['published_date']}, "
                    f"{result['date_source']}, "
                    f"{len(result['content'])}자)"
                )

            done[url] = True
            since_save += 1
            time.sleep(REQUEST_DELAY_SECONDS)

        if since_save >= SAVE_EVERY:
            save_progress(done.keys(), articles, failed)
            since_save = 0

    save_progress(done.keys(), articles, failed)

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)
    print("확보:", len(articles))
    print("실패/제외:", len(done) - len(articles))
    print("저장:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
