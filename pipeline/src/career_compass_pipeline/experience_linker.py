"""제안 항목에 경험 카탈로그 item id를 연결·검증합니다.

LLM이 생성한 ``NewSuggestion.coversItemIds`` / ``DeepenSuggestion.fromItemIds``
가 ``data/experience.json`` 의 실제 item id를 가리키는지 확인하고,
카탈로그에 없는 id를 제거합니다.

유효 id가 0개가 된 제안은 드롭합니다 — 경험 연결이 없는 신규 제안은
개인화(F-06) 화면에서 아무 이름표도 붙지 않고, 전제 경험이 없는 심화 제안은
역매칭(F-07) 로직이 성립하지 않기 때문입니다.

이 모듈은 결정적(deterministic)이며 LLM을 사용하지 않습니다.

기능명세 참조:
- F-06. 개인화 결과: ``coversItemIds``로 사용자 선택 경험과 신규 제안을 대조.
- F-07. 역매칭: ``fromItemIds``로 전제 경험과 회사 결과를 3단계로 분류.
"""

from __future__ import annotations

from typing import TypedDict

# ── 출력 타입 ──────────────────────────────────────────────────────────────────


class SuggestionValidationResult(TypedDict):
    """link_suggestions 반환값."""

    new: list[dict]
    """유효한 coversItemIds를 1개 이상 가진 신규 제안 목록."""

    deepen: list[dict]
    """유효한 fromItemIds를 1개 이상 가진 심화 제안 목록."""

    dropped_new: list[dict]
    """coversItemIds가 0개여서 드롭된 신규 제안."""

    dropped_deepen: list[dict]
    """fromItemIds가 0개여서 드롭된 심화 제안."""


# ── 핵심 함수 ──────────────────────────────────────────────────────────────────


def load_experience_ids(catalog: dict) -> set[str]:
    """experience.json에서 유효한 item id 집합을 추출합니다.

    ``levels`` 의 id는 포함하지 않습니다. 제안 연결에는 item id만 씁니다.

    Args:
        catalog: ``data/experience.json`` 전체를 파싱한 dict.

    Returns:
        모든 그룹의 item id를 모은 frozenset 수준의 set.
    """
    ids: set[str] = set()
    for group in catalog.get("groups", []):
        for item in group.get("items", []):
            item_id = item.get("id", "")
            if item_id:
                ids.add(item_id)
    return ids


def filter_experience_ids(ids: list[str], valid_ids: set[str]) -> list[str]:
    """카탈로그에 없는 item id를 제거합니다. 순서는 유지합니다.

    Args:
        ids: 검사할 id 목록.
        valid_ids: :func:`load_experience_ids` 로 추출한 유효 id 집합.

    Returns:
        카탈로그에 있는 id만 남긴 목록. 입력 순서를 보존합니다.
    """
    return [item_id for item_id in ids if item_id in valid_ids]


def link_new_suggestion(
    suggestion: dict,
    valid_ids: set[str],
) -> dict | None:
    """신규 제안의 ``coversItemIds`` 를 카탈로그 기준으로 검증합니다.

    유효 id가 1개 이상이면 정제된 제안 dict를 반환합니다.
    0개이면 ``None`` 을 반환합니다 (드롭 대상).

    F-06 개인화 결과에서 사용자가 고른 경험과 이 id들을 대조합니다.
    유효 id가 없으면 어떤 사용자에게도 "내 경험과 겹침" 이름표가 붙지 않으므로
    제안을 드롭합니다.

    Args:
        suggestion: ``NewSuggestion`` dict. ``coversItemIds`` 키를 포함합니다.
        valid_ids: 카탈로그에서 추출한 유효 id 집합.

    Returns:
        ``coversItemIds`` 가 정제된 제안 dict, 또는 ``None``.
    """
    raw: list[str] = suggestion.get("coversItemIds") or []
    filtered = filter_experience_ids(raw, valid_ids)
    if not filtered:
        return None
    return {**suggestion, "coversItemIds": filtered}


def link_deepen_suggestion(
    suggestion: dict,
    valid_ids: set[str],
) -> dict | None:
    """심화 제안의 ``fromItemIds`` 를 카탈로그 기준으로 검증합니다.

    유효 id가 1개 이상이면 정제된 제안 dict를 반환합니다.
    0개이면 ``None`` 을 반환합니다 (드롭 대상).

    심화 제안은 "A를 만들었다면 → B" 구조이므로 ``fromItemIds`` 가 없으면
    제안 자체가 성립하지 않습니다. F-07 역매칭도 전제 경험 id로 분류를 수행하므로
    유효 id가 없는 심화 제안은 드롭합니다.

    Args:
        suggestion: ``DeepenSuggestion`` dict. ``fromItemIds`` 키를 포함합니다.
        valid_ids: 카탈로그에서 추출한 유효 id 집합.

    Returns:
        ``fromItemIds`` 가 정제된 제안 dict, 또는 ``None``.
    """
    raw: list[str] = suggestion.get("fromItemIds") or []
    filtered = filter_experience_ids(raw, valid_ids)
    if not filtered:
        return None
    return {**suggestion, "fromItemIds": filtered}


def link_suggestions(
    suggestions: dict,
    catalog: dict,
) -> SuggestionValidationResult:
    """모든 제안에 경험 id를 연결하고 유효하지 않은 제안을 드롭합니다.

    LLM이 출력한 신규/심화 제안 각각에 대해:

    - ``coversItemIds`` / ``fromItemIds`` 에서 카탈로그에 없는 id를 제거합니다.
    - 유효 id가 0개가 된 제안은 드롭합니다.

    **기능명세 참조**

    - F-06. 개인화 결과 — ``coversItemIds`` 로 사용자의 선택 경험과 신규 제안을
      대조합니다. ``personalize.ts::groundedSuggestionIds`` 가 이 id들을 소비합니다.
    - F-07. 역매칭 — ``fromItemIds`` 로 전제 경험이 있는 심화 제안을 찾아
      회사들을 3단계(fit / step / far)로 분류합니다.

    Args:
        suggestions: ``{"new": [...], "deepen": [...]}`` 형태의 dict.
        catalog: ``data/experience.json`` 전체를 파싱한 dict.

    Returns:
        :class:`SuggestionValidationResult` — 유효 제안과 드롭된 제안 목록.
    """
    valid_ids = load_experience_ids(catalog)

    linked_new: list[dict] = []
    dropped_new: list[dict] = []
    for s in suggestions.get("new", []):
        result = link_new_suggestion(s, valid_ids)
        if result is not None:
            linked_new.append(result)
        else:
            dropped_new.append(s)

    linked_deepen: list[dict] = []
    dropped_deepen: list[dict] = []
    for s in suggestions.get("deepen", []):
        result = link_deepen_suggestion(s, valid_ids)
        if result is not None:
            linked_deepen.append(result)
        else:
            dropped_deepen.append(s)

    return SuggestionValidationResult(
        new=linked_new,
        deepen=linked_deepen,
        dropped_new=dropped_new,
        dropped_deepen=dropped_deepen,
    )
