"""근거 문서 메타 카탈로그(evidence[]) 조립.

기능명세 연결:
  F-02. 조직 파악  — 영역 칩의 소스별 근거 건수 표시
  F-03. 프로젝트 방향 제안 — 제안 카드의 근거 링크(제목·URL)

``build_evidence_catalog``은 Area evidence에서 메타 필드만 추출하고
중복을 제거한 ``Analysis.evidence[]``를 돌려줍니다.
LLM 호출 없음, 결정적(deterministic) 변환.

조건 (기능명세):
  - 본문을 화면에 재출력하지 않음 — 제목·발행일·출처·URL까지만
  - 공고 데이터가 없어도 블로그만으로 정상 동작 (source 기본값 "blog")
"""

from __future__ import annotations

from typing import TypedDict

# ── 상수 ──────────────────────────────────────────────────────────────────────

_DEFAULT_SOURCE = "blog"
_EVIDENCE_ID_PREFIX = "ev-"


def _evidence_id(article_id: str) -> str:
    """article_id → ``ev-{article_id}`` 형식 id를 반환합니다.

    ``aggregate.article_id_to_evidence_id``와 동일한 규칙입니다.
    두 모듈이 머지되면 공통 헬퍼로 통합할 수 있습니다.
    """
    return f"{_EVIDENCE_ID_PREFIX}{article_id}"


# ── 출력 타입 ──────────────────────────────────────────────────────────────────


class Evidence(TypedDict):
    """웹 Analysis.evidence[] 항목 하나.

    화면은 본문을 싣지 않습니다.
    title·publishedAt·source·url 네 필드만 표시합니다.
    """

    id: str
    """``ev-{article_id}`` 형식. ``aggregate.article_id_to_evidence_id``와 동일한 규칙.
    두 모듈이 머지되면 공통 헬퍼로 통합할 수 있습니다."""

    title: str
    """수집 문서 제목. 비어 있으면 빈 문자열."""

    publishedAt: str
    """발행일 YYYY-MM-DD. 알 수 없으면 빈 문자열."""

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
    """Area 목록에서 근거 문서 메타 카탈로그를 조립합니다.

    ``build_domains``와 같은 Area 입력을 받아 role 기준으로 필터링한 뒤
    중복 없는 ``Evidence`` 목록을 반환합니다.

    Args:
        areas: ``build_areas_per_company.py`` 출력의 Area 목록.
            각 evidence 항목에 ``article_id``, ``title``, ``url`` 필드가 있어야 합니다.
        role: 필터링할 직무 슬러그 (예: ``"backend"``).
            evidence의 ``roles`` 목록에 이 값이 없으면 제외합니다.
        source_by_id: ``article_id → "blog"|"job"`` 매핑.
            생략하면 전부 ``"blog"`` (기술 블로그 기본값, F-02 조건).
        published_at_by_id: ``article_id → "YYYY-MM-DD"`` 매핑.
            생략하거나 해당 id가 없으면 빈 문자열.

    Returns:
        ``Evidence`` TypedDict 목록.

        - 같은 ``article_id``가 여러 Area에 걸쳐 등장해도 한 번만 포함.
          첫 번째 등장의 title·url이 사용됩니다.
        - 입력 areas의 evidence 등장 순서를 유지합니다.
        - 본문·임베딩 등 무거운 필드는 포함하지 않습니다.

    Notes:
        evidence id 생성 규칙(``ev-{article_id}``)은 ``aggregate.article_id_to_evidence_id``와
        동일합니다. 두 모듈이 머지된 뒤 ``build_domains``의 ``evidenceIds``와
        1:1 매핑이 통합 테스트로 검증될 수 있습니다.
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
                    id=_evidence_id(aid),
                    title=ev.get("title") or "",
                    publishedAt=published_at_by_id.get(aid, ""),
                    source=source_by_id.get(aid, _DEFAULT_SOURCE),
                    url=ev.get("url") or "",
                )
            )

    return items
