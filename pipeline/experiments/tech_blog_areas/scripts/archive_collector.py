import re

from urllib.parse import (
    urljoin,
    urlparse,
    parse_qs,
    urlencode,
    urlunparse
)

import requests

from bs4 import BeautifulSoup


TIMEOUT = 15
MAX_PAGES = 20

EXCLUDED_PATH_WORDS = [
    "tag",
    "tags",
    "category",
    "categories",
    "author",
    "authors",
    "page",
    "search",
    "about",
    "contact",
    "feed",
    "rss",
    "atom",
    "subscribe",
    "login",
    "signin",
    "privacy",
    "terms",
    "sitemap"
]

# 날짜 텍스트가 <time datetime>에 없을 때를 대비한
# 느슨한 fallback 패턴. 오탐이 있을 수 있어 링크 근처
# 텍스트에서만 사용한다.
DATE_TEXT_PATTERN = re.compile(
    r"\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}"
)


def is_same_domain(
    url,
    blog_netloc
):
    return (
        urlparse(url).netloc
        == blog_netloc
    )


def looks_like_non_article_path(
    path
):
    lowered = path.lower()

    segments = [
        segment
        for segment in lowered.split("/")
        if segment
    ]

    if not segments:
        return True

    return any(
        segment in EXCLUDED_PATH_WORDS
        for segment in segments
    )


def extract_article_links(
    html,
    page_url,
    blog_netloc,
    normalize_url
):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = {}

    for anchor in soup.find_all(
        "a",
        href=True
    ):
        href = anchor["href"].strip()

        if (
            not href
            or href.startswith("#")
            or href.startswith("mailto:")
            or href.startswith("javascript:")
        ):
            continue

        absolute_url = normalize_url(
            urljoin(
                page_url,
                href
            )
        )

        if not is_same_domain(
            absolute_url,
            blog_netloc
        ):
            continue

        path = urlparse(
            absolute_url
        ).path

        if looks_like_non_article_path(
            path
        ):
            continue

        # 루트나 아주 짧은 경로는 목록/네비게이션일
        # 가능성이 높아 후보에서 제외한다.
        if (
            len(
                [
                    segment
                    for segment in path.split("/")
                    if segment
                ]
            )
            == 0
        ):
            continue

        candidate_date = (
            find_nearby_date_text(
                anchor
            )
        )

        links[absolute_url] = {
            "url": absolute_url,
            "link_text": (
                anchor.get_text(
                    " ",
                    strip=True
                )
            ),
            "nearby_date_text": (
                candidate_date
            )
        }

    return links


def find_nearby_date_text(
    anchor
):
    # 카드형 목록에서 흔한 패턴: 링크를 감싸는
    # 부모 요소 안에 <time datetime="..."> 또는
    # "2026-01-15" 같은 날짜 텍스트가 같이 있다.
    # 최대 3단계 상위까지만 보고, 그 이상은
    # 서로 다른 카드의 텍스트까지 섞여 들어올
    # 위험이 커서 포기한다.
    node = anchor

    for _ in range(3):
        if node is None:
            break

        time_tag = node.find(
            "time"
        )

        if (
            time_tag
            and time_tag.get(
                "datetime"
            )
        ):
            return time_tag[
                "datetime"
            ]

        text = node.get_text(
            " ",
            strip=True
        )

        match = DATE_TEXT_PATTERN.search(
            text
        )

        if match:
            return match.group(
                0
            )

        node = node.parent

    return None


def build_next_page_url(
    current_url,
    page_number,
    working_pattern
):
    parsed = urlparse(
        current_url
    )

    if working_pattern == "query_page":
        query = parse_qs(
            parsed.query
        )

        query["page"] = [
            str(page_number)
        ]

        new_query = urlencode(
            query,
            doseq=True
        )

        return urlunparse(
            parsed._replace(
                query=new_query
            )
        )

    if working_pattern == "query_p":
        query = parse_qs(
            parsed.query
        )

        query["p"] = [
            str(page_number)
        ]

        new_query = urlencode(
            query,
            doseq=True
        )

        return urlunparse(
            parsed._replace(
                query=new_query
            )
        )

    if working_pattern == "path_page":
        base = current_url.rstrip(
            "/"
        )

        return (
            base
            + f"/page/{page_number}/"
        )

    return None


def find_rel_next(
    html,
    page_url,
    normalize_url
):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    candidate = soup.find(
        "a",
        attrs={
            "rel": "next"
        },
        href=True
    )

    if not candidate:
        candidate = soup.find(
            "link",
            attrs={
                "rel": "next"
            },
            href=True
        )

    if not candidate:
        return None

    return normalize_url(
        urljoin(
            page_url,
            candidate["href"]
        )
    )


