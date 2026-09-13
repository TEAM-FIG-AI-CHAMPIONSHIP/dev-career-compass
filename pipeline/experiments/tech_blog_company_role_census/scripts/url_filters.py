"""sitemap loc 중 글이 아닌 목록·태그 URL을 걸러낸다."""

from __future__ import annotations

from urllib.parse import urlparse

SKIP_SEGMENTS = {
    "tag",
    "tags",
    "tagged",
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
    "sitemap",
    "series",
}
LISTING_LAST = {"posts", "blog", "articles", "news", "entry"}


def path_segments(url: str) -> list[str]:
    return [part.lower() for part in urlparse(url).path.split("/") if part]


def looks_like_article(url: str, blog_url: str) -> bool:
    article = urlparse((url or "").rstrip("/"))
    blog = urlparse((blog_url or "").rstrip("/"))
    if not article.netloc:
        return False
    if article.netloc == blog.netloc and article.path == blog.path:
        return False
    segments = path_segments(url)
    if not segments:
        return False
    if any(segment in SKIP_SEGMENTS for segment in segments):
        return False
    if segments[-1] in LISTING_LAST:
        return False
    return True
