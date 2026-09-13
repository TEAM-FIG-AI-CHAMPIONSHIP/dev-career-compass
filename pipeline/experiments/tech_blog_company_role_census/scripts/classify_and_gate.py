"""제목(+본문)으로 기술글 여부와 직무를 다중 매핑하고 1차 게이트를 집계한다."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import (
    ARTICLES_FILE,
    CLASSIFIED_FILE,
    COLLECT_REPORT,
    COMPANIES_FILE,
    EXTRACT_REPORT,
    EXTRACTED_FILE,
    RESEARCH,
)

ROLES = ["backend", "frontend", "mobile", "data-ai"]
ROLE_LABELS = {
    "backend": "서버·백엔드",
    "frontend": "웹 프론트엔드",
    "mobile": "모바일",
    "data-ai": "데이터·AI",
}
GATE = 8
QUALITY = 10
S5_MIN_COMPANIES = 3

NON_TECH = [
    "채용 공고",
    "채용공고",
    "신입 채용",
    "경력 채용",
    "인턴 모집",
    "채용 안내",
    "복지",
    "기업문화",
    "조직문화",
    "워크숍 후기",
    "컨퍼런스 후기",
    "세미나 후기",
    "밋업 후기",
    "행사 스케치",
    "파티",
    "회식",
    "온보딩 데이",
    "입사 후기",
    "인터뷰이",
    "디자이너를 만나",
]

TECH_HINTS = [
    "서버",
    "백엔드",
    "프론트",
    "모바일",
    "안드로이드",
    "데이터",
    "인프라",
    "api",
    "kafka",
    "redis",
    "kubernetes",
    "react",
    "spring",
    "msa",
    "llm",
    "ml",
    "ai",
    "ios",
    "android",
    "pipeline",
    "모니터링",
    "배포",
    "테스트",
    "성능",
    "캐시",
    "데이터베이스",
    "도커",
    "클라우드",
]

ROLE_KEYWORDS = {
    "backend": [
        "백엔드",
        "서버",
        "backend",
        "spring",
        "kafka",
        "redis",
        "msa",
        "마이크로서비스",
        "동시성",
        "인프라",
        "kubernetes",
        "k8s",
        "sre",
        "devops",
        "api 서버",
        "메시지 큐",
        "데이터베이스",
        "postgresql",
        "mysql",
    ],
    "frontend": [
        "프론트엔드",
        "프론트",
        "frontend",
        "react",
        "next.js",
        "nextjs",
        "css",
        "webview",
        "웹뷰",
        "접근성",
        "디자인 시스템",
        "typescript",
        "spa",
        "브라우저",
    ],
    "mobile": [
        "모바일",
        "ios",
        "android",
        "안드로이드",
        "flutter",
        "react native",
        "swift",
        "kotlin",
        "앱스토어",
    ],
    "data-ai": [
        "데이터",
        "머신러닝",
        "인공지능",
        "추천",
        "llm",
        "mlops",
        "bigquery",
        "분석 플랫폼",
        "데이터 파이프라인",
        "airflow",
        "feature store",
        "임베딩",
        "모델 서빙",
    ],
}


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())


def is_non_tech(text: str) -> bool:
    lowered = normalize(text)
    if any(token.lower() in lowered for token in NON_TECH):
        if not any(hint in lowered for hint in TECH_HINTS):
            return True
        event_only = any(token in lowered for token in ["채용", "복지", "회식", "입사 후기"])
        return event_only and not any(
            hint in lowered for hint in ["kafka", "react", "spring", "kubernetes", "llm"]
        )
    return False


def map_roles(text: str) -> list[str]:
    lowered = normalize(text)
    roles = []
    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            roles.append(role)
    return roles


def classify_article(article: dict) -> dict:
    text = " ".join(
        part
        for part in [article.get("title", ""), article.get("content", "")]
        if part
    )
    non_tech = is_non_tech(article.get("title", ""))
    roles = [] if non_tech else map_roles(text)
    if not non_tech and not roles:
        if any(hint in normalize(text) for hint in TECH_HINTS):
            assignment = []
            unassigned = False
            tech = True
        else:
            assignment = []
            unassigned = True
            tech = False
            non_tech = True
    else:
        assignment = roles
        unassigned = not non_tech and not roles
        tech = not non_tech and (bool(roles) or any(hint in normalize(text) for hint in TECH_HINTS))
        if unassigned:
            tech = False
    return {
        "article_id": article["article_id"],
        "company": article["company"],
        "title": article["title"],
        "url": article["url"],
        "published_at": article["published_at"],
        "is_tech": tech,
        "is_non_tech": non_tech,
        "roles": assignment,
        "unassigned": unassigned,
        "classified_from": "content" if article.get("content") else "title",
    }


def render_markdown(payload: dict) -> str:
    rows = payload["companies"]
    passing = [row for row in rows if row["pass_company"]]
    lines = [
        "# 111개 기술블로그 회사×직무 census (1차 게이트)",
        "",
        f"조사 시각: {payload['generated_at']}",
        f"관련 이슈: #{payload['issue']} (이전 #30)",
        "",
        "회사 전체 글 수가 아니라 **회사 × 직무당 최근 12개월 기술글 8개**를 1차 게이트로 본다.",
        "Area / embedding / clustering / LLM은 돌리지 않았다. 이 파일이 최종 60~80 확정이 아니다.",
        "뉴스·채용공고는 집계에 쓰지 않았다.",
        "",
        "## 총괄",
        "",
        f"- 조사 회사: {payload['totals']['companies']}곳",
        f"- 메타데이터 1건 이상 수집: {payload['totals']['collectable']}곳",
        f"- 12개월 RSS가 닫힌 회사: {payload['totals']['twelve_month_closed']}곳",
        f"- 수집 게시글: {payload['totals']['articles']}건",
        f"- 본문 추출 성공: {payload['totals']['extract_success']} / 시도 {payload['totals']['extract_input']}",
        f"- 기술글: {payload['totals']['tech_articles']}건",
        f"- 1차 게이트 통과(pass): **{payload['totals']['passing_companies']}곳**",
        f"- 12개월은 닫혔으나 8개 미만(fail): **{payload['totals']['fail_companies']}곳**",
        f"- 아직 12개월을 못 닫음(unknown): **{payload['totals']['unknown_companies']}곳**",
        f"- 1차 게이트 통과 조합: **{payload['totals']['passing_pairs']}개**",
        "",
        "표의 X는 탈락이 아니다. `unknown`은 수집을 못 해서 글 수를 모르는 상태다.",
        "",
        "## 직무별 통과 회사 수 (S5 최소 3곳)",
        "",
        "| 직무 | 통과 회사 | S5 |",
        "| --- | ---: | --- |",
    ]
    for role in ROLES:
        count = payload["role_company_counts"][role]
        lines.append(
            f"| {ROLE_LABELS[role]} | {count} | {'통과' if count >= S5_MIN_COMPANIES else '미달'} |"
        )
    lines.extend(
        [
            "",
            "## 1차 게이트를 통과한 회사",
            "",
            "| 회사 | 기술글 | 백엔드 | 프론트 | 모바일 | 데이터·AI | 통과 직무 | 비고 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in passing:
        lines.append(
            "| {name} | {tech} | {backend} | {frontend} | {mobile} | {data} | {roles} | {notes} |".format(
                name=row["name"],
                tech=row["tech_count"],
                backend=row["roles"]["backend"]["tech_count"],
                frontend=row["roles"]["frontend"]["tech_count"],
                mobile=row["roles"]["mobile"]["tech_count"],
                data=row["roles"]["data-ai"]["tech_count"],
                roles=", ".join(ROLE_LABELS[r] for r in row["passing_roles"]) or "-",
                notes=row["notes"] or "-",
            )
        )
    lines.extend(
        [
            "",
            "## 전체 회사 판정",
            "",
            "| 회사 | 수집 | 12개월 닫힘 | 기술글 | 백엔드 | 프론트 | 모바일 | 데이터·AI | 1차 통과 직무 | 판정 |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {name} | {collected} | {closed} | {tech} | {backend} | {frontend} | {mobile} | {data} | {roles} | {expose} |".format(
                name=row["name"],
                collected=row["collected_count"],
                closed="O" if row["twelve_month_closed"] else "X",
                tech=row["tech_count"],
                backend=row["roles"]["backend"]["tech_count"],
                frontend=row["roles"]["frontend"]["tech_count"],
                mobile=row["roles"]["mobile"]["tech_count"],
                data=row["roles"]["data-ai"]["tech_count"],
                roles=", ".join(ROLE_LABELS[r] for r in row["passing_roles"]) or "-",
                expose=row["verdict"],
            )
        )
    lines.extend(
        [
            "",
            "## 한계",
            "",
            "- RSS 1라운드 뒤에 sitemap URL을 더 모을 수 있다. lastmod만 있으면 제목이 비어 분류가 안 된다.",
            "- 우아한형제들 표준 HTML/RSS/sitemap/wp-json은 이 census 경로에서 403이다. 별도 조사에서 기술블로그 수집 자체는 가능하다.",
            "- 카카오뱅크·페이·모빌리티는 archive/custom으로 12개월을 닫았고, 직무당 8개 미만이면 fail이다.",
            "- 분류는 제목(본문이 있으면 본문 포함) 키워드 다중 매핑이다. LLM이 아니다.",
            "- `데이터` 키워드가 데이터·AI를 과대 집계할 수 있다. 구름·한컴·삼성 등은 검수 필요.",
            "- RSS가 최근 N건만 주는 회사(토스, 네이버 D2, 당근, 카카오 등)는 sitemap/custom 전까지 과소 집계된다.",
            "- 8개 통과는 Area 3개·근거 2개를 보장하지 않는다. 그건 다음 게이트다.",
            "- 60~80개는 목표가 아니며, 통과분이 적으면 억지로 채우지 않는다.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    companies = load_json(COMPANIES_FILE) or []
    collect_report = load_json(COLLECT_REPORT) or {"companies": []}
    collected = load_json(ARTICLES_FILE) or []
    extracted = {item["article_id"]: item for item in (load_json(EXTRACTED_FILE) or [])}
    extract_report = load_json(EXTRACT_REPORT) or {}
    collect_by_name = {row["company"]: row for row in collect_report.get("companies", [])}

    classified = []
    for article in collected:
        merged = dict(article)
        if article["article_id"] in extracted:
            merged["content"] = extracted[article["article_id"]].get("content", "")
        classified.append(classify_article(merged))
    save_json(CLASSIFIED_FILE, classified)

    by_company = defaultdict(list)
    for item in classified:
        by_company[item["company"]].append(item)

    rows = []
    passing_pairs = 0
    role_company_counts = {role: 0 for role in ROLES}
    for source in companies:
        name = source["name"]
        collect_row = collect_by_name.get(name, {})
        items = by_company.get(name, [])
        tech_items = [item for item in items if item["is_tech"]]
        role_stats = {}
        passing_roles = []
        for role in ROLES:
            count = sum(1 for item in tech_items if role in item["roles"])
            passed = count >= GATE
            quality = count >= QUALITY
            role_stats[role] = {
                "tech_count": count,
                "pass": passed,
                "quality_band": quality,
            }
            if passed:
                passing_roles.append(role)
                role_company_counts[role] += 1
                passing_pairs += 1
        notes = []
        if collect_row.get("error"):
            notes.append(f"수집 오류: {collect_row['error']}")
        if not collect_row.get("collectable") and not items:
            notes.append("최근 12개월 메타데이터를 generic RSS로 못 모음")
        if collect_row.get("rss", {}).get("coverage") == "insufficient":
            notes.append("RSS가 12개월을 닫지 못해 과소 집계 가능")
        if collect_row.get("round2", {}).get("strategy") == "skip_medium_sitemap":
            notes.append("Medium sitemap은 제외. RSS만으로 12개월 판정")
        if collect_row.get("round2", {}).get("closed_by_sitemap"):
            notes.append("sitemap으로 12개월을 보강함")
        empty_titles = sum(1 for item in items if not (item.get("title") or "").strip())
        if empty_titles >= 8:
            notes.append(f"제목 없는 sitemap URL {empty_titles}건. 분류 전 제목 보강 필요")
        closed = bool(collect_row.get("twelve_month_closed"))
        passed = len(passing_roles) >= 1
        if passed:
            verdict = "pass"
        elif closed:
            verdict = "fail"
        else:
            verdict = "unknown"
        rows.append(
            {
                "name": name,
                "blog_url": source["url"],
                "collected_count": collect_row.get("collected_count", len(items)),
                "collectable": bool(collect_row.get("collectable")),
                "twelve_month_closed": closed,
                "tech_count": len(tech_items),
                "non_tech_count": sum(1 for item in items if item["is_non_tech"]),
                "unassigned_count": sum(1 for item in items if item["unassigned"]),
                "roles": role_stats,
                "passing_roles": passing_roles,
                "pass_company": passed,
                "verdict": verdict,
                "notes": "; ".join(notes),
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issue": 40,
        "gate": {"min_tech_posts_per_role": GATE, "quality_band": QUALITY},
        "totals": {
            "companies": len(companies),
            "collectable": sum(1 for row in rows if row["collectable"]),
            "twelve_month_closed": sum(1 for row in rows if row["twelve_month_closed"]),
            "articles": len(collected),
            "extract_input": extract_report.get("input_count", 0),
            "extract_success": extract_report.get("success_count", 0),
            "tech_articles": sum(1 for item in classified if item["is_tech"]),
            "passing_companies": sum(1 for row in rows if row["verdict"] == "pass"),
            "fail_companies": sum(1 for row in rows if row["verdict"] == "fail"),
            "unknown_companies": sum(1 for row in rows if row["verdict"] == "unknown"),
            "passing_pairs": passing_pairs,
        },
        "role_company_counts": role_company_counts,
        "companies": rows,
    }
    selected = [
        {
            "name": row["name"],
            "blog_url": row["blog_url"],
            "passing_roles": [ROLE_LABELS[role] for role in row["passing_roles"]],
            "role_counts": {
                ROLE_LABELS[role]: row["roles"][role]["tech_count"] for role in ROLES
            },
            "tech_count": row["tech_count"],
            "job_count": len(row["passing_roles"]),
            "gate": "first_count_only",
            "final_area_gate": False,
        }
        for row in rows
        if row["pass_company"]
    ]
    RESEARCH.mkdir(parents=True, exist_ok=True)
    save_json(RESEARCH / "census.json", payload)
    save_json(
        RESEARCH / "selected_companies.json",
        {
            "issue": 40,
            "note": "verdict=pass 만. 직무당 기술글 8개. Area 게이트는 아직 아니다.",
            "company_count": len(selected),
            "companies": selected,
        },
    )
    unknown = [
        {
            "name": row["name"],
            "blog_url": row["blog_url"],
            "collected_count": row["collected_count"],
            "notes": row["notes"],
        }
        for row in rows
        if row["verdict"] == "unknown"
    ]
    save_json(
        RESEARCH / "unknown_companies.json",
        {
            "note": "12개월을 닫지 못해 탈락이 아니라 미수집이다. sitemap/custom 다음 라운드 대상.",
            "company_count": len(unknown),
            "companies": unknown,
        },
    )
    (RESEARCH / "summary.md").write_text(render_markdown(payload), encoding="utf-8")
    print("통과 회사", len(selected), "조합", passing_pairs)
    print(RESEARCH / "summary.md")


if __name__ == "__main__":
    main()
