"""experience_linker 단위 테스트.

검증 대상:
- load_experience_ids: groups → item id 집합 추출
- filter_experience_ids: 유효하지 않은 id 제거, 순서 보존
- link_new_suggestion: coversItemIds 검증 / 드롭 판단
- link_deepen_suggestion: fromItemIds 검증 / 드롭 판단
- link_suggestions: 전체 파이프라인 — 유효/드롭 분리

F-06 개인화 결과 및 F-07 역매칭에서 이 로직을 소비하므로,
잘못된 id가 통과하면 화면 로직이 엉뚱한 결과를 보여줄 수 있습니다.
"""

from __future__ import annotations

from career_compass_pipeline.experience_linker import (
    SuggestionValidationResult,
    filter_experience_ids,
    link_deepen_suggestion,
    link_new_suggestion,
    link_suggestions,
    load_experience_ids,
)

# ── 픽스처 ─────────────────────────────────────────────────────────────────────

MINIMAL_CATALOG: dict = {
    "version": 2,
    "groups": [
        {
            "id": "project-kind",
            "title": "무엇을 만들어 봤나요",
            "items": [
                {"id": "crud", "label": "CRUD 웹서비스"},
                {"id": "realtime", "label": "실시간 통신"},
                {"id": "big-data", "label": "대용량 데이터"},
            ],
        },
        {
            "id": "backend",
            "title": "서버·백엔드",
            "appliesTo": ["backend"],
            "items": [
                {"id": "rest-api", "label": "REST API 설계"},
                {"id": "db-design", "label": "데이터베이스 설계"},
                {"id": "concurrency", "label": "동시성 제어"},
            ],
        },
    ],
    "levels": [
        {"id": "solo", "step": "", "title": "혼자 만들어 봄", "description": ""},
        {"id": "team", "step": "", "title": "팀 프로젝트", "description": ""},
    ],
}

VALID_IDS = {"crud", "realtime", "big-data", "rest-api", "db-design", "concurrency"}


def _new(covers: list[str], sid: str = "n1") -> dict:
    """테스트용 NewSuggestion dict."""
    return {
        "id": sid,
        "title": "테스트 신규 제안",
        "body": "본문",
        "steps": ["step A"],
        "domainId": "dom-foo",
        "coversItemIds": covers,
        "evidenceIds": ["ev-001"],
    }


def _deepen(froms: list[str], sid: str = "d1") -> dict:
    """테스트용 DeepenSuggestion dict."""
    return {
        "id": sid,
        "from": "이것을 만들었다면",
        "to": "저것을 해보세요",
        "body": "본문",
        "steps": ["step B"],
        "domainId": "dom-bar",
        "fromItemIds": froms,
        "evidenceIds": ["ev-002"],
    }


# ── load_experience_ids ────────────────────────────────────────────────────────


def test_load_extracts_all_item_ids() -> None:
    ids = load_experience_ids(MINIMAL_CATALOG)
    assert ids == VALID_IDS


def test_load_excludes_level_ids() -> None:
    """levels.id는 item id가 아니므로 결과에 포함되지 않아야 합니다."""
    ids = load_experience_ids(MINIMAL_CATALOG)
    assert "solo" not in ids
    assert "team" not in ids


def test_load_empty_catalog() -> None:
    assert load_experience_ids({}) == set()


def test_load_catalog_without_groups() -> None:
    assert load_experience_ids({"groups": []}) == set()


def test_load_skips_items_without_id() -> None:
    catalog = {
        "groups": [
            {
                "id": "g",
                "items": [
                    {"id": "valid-id", "label": "ok"},
                    {"label": "no id field"},
                    {"id": "", "label": "empty id"},
                ],
            }
        ]
    }
    assert load_experience_ids(catalog) == {"valid-id"}


# ── filter_experience_ids ──────────────────────────────────────────────────────


