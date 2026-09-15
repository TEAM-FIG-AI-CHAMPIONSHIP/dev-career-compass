"""Playwright로 목록 페이지를 열고, 그 과정에서 나온 공개 JSON만 가로챈다.

로그인·지원·이력서 경로는 열지 않는다. 분석·광고 응답은 버린다.
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common.http_utils import USER_AGENT

SKIP_URL = (
    "google-analytics",
    "googletagmanager",
    "doubleclick",
    "facebook.com",
    "sentry.io",
    "hotjar",
    "mixpanel",
    "amplitude",
    "datadog",
    "clarity.ms",
)


def capture_page(
    url,
    *,
    wait_until="networkidle",
    timeout=60000,
    extra_wait_ms=1500,
    wait_selector=None,
    block_url_substrings=None,
):
    """목록 URL 1회 방문. (html, json_responses) 반환."""
    from playwright.sync_api import sync_playwright

    json_responses = []
    html = ""
    blocked = tuple(block_url_substrings or ())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, locale="ko-KR")
        page = context.new_page()
        if blocked:
            page.route(
                "**/*",
                lambda route: route.abort()
                if any(token in route.request.url for token in blocked)
                else route.continue_(),
            )

        def on_response(response):
            ctype = (response.headers.get("content-type") or "").lower()
            url_l = response.url.lower()
            if any(skip in url_l for skip in SKIP_URL):
                return
            if "application/json" not in ctype and not url_l.split("?", 1)[0].endswith(".json"):
                return
            try:
                json_responses.append(
                    {"url": response.url, "status": response.status, "body": response.json()}
                )
            except Exception:
                pass

        page.on("response", on_response)
        page.goto(url, wait_until=wait_until, timeout=timeout)
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=20000)
            except Exception:
                pass
        if extra_wait_ms:
            page.wait_for_timeout(extra_wait_ms)
        html = page.content()
        browser.close()
    return html, json_responses


def extract_dom_links(html, base_url, href_needles=None, min_title=4):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    seen = set()
    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        if href_needles and not any(needle in href.lower() for needle in href_needles):
            continue
        title = anchor.get_text(" ", strip=True)
        if len(title) < min_title:
            continue
        key = (href, title)
        if key in seen:
            continue
        seen.add(key)
        records.append({"title": title, "url": href})
    return records
