"""validate_analysis() 테스트 — F-02/F-03 Analysis 참조 무결성.

검증 축:
 - 실제 oliveyoung fixture·experience 카탈로그로 통과 확인
 - 필수 필드·타입 (generatedAt/company/job/window/domains/suggestions/evidence,
   Evidence.publishedAt(빈 문자열 허용), 신규 title, 심화 from/to)
 - suggestions.*.domainId ∈ domains[].id
 - suggestions.*.evidenceIds ⊆ evidence[].id, 길이 ≥ 1
 - domains[].evidenceIds ⊆ evidence[].id
 - coversItemIds(신규) / fromItemIds(심화) ⊆ 경험 카탈로그
 - 제안 개수 하한 (신규 ≥ 2, 심화 ≥ 3)
 - 중복 id(domain/evidence/제안 — 제안은 new·deepen 합친 범위), 잘못된
   source/counts 타입(bool이 int로 오인되지 않는지 포함)
 - 여러 오류가 한 번에 모여 보고됨
 - #107이 제안을 지운 뒤에도(개수가 줄어도) 그대로 동작함
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from career_compass_pipeline.analysis_validation import (
    AnalysisValidationError,
    validate_analysis,
)

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


# ── 테스트용 헬퍼 ─────────────────────────────────────────────────────────────


def _experience_catalog() -> dict:
    return {
        "version": 1,
        "groups": [
            {
                "id": "backend",
                "title": "서버·백엔드",
                "items": [
                    {"id": "rest-api", "label": "REST API"},
                    {"id": "concurrency", "label": "동시성 제어"},
                    {"id": "messaging-queue", "label": "메시징 큐"},
                ],
            }
        ],
        "levels": [],
    }


def _evidence(suffix: str = "1") -> dict:
    return {
        "id": f"ev-{suffix}",
        "title": f"제목 {suffix}",
        "publishedAt": "2026-01-01",
        "source": "blog",
        "url": f"https://example.com/{suffix}",
    }


def _domain(domain_id: str = "dom-1", evidence_ids: tuple[str, ...] = ("ev-1",)) -> dict:
    return {
        "id": domain_id,
        "label": "영역",
        "counts": {"blog": len(evidence_ids)},
        "evidenceIds": list(evidence_ids),
    }


def _new_suggestion(
    suggestion_id: str = "sg-1",
    *,
    domain_id: str = "dom-1",
    evidence_ids: tuple[str, ...] = ("ev-1",),
    covers: tuple[str, ...] = ("rest-api",),
) -> dict:
    return {
        "id": suggestion_id,
        "title": "제목",
        "body": "설명",
        "steps": ["해볼 것"],
        "domainId": domain_id,
        "coversItemIds": list(covers),
        "evidenceIds": list(evidence_ids),
    }


def _deepen_suggestion(
    suggestion_id: str = "sg-d1",
    *,
    domain_id: str = "dom-1",
    evidence_ids: tuple[str, ...] = ("ev-1",),
    from_items: tuple[str, ...] = ("rest-api",),
) -> dict:
    return {
        "id": suggestion_id,
        "from": "REST API를 만들었다면",
        "to": "다음 단계",
        "body": "설명",
        "steps": ["해볼 것"],
        "domainId": domain_id,
        "fromItemIds": list(from_items),
        "evidenceIds": list(evidence_ids),
    }


def _valid_analysis() -> dict:
    """개수 하한(신규 2·심화 3)에 정확히 걸쳐 있는 최소 유효 Analysis."""
    return {
        "company": {"slug": "acme", "name": "에이씨엠이"},
        "job": {"slug": "backend", "name": "서버·백엔드"},
        "generatedAt": "2026-01-01T00:00:00Z",
        "window": {"from": "2025-01-01", "to": "2026-01-01"},
        "domains": [_domain()],
        "suggestions": {
            "new": [_new_suggestion("sg-1"), _new_suggestion("sg-2")],
            "deepen": [
                _deepen_suggestion("sg-d1"),
                _deepen_suggestion("sg-d2"),
                _deepen_suggestion("sg-d3"),
            ],
        },
        "evidence": [_evidence("1")],
    }


# ── 유효한 Analysis ────────────────────────────────────────────────────────────


def test_valid_analysis_passes() -> None:
    validate_analysis(_valid_analysis(), _experience_catalog())


def test_oliveyoung_fixture_passes() -> None:
    """유효한 Analysis 샘플(oliveyoung fixture)은 검증을 통과해야 한다."""
    analysis = load_json(ROOT / "data" / "fixtures" / "oliveyoung" / "backend.json")
    experience_catalog = load_json(ROOT / "data" / "experience.json")

    validate_analysis(analysis, experience_catalog)


# ── 필수 필드·타입 ─────────────────────────────────────────────────────────────


def test_missing_company_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["company"]
    with pytest.raises(AnalysisValidationError, match="company must be an object"):
        validate_analysis(analysis, _experience_catalog())


def test_missing_job_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["job"]
    with pytest.raises(AnalysisValidationError, match="job must be an object"):
        validate_analysis(analysis, _experience_catalog())


def test_missing_window_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["window"]
    with pytest.raises(AnalysisValidationError, match="window must be an object"):
        validate_analysis(analysis, _experience_catalog())


def test_domains_not_a_list_rejected() -> None:
    analysis = _valid_analysis()
    analysis["domains"] = "dom-1"
    with pytest.raises(AnalysisValidationError, match="domains must be an array"):
        validate_analysis(analysis, _experience_catalog())


def test_evidence_not_a_list_rejected() -> None:
    analysis = _valid_analysis()
    analysis["evidence"] = {}
    with pytest.raises(AnalysisValidationError, match="evidence must be an array"):
        validate_analysis(analysis, _experience_catalog())


def test_missing_generated_at_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["generatedAt"]
    with pytest.raises(AnalysisValidationError, match="generatedAt must be a non-empty string"):
        validate_analysis(analysis, _experience_catalog())


def test_evidence_missing_published_at_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["evidence"][0]["publishedAt"]
    with pytest.raises(AnalysisValidationError, match="evidence ev-1.publishedAt must be a string"):
        validate_analysis(analysis, _experience_catalog())


def test_evidence_published_at_empty_string_allowed() -> None:
    """알 수 없는 발행일은 빈 문자열이 정상 상태다 (evidence.py의 문서화된 계약)."""
    analysis = _valid_analysis()
    analysis["evidence"][0]["publishedAt"] = ""
    validate_analysis(analysis, _experience_catalog())


def test_new_suggestion_missing_title_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["suggestions"]["new"][0]["title"]
    with pytest.raises(
        AnalysisValidationError, match=r"suggestions\.new\[0\].*title must be a non-empty string"
    ):
        validate_analysis(analysis, _experience_catalog())


def test_deepen_suggestion_missing_from_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["suggestions"]["deepen"][0]["from"]
    with pytest.raises(
        AnalysisValidationError, match=r"suggestions\.deepen\[0\].*from must be a non-empty string"
    ):
        validate_analysis(analysis, _experience_catalog())


def test_deepen_suggestion_missing_to_rejected() -> None:
    analysis = _valid_analysis()
    del analysis["suggestions"]["deepen"][0]["to"]
    with pytest.raises(
        AnalysisValidationError, match=r"suggestions\.deepen\[0\].*to must be a non-empty string"
    ):
        validate_analysis(analysis, _experience_catalog())


# ── domainId 없음/미존재 ───────────────────────────────────────────────────────


def test_new_suggestion_unknown_domain_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][0]["domainId"] = "dom-nope"
    with pytest.raises(AnalysisValidationError, match="references unknown domain: dom-nope"):
        validate_analysis(analysis, _experience_catalog())


def test_deepen_suggestion_unknown_domain_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["deepen"][0]["domainId"] = "dom-nope"
    with pytest.raises(AnalysisValidationError, match="references unknown domain: dom-nope"):
        validate_analysis(analysis, _experience_catalog())


# ── evidenceId 고아 ────────────────────────────────────────────────────────────


def test_new_suggestion_orphan_evidence_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][0]["evidenceIds"] = ["ev-nope"]
    with pytest.raises(AnalysisValidationError, match="references unknown evidence: ev-nope"):
        validate_analysis(analysis, _experience_catalog())


def test_domain_orphan_evidence_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["domains"][0]["evidenceIds"] = ["ev-nope"]
    with pytest.raises(AnalysisValidationError, match="references unknown evidence: ev-nope"):
        validate_analysis(analysis, _experience_catalog())


# ── 경험 id 미존재 ─────────────────────────────────────────────────────────────


def test_covers_item_id_unknown_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][0]["coversItemIds"] = ["not-a-real-item"]
    with pytest.raises(
        AnalysisValidationError, match="references unknown experience item: not-a-real-item"
    ):
        validate_analysis(analysis, _experience_catalog())


def test_from_item_id_unknown_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["deepen"][0]["fromItemIds"] = ["not-a-real-item"]
    with pytest.raises(
        AnalysisValidationError, match="references unknown experience item: not-a-real-item"
    ):
        validate_analysis(analysis, _experience_catalog())


# ── 근거 0개 제안 ──────────────────────────────────────────────────────────────


def test_new_suggestion_with_no_evidence_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][0]["evidenceIds"] = []
    with pytest.raises(AnalysisValidationError, match=r"suggestions\.new\[0\].*has no evidence"):
        validate_analysis(analysis, _experience_catalog())


def test_deepen_suggestion_with_no_evidence_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["deepen"][0]["evidenceIds"] = []
    with pytest.raises(
        AnalysisValidationError, match=r"suggestions\.deepen\[0\].*has no evidence"
    ):
        validate_analysis(analysis, _experience_catalog())


# ── 개수 하한 ──────────────────────────────────────────────────────────────────


def test_below_min_new_suggestions_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"] = [_new_suggestion("sg-1")]  # 1개, 하한 2 미달
    with pytest.raises(AnalysisValidationError, match=r"suggestions\.new has 1.*below the minimum"):
        validate_analysis(analysis, _experience_catalog())


def test_below_min_deepen_suggestions_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["deepen"] = analysis["suggestions"]["deepen"][:2]  # 2개, 하한 3 미달
    with pytest.raises(
        AnalysisValidationError, match=r"suggestions\.deepen has 2.*below the minimum"
    ):
        validate_analysis(analysis, _experience_catalog())


def test_min_suggestion_counts_are_configurable() -> None:
    """팀 규칙(하한)을 호출부에서 바꿀 수 있어야 한다 — 기본값은 명세의 하한일 뿐."""
    analysis = _valid_analysis()
    analysis["suggestions"]["new"] = [_new_suggestion("sg-1")]

    validate_analysis(analysis, _experience_catalog(), min_new_suggestions=1)


def test_analysis_with_suggestion_removed_by_evidence_check_still_validates() -> None:
    """#107이 근거 불일치 제안을 지운 뒤 남은 개수가 하한 미달이면 이 검증기가 잡아낸다.

    F-03 조건("근거 검증 후 신규 제안이 0개인 조합은 노출하지 않는다")을
    개수 하한 미달 거부로 통일해 처리한다 — 0개든 1개든 하한(2) 미달이면 같은
    경로로 거부된다.
    """
    analysis = _valid_analysis()
    analysis["suggestions"]["new"].pop()  # #107이 하나를 지웠다고 가정 → 1개 남음

    with pytest.raises(AnalysisValidationError, match="below the minimum"):
        validate_analysis(analysis, _experience_catalog())


# ── 중복 id ────────────────────────────────────────────────────────────────────


def test_duplicate_domain_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["domains"].append(deepcopy(analysis["domains"][0]))
    with pytest.raises(AnalysisValidationError, match="duplicate domain id: dom-1"):
        validate_analysis(analysis, _experience_catalog())


def test_duplicate_evidence_id_rejected() -> None:
    analysis = _valid_analysis()
    analysis["evidence"].append(deepcopy(analysis["evidence"][0]))
    with pytest.raises(AnalysisValidationError, match="duplicate evidence id: ev-1"):
        validate_analysis(analysis, _experience_catalog())


def test_duplicate_suggestion_id_across_new_and_deepen_rejected() -> None:
    """제안 id는 React key이자 선택 상태 키라, 신규·심화 사이에도 겹치면 안 된다."""
    analysis = _valid_analysis()
    analysis["suggestions"]["deepen"][0]["id"] = "sg-1"  # 신규 sg-1과 충돌
    with pytest.raises(
        AnalysisValidationError,
        match="duplicate suggestion id across suggestions.new/deepen: sg-1",
    ):
        validate_analysis(analysis, _experience_catalog())


def test_duplicate_suggestion_id_within_new_rejected() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][1]["id"] = "sg-1"
    with pytest.raises(
        AnalysisValidationError,
        match="duplicate suggestion id across suggestions.new/deepen: sg-1",
    ):
        validate_analysis(analysis, _experience_catalog())


# ── source / counts 타입 ───────────────────────────────────────────────────────


def test_evidence_invalid_source_rejected() -> None:
    analysis = _valid_analysis()
    analysis["evidence"][0]["source"] = "news"  # F-02 조건: 뉴스는 MVP 범위 밖
    with pytest.raises(AnalysisValidationError, match='must be "blog" or "job"'):
        validate_analysis(analysis, _experience_catalog())


def test_domain_counts_missing_blog_key_rejected() -> None:
    """EvidenceCounts.blog는 required — 없으면 DomainChips.tsx가 undefined를 그린다."""
    analysis = _valid_analysis()
    del analysis["domains"][0]["counts"]["blog"]
    with pytest.raises(AnalysisValidationError, match="counts.blog must be an integer"):
        validate_analysis(analysis, _experience_catalog())


def test_domain_counts_blog_boolean_rejected() -> None:
    """bool은 int의 서브클래스라 isinstance만으로는 counts.blog: true를 걸러내지 못한다."""
    analysis = _valid_analysis()
    analysis["domains"][0]["counts"]["blog"] = True
    with pytest.raises(AnalysisValidationError, match="counts.blog must be an integer"):
        validate_analysis(analysis, _experience_catalog())


def test_domain_counts_job_boolean_rejected() -> None:
    analysis = _valid_analysis()
    analysis["domains"][0]["counts"]["job"] = False
    with pytest.raises(AnalysisValidationError, match="counts.job must be an integer"):
        validate_analysis(analysis, _experience_catalog())


# ── 여러 오류가 한 번에 모임 ────────────────────────────────────────────────────


def test_multiple_errors_reported_together() -> None:
    analysis = _valid_analysis()
    analysis["suggestions"]["new"][0]["domainId"] = "dom-nope"
    analysis["suggestions"]["new"][1]["evidenceIds"] = []

    with pytest.raises(AnalysisValidationError) as excinfo:
        validate_analysis(analysis, _experience_catalog())

    message = str(excinfo.value)
    assert "references unknown domain: dom-nope" in message
    assert "has no evidence" in message