def test_filter_keeps_valid_ids() -> None:
    result = filter_experience_ids(["crud", "rest-api"], VALID_IDS)
    assert result == ["crud", "rest-api"]


def test_filter_removes_invalid_ids() -> None:
    result = filter_experience_ids(["crud", "nonexistent", "rest-api"], VALID_IDS)
    assert result == ["crud", "rest-api"]


def test_filter_all_invalid_returns_empty() -> None:
    result = filter_experience_ids(["ghost", "phantom"], VALID_IDS)
    assert result == []


def test_filter_preserves_order() -> None:
    ids = ["concurrency", "crud", "db-design"]
    result = filter_experience_ids(ids, VALID_IDS)
    assert result == ids


def test_filter_empty_input() -> None:
    assert filter_experience_ids([], VALID_IDS) == []


# ── link_new_suggestion ────────────────────────────────────────────────────────


def test_new_valid_ids_pass_through() -> None:
    s = _new(["crud", "rest-api"])
    result = link_new_suggestion(s, VALID_IDS)
    assert result is not None
    assert result["coversItemIds"] == ["crud", "rest-api"]


def test_new_mixed_ids_removes_invalid() -> None:
    s = _new(["crud", "INVALID"])
    result = link_new_suggestion(s, VALID_IDS)
    assert result is not None
    assert result["coversItemIds"] == ["crud"]


def test_new_all_invalid_returns_none() -> None:
    """coversItemIds가 모두 카탈로그에 없으면 드롭(None)."""
    s = _new(["ghost1", "ghost2"])
    assert link_new_suggestion(s, VALID_IDS) is None


def test_new_empty_covers_returns_none() -> None:
    """coversItemIds가 빈 리스트면 드롭(None)."""
    s = _new([])
    assert link_new_suggestion(s, VALID_IDS) is None


def test_new_missing_covers_key_returns_none() -> None:
    """coversItemIds 키가 없으면 드롭(None)."""
    s = {
        "id": "n1",
        "title": "no covers",
        "body": "",
        "steps": [],
        "domainId": "dom-x",
        "evidenceIds": [],
    }
    assert link_new_suggestion(s, VALID_IDS) is None


def test_new_does_not_mutate_input() -> None:
    """입력 dict가 변경되지 않아야 합니다."""
    s = _new(["crud", "ghost"])
    original = s.copy()
    link_new_suggestion(s, VALID_IDS)
    assert s == original


def test_new_preserves_other_fields() -> None:
    """coversItemIds만 수정하고 나머지 필드는 그대로 유지합니다."""
    s = _new(["crud", "ghost"])
    result = link_new_suggestion(s, VALID_IDS)
    assert result is not None
    assert result["id"] == s["id"]
    assert result["title"] == s["title"]
    assert result["evidenceIds"] == s["evidenceIds"]


# ── link_deepen_suggestion ─────────────────────────────────────────────────────


def test_deepen_valid_ids_pass_through() -> None:
    s = _deepen(["db-design", "concurrency"])
    result = link_deepen_suggestion(s, VALID_IDS)
    assert result is not None
    assert result["fromItemIds"] == ["db-design", "concurrency"]


def test_deepen_mixed_ids_removes_invalid() -> None:
    s = _deepen(["db-design", "BAD_ID"])
    result = link_deepen_suggestion(s, VALID_IDS)
    assert result is not None
    assert result["fromItemIds"] == ["db-design"]


def test_deepen_all_invalid_returns_none() -> None:
    """fromItemIds가 모두 카탈로그에 없으면 드롭(None)."""
    s = _deepen(["no-such", "also-not"])
    assert link_deepen_suggestion(s, VALID_IDS) is None


def test_deepen_empty_from_returns_none() -> None:
    """fromItemIds가 빈 리스트면 전제 경험이 없어 드롭(None)."""
    s = _deepen([])
    assert link_deepen_suggestion(s, VALID_IDS) is None


