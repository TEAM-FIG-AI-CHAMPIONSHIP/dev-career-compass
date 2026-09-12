"""자체구축 사이트 공통 탐지기.

사용: python3 sources/custom/probe.py <url> [<url> ...]
robots.txt / sitemap / 임베디드 JSON / 정적 텍스트 / API URL 흔적을 한 번에 본다.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_utils import fetch  # noqa: E402
from common.paths import PROBE_DIR  # noqa: E402

EMBEDDED = ["__NEXT_DATA__", "__NUXT__", "__APOLLO_STATE__", "__INITIAL_STATE__",
            "__remixContext", "window.__", "__sveltekit"]
API_PAT = re.compile(
    r"""["'`](https?://[^"'`\s]{0,120}?(?:api|graphql|\.do|\.json)[^"'`\s]{0,120}|/[a-zA-Z0-9_\-/\.]{0,90}(?:api|graphql|\.do|\.json)[a-zA-Z0-9_\-/\.]{0,90})["'`]""",
    re.I,
)
JOB_HINT = ["개발", "엔지니어", "채용", "모집", "직무", "Engineer", "Developer"]


def probe(url):
    print("=" * 88)
    print(f"[{url}]")
    print("=" * 88)
    host = urlparse(url).netloc

    # robots.txt
    try:
        robots = fetch(f"https://{host}/robots.txt", delay=0.4)
        tail = robots.split("END Cloudflare Managed Content")[-1]
        rules = [l.strip() for l in tail.splitlines()
                 if l.strip().lower().startswith(("user-agent", "disallow", "allow", "crawl-delay", "sitemap"))]
        print("  -- robots.txt --")
        for r in rules[:40]:
            print(f"     {r}")
    except Exception as exc:
        print(f"  robots.txt: {exc}")

    # HTML
    try:
        html = fetch(url)
    except Exception as exc:
        print(f"  ❌ fetch 실패: {exc}")
        return
    print(f"\n  HTML {len(html):,} bytes")
    slug = re.sub(r"[^a-z0-9]+", "_", host.lower())
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    (PROBE_DIR / f"_probe_{slug}.html").write_text(html, encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")
    print("  -- 임베디드 JSON --")
    for key in EMBEDDED:
        if key in html:
            print(f"     ✅ {key}")
    if not any(k in html for k in EMBEDDED):
        print("     (없음)")

    text = soup.get_text(" ", strip=True)
    counts = {k: text.count(k) for k in JOB_HINT}
    print(f"  -- 정적 텍스트 {len(text):,}자: {counts}")
    print(f"     발췌: {text[:260]}")

    nd = soup.find("script", id="__NEXT_DATA__")
    if nd and nd.string:
        data = json.loads(nd.string)
        print(f"  -- __NEXT_DATA__ page={data.get('page')}")
        props = data.get("props", {}).get("pageProps", {})
        print(f"     pageProps 키: {list(props.keys())[:25]}")
        (PROBE_DIR / f"_probe_{slug}_next.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("  -- 인라인 스크립트 API URL --")
    inline = set()
    for s in soup.find_all("script"):
        if s.string:
            inline.update(m.group(1) for m in API_PAT.finditer(s.string))
    for u in sorted(inline)[:30]:
        print("    ", u)
    if not inline:
        print("     (없음)")

    print("  -- JS 번들 API URL --")
    srcs = [urljoin(url, s.get("src")) for s in soup.find_all("script") if s.get("src")]
    print(f"     번들 {len(srcs)}개")
    bundle = set()
    for src in srcs[:14]:
        try:
            js = fetch(src, delay=0.2)
        except Exception:
            continue
        bundle.update(m.group(1) for m in API_PAT.finditer(js))
    for u in sorted(bundle)[:40]:
        print("    ", u)
    if not bundle:
        print("     (없음)")

    # sitemap
    try:
        sm = fetch(f"https://{host}/sitemap.xml", delay=0.4)
        locs = re.findall(r"<loc>(.*?)</loc>", sm)
        print(f"  -- sitemap.xml: {len(locs)}개 URL")
        for l in locs[:15]:
            print("    ", l.strip())
    except Exception as exc:
        print(f"  -- sitemap.xml: {str(exc)[:70]}")
    print()


if __name__ == "__main__":
    for u in sys.argv[1:]:
        probe(u)
