"""Area evidence를 Analysis용 domains 목록으로 집계합니다.

``build_areas_per_company.py``가 생성한 Area 데이터를 받아
``apps/web/src/types/data.ts``의 ``Domain`` 타입에 맞는
``domains[]`` 배열을 만듭니다.

집계 로직만 담당합니다 — LLM 호출 없음, 결정적(deterministic) 변환.
"""

from __future__ import annotations

import re
from typing import TypedDict


# ── 출력 타입 ──────────────────────────────────────────────────────────────────


class Domain(TypedDict):
    """웹 Analysis.domains[] 항목 하나."""

    id: str
    """``dom-`` 접두사를 가진 kebab-slug. Area id 기반으로 결정적으로 생성."""

    label: str
    """화면에 표시할 Area 이름 (한국어 가능)."""

    counts: dict[str, int]
    """출처별 근거 문서 건수. 예: ``{"blog": 4}`` 또는 ``{"blog": 3, "job": 1}``."""

    evidenceIds: list[str]
    """``ev-`` 접두사를 가진 근거 문서 id 목록. article_id 기반으로 결정적으로 생성."""


# ── 내부 상수 ──────────────────────────────────────────────────────────────────

_NON_SLUG_RE = re.compile(r"[^a-z0-9]+")
_DOMAIN_ID_PREFIX = "dom-"
_EVIDENCE_ID_PREFIX = "ev-"
_DEFAULT_SOURCE = "blog"


# ── 공개 헬퍼 ─────────────────────────────────────────────────────────────────


def area_to_domain_id(area: dict) -> str:
    """Area dict에서 결정적인 domain id를 생성합니다.

    ``area["id"]``가 있으면 그것을 그대로 씁니다.
    없으면 ``area_name``을 ASCII-only kebab-slug로 변환합니다
    (한글 등 비ASCII 문자는 하이픈으로 대체).

    Args:
        area: Area dict. ``id`` 또는 ``area_name`` 필드를 사용.

    Returns:
        ``"dom-"`` 로 시작하는 문자열.
    """
    area_id: str = area.get("id", "")
    if area_id:
        return f"{_DOMAIN_ID_PREFIX}{area_id}"

    # fallback: area_name → ASCII kebab (한글은 하이픈으로 대체됨)
    name: str = area.get("area_name", "unknown")
    slug = _NON_SLUG_RE.sub("-", name.lower()).strip("-")[:50]
    return f"{_DOMAIN_ID_PREFIX}{slug or 'area'}"


def article_id_to_evidence_id(article_id: str) -> str:
    """article_id로 결정적인 evidence id를 생성합니다.

    Args:
        article_id: 콘텐츠 해시 기반 article_id (예: ``"40ca85f39b5dc7ec"``).

    Returns:
        ``"ev-"`` 로 시작하는 문자열.
    """
    return f"{_EVIDENCE_ID_PREFIX}{article_id}"


# ── 핵심 집계 함수 ────────────────────────────────────────────────────────────


def build_domains(
    areas: list[dict],
    role: str,
    *,
    source_by_id: dict[str, str] | None = None,
    min_evidence: int = 1,
) -> list[Domain]:
    """Area 목록을 Analysis용 ``domains[]``로 변환합니다.

    각 Domain은 하나의 Area를 특정 직무(role)에 해당하는 근거만 남겨
    필터링한 결과입니다. 해당 직무 근거가 ``min_evidence``건 미만이면
    그 Area는 출력에서 제외됩니다.

    Args:
        areas: ``build_areas_per_company.py`` 출력의 Area 목록.
            각 항목은 ``evidence[]`` 배열을 포함해야 합니다.
            evidence 항목은 ``article_id``, ``roles`` 필드를 가집니다.
            ``id`` 필드가 있으면 domain id 생성에 사용합니다.
        role: 필터링할 직무 슬러그 (예: ``"backend"``, ``"frontend"``).
        source_by_id: ``article_id → "blog"|"job"`` 매핑. 생략하면 모든
            evidence가 ``"blog"`` (기술 블로그)로 처리됩니다.
        min_evidence: 이 role의 근거가 이 수 미만이면 Area를 제외합니다.
            기본값 1 — 근거가 0건이면 제외.

    Returns:
        ``Domain`` TypedDict 목록. 입력 areas 순서를 유지합니다.

    Notes:
        - 같은 ``article_id``가 한 Area의 evidence에 중복 등장해도
          한 건으로만 셉니다 (중복 제거, 첫 번째 등장 순서 유지).
        - domain id는 Area ``id`` 필드 기반으로 결정적으로 생성됩니다.
          Area에 ``id``가 없으면 ``area_name``을 kebab으로 변환합니다.
        - domain id 충돌 시 자동으로 숫자 접미사(-2, -3, …)를 붙입니다.
        - ``counts``의 합계는 ``evidenceIds``의 길이와 항상 같습니다.
    """
    if source_by_id is None:
        source_by_id = {}

    domains: list[Domain] = []
    seen_domain_ids: set[str] = set()

    for area in areas:
        raw_evidence: list[dict] = area.get("evidence") or []

        # 1) 이 role의 근거만 추출
        role_evidence = [
            ev for ev in raw_evidence
            if role in (ev.get("roles") or [])
        ]

        if len(role_evidence) < min_evidence:
            continue

        # 2) domain id 생성 (충돌 방지)
        base_id = area_to_domain_id(area)
        domain_id = _unique_id(base_id, seen_domain_ids)
        seen_domain_ids.add(domain_id)

        # 3) 같은 article_id 중복 제거 (순서 유지)
        deduped = _deduplicate_evidence(role_evidence)

        # 4) 출처별 건수 집계
        counts: dict[str, int] = {}
        for ev in deduped:
            aid: str = ev.get("article_id", "")
            source = source_by_id.get(aid, _DEFAULT_SOURCE)
            counts[source] = counts.get(source, 0) + 1

        # 5) evidence id 목록
        evidence_ids = [
            article_id_to_evidence_id(ev["article_id"])
            for ev in deduped
            if ev.get("article_id")
        ]

        domains.append(
            Domain(
                id=domain_id,
                label=area.get("area_name", ""),
                counts=counts,
                evidenceIds=evidence_ids,
            )
        )

    return domains


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────


def _unique_id(base: str, seen: set[str]) -> str:
    """``base``가 ``seen``에 없으면 그대로, 있으면 ``-2``, ``-3``… 를 붙입니다."""
    if base not in seen:
        return base
    suffix = 2
    while f"{base}-{suffix}" in seen:
        suffix += 1
    return f"{base}-{suffix}"


def _deduplicate_evidence(evidence: list[dict]) -> list[dict]:
    """article_id 기준 중복 제거 (첫 번째 등장 순서 유지)."""
    seen: set[str] = set()
    result: list[dict] = []
    for ev in evidence:
        aid: str = ev.get("article_id", "")
        if not aid or aid in seen:
            continue
        seen.add(aid)
        result.append(ev)
    return result
