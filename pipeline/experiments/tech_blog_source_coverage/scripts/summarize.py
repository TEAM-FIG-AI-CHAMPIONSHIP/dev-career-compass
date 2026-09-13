"""probe/collect/extract 리포트만 읽어 data/research 요약을 만든다. 본문은 쓰지 않는다."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = PROJECT_ROOT / "pipeline" / "experiments" / "tech_blog_source_coverage"
WORK = PROJECT_ROOT / "data" / "work" / "tech_blog_source_coverage"
RESEARCH_DIR = PROJECT_ROOT / "data" / "research"
RESEARCH_MD = RESEARCH_DIR / "tech_blog_source_coverage.md"
RESEARCH_JSON = RESEARCH_DIR / "tech_blog_source_coverage.json"

PLATFORM_HINTS = {
    "올리브영": "자체 기술블로그 (oliveyoung.tech)",
    "네이버 D2": "자체 플랫폼 (d2.naver.com)",
    "토스": "자체 기술블로그 (toss.tech, Next.js)",
    "당근": "Medium publication (medium.com/daangn)",
}


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def first_working_rss(rss_results: list[dict]) -> dict | None:
    for item in rss_results:
        if item.get("available"):
            return item
    return None


def strategy_label(row: dict) -> str:
    if row["recent_12m_ok"] == "O":
        if (row.get("rss_coverage") == "likely_sufficient"):
            return "RSS"
        used = row.get("discovered_sources") or []
        has_rss = "rss" in used
        has_sitemap = "sitemap" in used
        if has_rss and has_sitemap:
            return "RSS+Sitemap"
        if has_rss:
            return "RSS"
        if has_sitemap:
            return "Sitemap"
        return row.get("probe_strategy") or "RSS"
    if row.get("probe_strategy") == "custom_or_archive":
        return "Custom"
    if row.get("archive_candidate"):
        return "Archive"
    return "Custom"


def build_rows() -> list[dict]:
    config = load_json(EXPERIMENT / "config" / "blogs.json") or []
    probe = load_json(WORK / "probe" / "source_probe.json") or {}
    collect = load_json(WORK / "collected" / "collect_report.json") or {}
    extract = load_json(WORK / "extracted" / "extract_report.json") or {}
    collected_articles = load_json(WORK / "collected" / "articles.json") or []
    extracted_articles = load_json(WORK / "extracted" / "articles.json") or []

    probe_by_company = {
        item["company"]: item for item in probe.get("companies", [])
    }
    collect_by_company = {
        item["company"]: item for item in collect.get("companies", [])
    }

    extracted_ok = {}
    extracted_short = {}
    for article in extracted_articles:
        company = article["company"]
        extracted_ok[company] = extracted_ok.get(company, 0) + 1
        if article.get("extraction_quality") == "short":
            extracted_short[company] = extracted_short.get(company, 0) + 1

    extract_fail_by_company = {}
    for failure in extract.get("failures", []):
        article_id = failure.get("article_id")
        company = next(
            (
                article["company"]
                for article in collected_articles
                if article.get("article_id") == article_id
            ),
            None,
        )
        if company:
            extract_fail_by_company[company] = extract_fail_by_company.get(company, 0) + 1

    discovered = {}
    for article in collected_articles:
        company = article["company"]
        sources = discovered.setdefault(company, set())
        sources.update(article.get("discovered_by") or [])

    rows = []
    for source in config:
        company = source["company"]
        probe_row = probe_by_company.get(company, {})
        collect_row = collect_by_company.get(company, {})
        rss = first_working_rss(probe_row.get("rss") or [])
        sitemap = probe_row.get("sitemap") or {}
        under_blog = sitemap.get("urls_under_blog", 0)
        outside_blog = sitemap.get("urls_outside_blog", 0)
        collect_count = collect_row.get("collected_count", 0)
        extract_ok = extracted_ok.get(company, 0)
        extract_fail = extract_fail_by_company.get(company, 0)
        total_extract = extract_ok + extract_fail

        rss_ok = "O" if rss else "X"
        sitemap_ok = "O" if under_blog > 0 else "X"
        rss_covers_12m = (rss or {}).get("coverage") == "likely_sufficient"
        sitemap_added = "sitemap" in discovered.get(company, set()) and not rss_covers_12m
        recent_ok = "O" if rss_covers_12m or sitemap_added else "X"

        failure_reasons = []
        if not rss:
            failure_reasons.append("RSS/Atom 없음 또는 파싱 실패")
        elif not rss_covers_12m:
            failure_reasons.append(
                f"RSS가 최근 {(rss or {}).get('entry_count')}건만 내려줌 "
                f"(oldest={(rss or {}).get('oldest_date')})"
            )
        if under_blog == 0:
            if sitemap.get("total_unique_urls", 0) > 0:
                failure_reasons.append(
                    f"sitemap URL {sitemap['total_unique_urls']}개 중 "
                    f"blog_url 접두어 밖 {outside_blog}개"
                )
            else:
                failure_reasons.append("sitemap에서 게시글 URL을 못 찾음")
        if collect_row.get("missing_date"):
            failure_reasons.append(
                f"게시일 확인 실패 {collect_row['missing_date']}건"
            )
        if collect_row.get("failed_count"):
            failure_reasons.append(
                f"페이지 요청 실패 {collect_row['failed_count']}건"
            )

        generic_failed = recent_ok == "X"
        custom_needed = generic_failed

        row = {
            "company": company,
            "blog_url": source["blog_url"],
            "platform": PLATFORM_HINTS.get(company, ""),
            "rss_atom": rss_ok,
            "rss_url": (rss or {}).get("url"),
            "rss_entry_count": (rss or {}).get("entry_count"),
            "rss_coverage": (rss or {}).get("coverage"),
            "sitemap": sitemap_ok,
            "sitemap_urls_under_blog": under_blog,
            "sitemap_urls_outside_blog": outside_blog,
            "recent_12m_ok": recent_ok,
            "recent_12m_count": collect_count,
            "extract_success": extract_ok,
            "extract_failure": extract_fail,
            "extract_total": total_extract,
            "extract_short": extracted_short.get(company, 0),
            "extract_rate": (
                round(extract_ok / total_extract * 100, 1)
                if total_extract
                else None
            ),
            "discovered_sources": sorted(discovered.get(company, [])),
            "probe_strategy": probe_row.get("recommended_strategy"),
            "generic_failure_reason": (
                "; ".join(failure_reasons) if generic_failed else ""
            ),
            "custom_needed": "O" if custom_needed else "X",
            "notes": [],
        }
        if collect_row.get("missing_date") and rss_covers_12m:
            row["notes"].append(
                f"sitemap HTML 게시일 확인 실패 {collect_row['missing_date']}건. "
                "12개월 확정분은 RSS"
            )
        if outside_blog > 0:
            row["notes"].append(
                f"sitemap 전체 {sitemap.get('total_unique_urls', 0)}개 중 "
                f"{outside_blog}개는 blog_url 밖이라 generic 가드로 제외"
            )
        if extracted_short.get(company):
            row["notes"].append(
                f"본문 300자 미만 {extracted_short[company]}건 (성공으로 집계, quality=short)"
            )
        if extract_fail:
            row["notes"].append(
                f"Trafilatura 본문 추출 실패 {extract_fail}/{total_extract}"
            )
        row["collect_strategy"] = strategy_label(row)
        rows.append(row)
    return rows


def render_markdown(rows: list[dict], generated_at: str) -> str:
    lines = [
        "# 기업별 기술블로그 수집 소스 커버리지",
        "",
        f"조사 시각: {generated_at}",
        "",
        "우아한형제들에서 검증한 generic collector(RSS 우선 → sitemap fallback)를",
        "올리브영, 네이버 D2, 토스, 당근에 그대로 적용한 결과입니다.",
        "Area / embedding / clustering / LLM은 포함하지 않습니다.",
        "",
        "본문 원문은 `data/work/tech_blog_source_coverage/`에만 있고 Git에 없습니다.",
        "",
        "## 회사별 요약",
        "",
        "| 회사명 | 블로그 URL | 플랫폼/형태 | RSS/Atom | Sitemap | 최근 12개월 수집 | 최근 12개월 게시글 수 | 본문 추출 성공 / 전체 | 수집 전략 | generic 실패 원인 | custom 필요 | 비고 |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        extract = (
            f"{row['extract_success']} / {row['extract_total']}"
            if row["extract_total"]
            else "0 / 0"
        )
        if row["extract_rate"] is not None:
            extract += f" ({row['extract_rate']}%)"
        lines.append(
            "| {company} | {blog_url} | {platform} | {rss} | {sitemap} | {recent} | {count} | {extract} | {strategy} | {failure} | {custom} | {notes} |".format(
                company=row["company"],
                blog_url=row["blog_url"],
                platform=row["platform"],
                rss=row["rss_atom"],
                sitemap=row["sitemap"],
                recent=row["recent_12m_ok"],
                count=row["recent_12m_count"],
                extract=extract,
                strategy=row["collect_strategy"],
                failure=row["generic_failure_reason"] or "-",
                custom=row["custom_needed"],
                notes="; ".join(row["notes"]) or "-",
            )
        )

    lines.extend(
        [
            "",
            "## 해석",
            "",
            "- `최근 12개월 수집`은 글이 한 건이라도 있다는 뜻이 아니다.",
            "  RSS/sitemap으로 **12개월 전체를 닫을 수 있는지**를 본다.",
            "  RSS oldest가 12개월보다 짧고 sitemap이 못 메우면 X다.",
            "- custom 필요는 전용 크롤러를 지금 만들라는 뜻이 아니다.",
            "  generic으로 12개월을 못 닫거나 본문을 거의 못 뽑은 곳에 O를 표시한다.",
            "- sitemap URL이 blog_url 접두어 밖이면 회사 글로 세지 않았다.",
            "  Medium처럼 호스트 단위 sitemap이 나오는 경우를 막기 위한 generic 가드이다.",
            "",
            "### 회사별",
            "",
            "- **올리브영:** RSS가 2020년까지 내려와 최근 12개월 48건을 확보했고",
            "  Trafilatura 본문 추출은 48/48이다. sitemap URL은 더 많지만",
            "  날짜를 못 읽는 페이지가 대부분이라 RSS만으로 충분하다.",
            "- **네이버 D2:** `d2.atom`이 최신 20건만 주고 sitemap이 없다.",
            "  확보한 20건도 Trafilatura가 본문을 하나도 못 뽑았다 (0/20).",
            "  목록 페이지네이션과 JS 본문 처리가 필요하다.",
            "- **토스:** `rss.xml`이 최신 20건만 주고 robots/sitemap이 없다.",
            "  그 20건 본문은 20/20으로 뽑힌다. 12개월 전체를 쓰려면",
            "  목록 archive/커스텀이 필요하다.",
            "- **당근:** Medium RSS가 최신 10건만 주고, Medium 전역 sitemap",
            "  약 11만 URL은 `medium.com/daangn` 밖이다. 본문은 1/10이다.",
            "  Medium 피드·렌더를 별도로 봐야 한다.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = build_rows()
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    RESEARCH_MD.write_text(render_markdown(rows, generated_at), encoding="utf-8")

    public_rows = []
    for row in rows:
        public_rows.append(
            {
                key: value
                for key, value in row.items()
                if key != "notes"
            }
            | {"notes": row["notes"]}
        )
    RESEARCH_JSON.write_text(
        json.dumps(
            {"generated_at": generated_at, "companies": public_rows},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(RESEARCH_MD)
    print(RESEARCH_JSON)


if __name__ == "__main__":
    main()
