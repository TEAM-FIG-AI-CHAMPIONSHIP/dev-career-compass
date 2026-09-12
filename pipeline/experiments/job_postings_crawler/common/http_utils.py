"""공통 HTTP 요청 유틸 (헤더 / 재시도 / sleep)."""

import time

import requests

# HTTP 헤더는 latin-1만 허용하므로 한글("해커톤 프로젝트")을 그대로 보낼 수 없다.
USER_AGENT = "BeforeJoinCrawler/1.0 (Wanted AI Hackathon project)"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "ko-KR,ko;q=0.9",
}

DEFAULT_DELAY = 1.0
DEFAULT_TIMEOUT = 15


def fetch(url, delay=DEFAULT_DELAY, retries=2, params=None, headers=None):
    """GET 요청 후 응답 텍스트 반환. 요청 전 delay초 대기."""
    return _request("GET", url, delay=delay, retries=retries, params=params, headers=headers).text


def fetch_json(url, delay=DEFAULT_DELAY, retries=2, params=None, headers=None, method="GET", json_body=None):
    """JSON API 호출 후 파싱된 결과 반환."""
    merged = {"Accept": "application/json"}
    if headers:
        merged.update(headers)
    res = _request(
        method, url, delay=delay, retries=retries, params=params, headers=merged, json_body=json_body
    )
    return res.json()


def _request(method, url, delay, retries, params=None, headers=None, json_body=None):
    merged = dict(HEADERS)
    if headers:
        merged.update(headers)

    last_error = None
    for attempt in range(retries + 1):
        time.sleep(delay if attempt == 0 else delay * (attempt + 1))
        try:
            res = requests.request(
                method, url, headers=merged, params=params, json=json_body, timeout=DEFAULT_TIMEOUT
            )
            res.raise_for_status()
            # Content-Type에 charset이 없으면 requests가 ISO-8859-1로 넘겨 한글이 깨진다.
            if res.encoding and res.encoding.lower() in ("iso-8859-1", "latin-1"):
                res.encoding = res.apparent_encoding or "utf-8"
            return res
        except requests.RequestException as exc:
            last_error = exc
    raise last_error