def test_deepen_missing_from_key_returns_none() -> None:
    """fromItemIds 키가 없으면 드롭(None)."""
    s = {
        "id": "d1",
        "from": "A",
        "to": "B",
        "body": "",
        "steps": [],
        "domainId": "dom-y",
        "evidenceIds": [],
    }
    assert link_deepen_suggestion(s, VALID_IDS) is None


def test_deepen_does_not_mutate_input() -> None:
    s = _deepen(["db-design", "ghost"])
    original = s.copy()
    link_deepen_suggestion(s, VALID_IDS)
    assert s == original


# ── link_suggestions (통합) ────────────────────────────────────────────────────


def test_link_suggestions_all_valid() -> None:
    suggestions = {
        "new": [_new(["crud"]), _new(["realtime"], "n2")],
        "deepen": [_deepen(["rest-api"]), _deepen(["concurrency"], "d2")],
    }
    result = link_suggestions(suggestions, MINIMAL_CATALOG)

    assert len(result["new"]) == 2
    assert len(result["deepen"]) == 2
    assert result["dropped_new"] == []
    assert result["dropped_deepen"] == []


def test_link_suggestions_drops_invalid_new() -> None:
    suggestions = {
        "new": [
            _new(["crud"], "n-ok"),
            _new(["no-such-item"], "n-bad"),
        ],
        "deepen": [],
    }
    result = link_suggestions(suggestions, MINIMAL_CATALOG)

    assert [s["id"] for s in result["new"]] == ["n-ok"]
    assert [s["id"] for s in result["dropped_new"]] == ["n-bad"]


def test_link_suggestions_drops_invalid_deepen() -> None:
    suggestions = {
        "new": [],
        "deepen": [
            _deepen(["db-design"], "d-ok"),
            _deepen(["NOT_REAL"], "d-bad"),
        ],
    }
    result = link_suggestions(suggestions, MINIMAL_CATALOG)

    assert [s["id"] for s in result["deepen"]] == ["d-ok"]
    assert [s["id"] for s in result["dropped_deepen"]] == ["d-bad"]


def test_link_suggestions_partial_ids_filtered() -> None:
    """일부만 유효하면 드롭이 아니라 valid id만 남겨야 합니다."""
    suggestions = {
        "new": [_new(["crud", "GHOST", "realtime"])],
        "deepen": [_deepen(["rest-api", "PHANTOM"])],
    }
    result = link_suggestions(suggestions, MINIMAL_CATALOG)

    assert result["new"][0]["coversItemIds"] == ["crud", "realtime"]
    assert result["deepen"][0]["fromItemIds"] == ["rest-api"]


def test_link_suggestions_empty_input() -> None:
    result = link_suggestions({"new": [], "deepen": []}, MINIMAL_CATALOG)
    assert result == SuggestionValidationResult(
        new=[], deepen=[], dropped_new=[], dropped_deepen=[]
    )


def test_link_suggestions_missing_keys_tolerated() -> None:
    """new / deepen 키가 없어도 빈 목록으로 처리합니다."""
    result = link_suggestions({}, MINIMAL_CATALOG)
    assert result["new"] == []
    assert result["deepen"] == []


def test_link_suggestions_empty_catalog_drops_all() -> None:
    """카탈로그가 비어 있으면 모든 제안이 드롭됩니다."""
    suggestions = {
        "new": [_new(["crud"])],
        "deepen": [_deepen(["rest-api"])],
    }
    result = link_suggestions(suggestions, {"groups": [], "levels": []})

    assert result["new"] == []
    assert result["deepen"] == []
    assert len(result["dropped_new"]) == 1
    assert len(result["dropped_deepen"]) == 1


def test_link_suggestions_result_type_fields() -> None:
    """반환값이 SuggestionValidationResult의 네 키를 모두 가집니다."""
    result = link_suggestions({}, MINIMAL_CATALOG)
    assert set(result.keys()) == {"new", "deepen", "dropped_new", "dropped_deepen"}
