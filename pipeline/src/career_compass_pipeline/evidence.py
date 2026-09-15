"""근거 문서 메타 카탈로그(evidence[]) 조립 — F-04. 근거 타임라인.

기능명세 F-04:
  입력 : 수집 문서의 제목·발행일·출처·URL
  처리 : 시간 역순 정렬
  조건 : 본문을 화면에 재출력하지 않음 — 제목·날짜·링크까지만

``build_evidence_catalog``은 Area evidence에서 메타 필드만 추출하고
중복을 제거한 뒤 발행일 역순으로 정렬된 ``Analysis.evidence[]``를 돌려줍니다.
LLM 호출 없음, 결정적(deterministic) 변환.
"""

from __future__ import annotations

from typing import TypedDict

from career_compass_pipeline.aggregate import article_id_to_evidence_id

# ── 출력 타입 ──────────────────────────────────────────────────────────────────

_UNKNOWN_DATE = ""
_DEFAULT_SOURCE = "blog"


class Evidence(TypedDict):
    """웹 Analysis.evidence[] 항목 하나.

    화면은 본문을 싣지 않습니다.
    title·publishedAt·source·url 네 필드만 표시합니다 (F-04 조건).
    """

    id: str
    """``ev-{article_id}`` 형식. ``aggregate.article_id_to_evidence_id``와 동일한 규칙."""

    title: str
    """수집 문서 제목. 비어 있으면 빈 문자열."""

    publishedAt: str
    """발행일 YYYY-MM-DD. 알 수 없으면 빈 문자열.
    화면은 연월까지만 표시합니다 (F-04)."""

    source: str
    """``"blog"`` 또는 ``"job"``."""

    url: str
    """원문 링크."""


# ── 핵심 조립 함수 ────────────────────────────────────────────────────────────


def build_evidence_catalog(
    areas: list[dict],
    role: str,
    *,
    source_by_id: dict[str, str] | None = None,
    published_at_by_id: dict[str, str] | None = None,
) -> list[Evidence]:
    """Area 목록에서 근거 문서 메타 카탈로그를 조립합니다 (F-04).

    ``build_domains``와 같은 Area 입력을 받아 role 기준으로 필터링한 뒤
    중복 없는 ``Evidence`` 목록을 **발행일 역순**으로 반환합니다.

    Args:
        areas: ``build_areas_per_company.py`` 출력의 Area 목록.
            각 evidence 항목에 ``article_id``, ``title``, ``url`` 필드가 있어야 합니다.
        role: 필터링할 직무 슬러그 (예: ``"backend"``).
            evidence의 ``roles`` 목록에 이 값이 없으면 제외합니다.
        source_by_id: ``article_id → "blog"|"job"`` 매핑.
            생략하면 전부 ``"blog"`` (기술 블로그 기본값).
        published_at_by_id: ``article_id → "YYYY-MM-DD"`` 매핑.
            생략하거나 해당 id가 없으면 발행일을 빈 문자열로 처리하고
            정렬 시 맨 뒤로 밉니다.

    Returns:
        ``Evidence`` TypedDict 목록.
        - **발행일 역순** 정렬 (최신 문서가 앞). 발행일 없는 항목은 뒤로.
        - 같은 ``article_id``가 여러 Area에 걸쳐 등장해도 한 번만 포함.
        - 본문·임베딩 등 무거운 필드는 포함하지 않음 (F-04 조건).

    Notes:
        evidence id 생성 규칙은 ``aggregate.article_id_to_evidence_id``와 동일합니다.
        ``build_domains``가 만든 ``evidenceIds``와 1:1 매핑이 보장됩니다.
    """
    if source_by_id is None:
        source_by_id = {}
    if published_at_by_id is None:
        published_at_by_id = {}

    seen: set[str] = set()
    items: list[Evidence] = []

    for area in areas:
        for ev in area.get("evidence") or []:
            if role not in (ev.get("roles") or []):
                continue

            aid: str = ev.get("article_id", "")
            if not aid or aid in seen:
                continue
            seen.add(aid)

            items.append(
                Evidence(
                    id=article_id_to_evidence_id(aid),
                    title=ev.get("title") or "",
                    publishedAt=published_at_by_id.get(aid, _UNKNOWN_DATE),
                    source=source_by_id.get(aid, _DEFAULT_SOURCE),
                    url=ev.get("url") or "",
                )
            )

    return _sort_by_published_at_desc(items)


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────


def _sort_key(item: Evidence) -> tuple[bool, str]:
    """발행일 역순 정렬 키.

    ``reverse=True``로 사용하며 다음 우선순위로 정렬됩니다.
    1. 발행일이 있는 항목 먼저 (``True > False``)
    2. 같은 그룹 내에서 날짜 내림차순 (``"2026-09" > "2025-01"``)
    3. 발행일이 없는 항목은 맨 뒤
    """
    date = item["publishedAt"]
    return (date != _UNKNOWN_DATE, date)


def _sort_by_published_at_desc(items: list[Evidence]) -> list[Evidence]:
    """발행일 역순(최신 → 과거 → 날짜 없음) 정렬."""
    return sorted(items, key=_sort_key, reverse=True)