def fetch_listing_page(
    session,
    url
):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        return (
            None,
            str(error)
        )

    if not response.ok:
        return (
            None,
            f"HTTP {response.status_code}"
        )

    content_type = (
        response.headers
        .get(
            "content-type",
            ""
        )
        .lower()
    )

    if (
        "text/html"
        not in content_type
    ):
        return (
            None,
            f"not html: {content_type}"
        )

    return (
        response.text,
        None
    )


def page_is_past_cutoff(
    links,
    cutoff,
    parse_date
):
    dated = [
        parse_date(
            link.get(
                "nearby_date_text"
            )
        )
        for link in links.values()
    ]

    dated = [
        date
        for date in dated
        if date is not None
    ]

    if not dated:
        # 목록 페이지에 날짜 신호가 전혀 없으면
        # cutoff 판단을 할 수 없다. False를 반환해
        # 안전 상한(MAX_PAGES)에 걸릴 때까지
        # 페이지네이션을 계속하게 둔다.
        return False

    return all(
        date < cutoff
        for date in dated
    )


def collect_archive(
    session,
    source,
    cutoff,
    already_found_urls,
    normalize_url,
    parse_date
):
    blog_url = source[
        "blog_url"
    ]

    blog_netloc = urlparse(
        blog_url
    ).netloc

    candidates = {}
    pages_visited = []
    working_pattern = None
    stop_reason = None

    current_url = blog_url

    for page_number in range(
        1,
        MAX_PAGES + 1
    ):
        html, error = fetch_listing_page(
            session,
            current_url
        )

        if html is None:
            stop_reason = (
                f"page {page_number} 요청 실패: "
                f"{error}"
            )

            break

        page_links = extract_article_links(
            html=html,
            page_url=current_url,
            blog_netloc=blog_netloc,
            normalize_url=normalize_url
        )

        new_links = {
            url: link
            for url, link in page_links.items()
            if (
                url not in candidates
                and url not in already_found_urls
            )
        }

        pages_visited.append(
            {
                "page_number": page_number,
                "url": current_url,
                "link_count": len(
                    page_links
                ),
                "new_link_count": len(
                    new_links
                )
            }
        )

        if (
            page_number > 1
            and not new_links
        ):
            stop_reason = (
                "새 링크 없음 (같은 페이지 반복 "
                "또는 목록 끝)"
            )

            break

        candidates.update(
            new_links
        )

        if page_is_past_cutoff(
            page_links,
            cutoff,
            parse_date
        ):
            stop_reason = (
                "페이지 내 날짜 신호가 모두 cutoff "
                "이전"
            )

            break

        if page_number == 1:
            next_url = find_rel_next(
                html,
                current_url,
                normalize_url
            )

            if next_url and next_url != current_url:
                working_pattern = "rel_next"

            else:
                for pattern in (
                    "query_page",
                    "query_p",
                    "path_page"
                ):
                    trial_url = (
                        build_next_page_url(
                            current_url,
                            2,
                            pattern
                        )
                    )

                    trial_html, trial_error = (
                        fetch_listing_page(
                            session,
                            trial_url
                        )
                    )

                    if trial_html is None:
                        continue

                    trial_links = (
                        extract_article_links(
                            html=trial_html,
                            page_url=trial_url,
                            blog_netloc=blog_netloc,
                            normalize_url=normalize_url
                        )
                    )

                    trial_new = {
                        url
                        for url in trial_links
                        if url not in page_links
                    }

                    if trial_new:
                        working_pattern = pattern
                        break

                if not working_pattern:
                    stop_reason = (
                        "다음 페이지 패턴을 찾지 못함 "
                        "(rel=next 없음, "
                        "page/2, ?page=2, ?p=2 모두 "
                        "새 링크 없음)"
                    )

                    break

        if working_pattern == "rel_next":
            next_url = find_rel_next(
                html,
                current_url,
                normalize_url
            )

            if not next_url or next_url == current_url:
                stop_reason = (
                    "rel=next가 더 이상 없음"
                )

                break

            current_url = next_url

        else:
            current_url = (
                build_next_page_url(
                    current_url,
                    page_number + 1,
                    working_pattern
                )
            )

    else:
        stop_reason = (
            f"안전 상한({MAX_PAGES}페이지) 도달"
        )

    report = {
        "blog_url": blog_url,
        "working_pattern": (
            working_pattern
        ),
        "pages_visited": (
            pages_visited
        ),
        "page_count": len(
            pages_visited
        ),
        "candidate_count": len(
            candidates
        ),
        "stop_reason": stop_reason
    }

    return (
        candidates,
        report
    )
