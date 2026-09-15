"""게시 직전 Analysis의 구조·참조 무결성을 검증합니다.

기능명세 연결: F-02/F-03 — 화면(``apps/web/src/types/data.ts``)이 읽는
``Analysis`` 형식을 기준으로, 제안·영역·근거 사이의 id 참조가 전부 닫혀
있는지와 제안 개수 하한을 게시 전에 코드로 확인합니다.

#107(근거 문장·문서 실재 검증)과 역할이 다릅니다:
  - #107: 제안에 적힌 근거가 원문 내용과 맞는지 → 안 맞으면 그 제안(문장) 삭제
  - 이 모듈: #107이 걸러내고 남긴 JSON이 화면·게시 계약상 참조가 전부
    닫혀 있는지 → #107 출력을 그대로 입력받아도 동작합니다

``pipeline/src/career_compass_pipeline/contracts.py`` 와는 검증 대상 문서가
다릅니다 (contracts.py는 packages/contracts의 role/experience/company-project
스키마 문서를, 이 모듈은 화면이 읽는 Analysis 형식을 검증합니다). 두 문서
형식이 아직 갈라져 있다는 점은 docs/work-status.md의
"계약이 둘로 갈라져 있습니다"를 참고하세요 — 이 모듈은 그 중 화면 쪽 형식을
우선합니다.

LLM 호출 없음, 결정적(deterministic) 검증.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

JsonObject = Mapping[str, Any]

# 기능명세: "신규 제안 2~3개", "심화 제안 3개 이상" 에서 하한만 취합니다.
# 상한(신규 3개)은 참조 무결성과 무관한 생성 단계의 몫이라 여기서는 강제하지
# 않습니다.
MIN_NEW_SUGGESTIONS = 2
MIN_DEEPEN_SUGGESTIONS = 3


class AnalysisValidationError(ValueError):
    """Analysis가 화면·게시 계약상 참조 무결성을 만족하지 못할 때 발생합니다."""


# ── 필드·타입 헬퍼 ────────────────────────────────────────────────────────────
# contracts.py와 검증 대상 문서가 다르므로 헬퍼를 공유하지 않고 이 모듈 안에
# 따로 둡니다 — 한쪽 문서 형식이 바뀌어도 다른 쪽 검증이 조용히 영향받지
# 않게 하기 위해서입니다.


def _mapping(value: Any, label: str, errors: list[str]) -> JsonObject:
    if not isinstance(value, Mapping):
        errors.append(f"{label} must be an object")
        return {}
    return value


def _string(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty string")
        return ""
    return value


def _records(value: Any, label: str, errors: list[str]) -> list[JsonObject]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        errors.append(f"{label} must be an array")
        return []

    records: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"{label}[{index}] must be an object")
            continue
        records.append(item)
    return records


def _string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        errors.append(f"{label} must be an array")
        return []

    ids: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        ids.append(item)
    return ids


def _index_unique(
    records: Iterable[JsonObject], label: str, errors: list[str]
) -> dict[str, JsonObject]:
    """레코드를 ``id`` 필드 기준으로 색인합니다.

    id가 없거나 중복이면 그 레코드는 색인에서 빠지고 errors에 남습니다 —
    이후 그 id를 참조하는 다른 검증은 "unknown id"로 자연히 함께 실패합니다.
    """
    indexed: dict[str, JsonObject] = {}
    for index, record in enumerate(records):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{label}[{index}] has no valid id")
            continue
        if record_id in indexed:
            errors.append(f"duplicate {label} id: {record_id}")
            continue
        indexed[record_id] = record
    return indexed


def _experience_item_ids(experience_catalog: JsonObject, errors: list[str]) -> set[str]:
    """``data/experience.json`` 형식에서 item id 전체를 모읍니다.

    그룹의 ``appliesTo``(직무 제한)는 화면 노출 범위일 뿐 참조 유효성과는
    무관하므로 구분하지 않고 전체 그룹을 대상으로 합니다.
    """
    item_ids: set[str] = set()
    groups = _records(experience_catalog.get("groups"), "experience_catalog.groups", errors)
    for group_index, group in enumerate(groups):
        items = _records(group.get("items"), f"experience_catalog.groups[{group_index}].items", errors)
        for item in items:
            item_id = item.get("id")
            if isinstance(item_id, str) and item_id:
                item_ids.add(item_id)
    return item_ids


# ── 개별 섹션 검증 ────────────────────────────────────────────────────────────


def _validate_evidence(
    analysis: JsonObject, errors: list[str]
) -> dict[str, JsonObject]:
    records = _records(analysis.get("evidence"), "evidence", errors)
    evidence_by_id = _index_unique(records, "evidence", errors)

    for evidence_id, evidence in evidence_by_id.items():
        _string(evidence.get("title"), f"evidence {evidence_id}.title", errors)
        _string(evidence.get("url"), f"evidence {evidence_id}.url", errors)
        source = evidence.get("source")
        if source not in ("blog", "job"):
            errors.append(
                f'evidence {evidence_id}.source must be "blog" or "job", got {source!r}'
            )

    return evidence_by_id


def _validate_domains(
    analysis: JsonObject, evidence_by_id: dict[str, JsonObject], errors: list[str]
) -> dict[str, JsonObject]:
    records = _records(analysis.get("domains"), "domains", errors)
    domains_by_id = _index_unique(records, "domain", errors)

    for domain_id, domain in domains_by_id.items():
        _string(domain.get("label"), f"domain {domain_id}.label", errors)

        counts = _mapping(domain.get("counts"), f"domain {domain_id}.counts", errors)
        if not isinstance(counts.get("blog"), int):
            errors.append(f"domain {domain_id}.counts.blog must be an integer")
        if "job" in counts and not isinstance(counts["job"], int):
            errors.append(f"domain {domain_id}.counts.job must be an integer")

        evidence_ids = _string_list(
            domain.get("evidenceIds"), f"domain {domain_id}.evidenceIds", errors
        )
        for evidence_id in evidence_ids:
            if evidence_id not in evidence_by_id:
                errors.append(f"domain {domain_id} references unknown evidence: {evidence_id}")

    return domains_by_id


def _validate_suggestion(
    *,
    label: str,
    suggestion: JsonObject,
    domains_by_id: dict[str, JsonObject],
    evidence_by_id: dict[str, JsonObject],
    experience_item_ids: set[str],
    experience_field: str,
    errors: list[str],
) -> None:
    """``suggestions.new[]`` / ``suggestions.deepen[]`` 항목 하나를 검증합니다.

    두 타입은 경험 참조 필드 이름만 다릅니다
    (``NewSuggestion.coversItemIds`` / ``DeepenSuggestion.fromItemIds``) —
    ``experience_field`` 로 그 차이를 흡수합니다.
    """
    suggestion_id = _string(suggestion.get("id"), f"{label}.id", errors) or f"[{label}]"
    _string(suggestion.get("body"), f"{label} ({suggestion_id}).body", errors)
    _string_list(suggestion.get("steps"), f"{label} ({suggestion_id}).steps", errors)

    domain_id = suggestion.get("domainId")
    if domain_id not in domains_by_id:
        errors.append(f"{label} ({suggestion_id}) references unknown domain: {domain_id}")

    evidence_ids = _string_list(
        suggestion.get("evidenceIds"), f"{label} ({suggestion_id}).evidenceIds", errors
    )
    if not evidence_ids:
        errors.append(f"{label} ({suggestion_id}) has no evidence")
    for evidence_id in evidence_ids:
        if evidence_id not in evidence_by_id:
            errors.append(f"{label} ({suggestion_id}) references unknown evidence: {evidence_id}")

    referenced_item_ids = _string_list(
        suggestion.get(experience_field), f"{label} ({suggestion_id}).{experience_field}", errors
    )
    for item_id in referenced_item_ids:
        if item_id not in experience_item_ids:
            errors.append(
                f"{label} ({suggestion_id}) references unknown experience item: {item_id}"
            )


# ── 공개 진입점 ───────────────────────────────────────────────────────────────


def validate_analysis(
    analysis: JsonObject,
    experience_catalog: JsonObject,
    *,
    min_new_suggestions: int = MIN_NEW_SUGGESTIONS,
    min_deepen_suggestions: int = MIN_DEEPEN_SUGGESTIONS,
) -> None:
    """Analysis 하나가 게시해도 되는 상태인지 확인합니다.

    Args:
        analysis: 화면 ``Analysis`` 타입과 같은 모양의 dict
            (``data/published/{회사}/{직무}.json`` 이 될 문서).
        experience_catalog: ``data/experience.json`` 과 같은 모양의 dict.
        min_new_suggestions: 신규 제안 개수 하한. 미달이면 거부합니다.
        min_deepen_suggestions: 심화 제안 개수 하한. 미달이면 거부합니다.

    검증 항목:
        - 필수 필드·타입: ``company``, ``job``, ``window``, ``domains``,
          ``suggestions``, ``evidence``
        - ``suggestions.*.domainId`` ∈ ``domains[].id``
        - ``suggestions.*.evidenceIds`` ⊆ ``evidence[].id`` 이고 길이 ≥ 1
        - ``domains[].evidenceIds`` ⊆ ``evidence[].id``
        - ``coversItemIds``(신규) / ``fromItemIds``(심화) ⊆ 경험 카탈로그 item id
        - 개수 하한: 신규 ≥ ``min_new_suggestions``, 심화 ≥ ``min_deepen_suggestions``

    Raises:
        AnalysisValidationError: 깨진 필드·참조를 전부 모아 한 번에 알려줍니다.
            메시지는 어떤 항목의 어떤 필드가 왜 깨졌는지를 담습니다.
    """
    errors: list[str] = []

    company = _mapping(analysis.get("company"), "company", errors)
    _string(company.get("slug"), "company.slug", errors)
    _string(company.get("name"), "company.name", errors)

    job = _mapping(analysis.get("job"), "job", errors)
    _string(job.get("slug"), "job.slug", errors)
    _string(job.get("name"), "job.name", errors)

    window = _mapping(analysis.get("window"), "window", errors)
    _string(window.get("from"), "window.from", errors)
    _string(window.get("to"), "window.to", errors)

    evidence_by_id = _validate_evidence(analysis, errors)
    domains_by_id = _validate_domains(analysis, evidence_by_id, errors)
    experience_item_ids = _experience_item_ids(experience_catalog, errors)

    suggestions = _mapping(analysis.get("suggestions"), "suggestions", errors)
    new_suggestions = _records(suggestions.get("new"), "suggestions.new", errors)
    deepen_suggestions = _records(suggestions.get("deepen"), "suggestions.deepen", errors)

    for index, suggestion in enumerate(new_suggestions):
        _validate_suggestion(
            label=f"suggestions.new[{index}]",
            suggestion=suggestion,
            domains_by_id=domains_by_id,
            evidence_by_id=evidence_by_id,
            experience_item_ids=experience_item_ids,
            experience_field="coversItemIds",
            errors=errors,
        )

    for index, suggestion in enumerate(deepen_suggestions):
        _validate_suggestion(
            label=f"suggestions.deepen[{index}]",
            suggestion=suggestion,
            domains_by_id=domains_by_id,
            evidence_by_id=evidence_by_id,
            experience_item_ids=experience_item_ids,
            experience_field="fromItemIds",
            errors=errors,
        )

    if len(new_suggestions) < min_new_suggestions:
        errors.append(
            f"suggestions.new has {len(new_suggestions)} item(s), "
            f"below the minimum of {min_new_suggestions}"
        )
    if len(deepen_suggestions) < min_deepen_suggestions:
        errors.append(
            f"suggestions.deepen has {len(deepen_suggestions)} item(s), "
            f"below the minimum of {min_deepen_suggestions}"
        )

    if errors:
        raise AnalysisValidationError("Invalid Analysis:\n- " + "\n- ".join(errors))
