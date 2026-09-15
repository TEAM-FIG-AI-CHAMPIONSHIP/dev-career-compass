"""build_domains() 및 내부 헬퍼 테스트.

검증 축:
 - domain/evidence id 생성 결정성·포맷
 - role 필터링 (일치·불일치·교집합)
 - 중복 article_id 제거
 - 출처별 counts 집계
 - min_evidence 임계값
 - 빈 입력 처리
 - domain id 충돌 방지
 - counts 합계 == evidenceIds 길이 불변식
"""

from __future__ import annotations

import pytest

from career_compass_pipeline.aggregate import (
    Domain,
    area_to_domain_id,
    article_id_to_evidence_id,
    build_domains,
)

# ── 테스트용 헬퍼 ─────────────────────────────────────────────────────────────


def _area(
    *,
    id: str = "oliveyoung-01",
    area_name: str = "재고 정합성·품절 반영",
    evidence: list[dict] | None = None,
) -> dict:
    """최소 Area dict를 만듭니다."""
    return {
        "id": id,
        "area_name": area_name,
        "evidence": evidence if evidence is not None else [],
    }


def _ev(article_id: str, roles: list[str], *, url: str = "") -> dict:
    """최소 evidence 항목을 만듭니다."""
    return {
        "article_id": article_id,
        "title": f"title-{article_id}",
        "url": url or f"https://example.com/{article_id}",
        "roles": roles,
    }


def _total_counts(domain: Domain) -> int:
    return sum(domain["counts"].values())


# ── area_to_domain_id ─────────────────────────────────────────────────────────


def test_domain_id_uses_area_id_field() -> None:
    area = {"id": "oliveyoung-01", "area_name": "재고 정합성"}
    assert area_to_domain_id(area) == "dom-oliveyoung-01"


def test_domain_id_starts_with_dom_prefix() -> None:
    area = {"id": "socar-03"}
    assert area_to_domain_id(area).startswith("dom-")


def test_domain_id_fallback_without_id_field() -> None:
    # area_name이 한글이어도 에러 없이 문자열이 반환된다.
    area = {"area_name": "배포 자동화"}
    result = area_to_domain_id(area)
    assert isinstance(result, str)
    assert result.startswith("dom-")
    assert len(result) > len("dom-")


def test_domain_id_fallback_empty_name() -> None:
    area: dict = {}  # id도 area_name도 없음
    result = area_to_domain_id(area)
    assert result.startswith("dom-")


# ── article_id_to_evidence_id ─────────────────────────────────────────────────


def test_evidence_id_format() -> None:
    assert article_id_to_evidence_id("40ca85f39b5dc7ec") == "ev-40ca85f39b5dc7ec"


def test_evidence_id_starts_with_ev_prefix() -> None:
    assert article_id_to_evidence_id("abc123").startswith("ev-")


def test_evidence_id_is_deterministic() -> None:
    assert article_id_to_evidence_id("xyz") == article_id_to_evidence_id("xyz")


# ── build_domains: 빈 입력 ────────────────────────────────────────────────────


def test_empty_areas_returns_empty() -> None:
    assert build_domains([], "backend") == []


def test_area_with_no_evidence_excluded() -> None:
    assert build_domains([_area(evidence=[])], "backend") == []


def test_area_with_evidence_but_no_role_match_excluded() -> None:
    areas = [_area(evidence=[_ev("a1", ["frontend"])])]
    assert build_domains(areas, "backend") == []


# ── build_domains: 기본 변환 ──────────────────────────────────────────────────


def test_basic_domain_created() -> None:
    areas = [
        _area(
            id="oliveyoung-01",
            area_name="재고 정합성·품절 반영",
            evidence=[
                _ev("aaa", ["backend", "data-ai"]),
                _ev("bbb", ["backend"]),
            ],
        )
    ]
    domains = build_domains(areas, "backend")

    assert len(domains) == 1
    d = domains[0]
    assert d["id"] == "dom-oliveyoung-01"
    assert d["label"] == "재고 정합성·품절 반영"
    assert d["counts"] == {"blog": 2}
    assert d["evidenceIds"] == ["ev-aaa", "ev-bbb"]


def test_evidence_not_matching_role_excluded_from_ids() -> None:
    areas = [
        _area(
            evidence=[
                _ev("x1", ["frontend"]),
                _ev("x2", ["backend"]),
                _ev("x3", ["frontend", "mobile"]),
            ]
        )
    ]
    domains = build_domains(areas, "backend")

    assert domains[0]["evidenceIds"] == ["ev-x2"]


def test_evidence_order_preserved() -> None:
    areas = [
        _area(
            evidence=[
                _ev("c", ["backend"]),
                _ev("a", ["backend"]),
                _ev("b", ["backend"]),
            ]
        )
    ]
    domains = build_domains(areas, "backend")
    assert domains[0]["evidenceIds"] == ["ev-c", "ev-a", "ev-b"]


# ── build_domains: role 필터링 ────────────────────────────────────────────────


def test_only_matching_role_articles_count() -> None:
    areas = [
        _area(
            evidence=[
                _ev("m1", ["backend"]),
                _ev("m2", ["backend", "mobile"]),
                _ev("m3", ["mobile"]),       # backend 아님 → 제외
                _ev("m4", ["data-ai"]),      # backend 아님 → 제외
            ]
        )
    ]
    domains = build_domains(areas, "backend")
    assert domains[0]["counts"] == {"blog": 2}
    assert len(domains[0]["evidenceIds"]) == 2


def test_multi_role_article_counts_once_per_domain() -> None:
    """backend+frontend 둘 다 가진 글은 backend 필터 시 1건으로 셉니다."""
    areas = [
        _area(evidence=[_ev("multi", ["backend", "frontend"])])
    ]
    domains = build_domains(areas, "backend")
    assert domains[0]["counts"] == {"blog": 1}


# ── build_domains: 중복 article_id 제거 ───────────────────────────────────────


def test_duplicate_article_id_deduplicated() -> None:
    areas = [
        _area(
            evidence=[
                _ev("dup", ["backend"]),
                _ev("dup", ["backend"]),   # 중복
                _ev("uniq", ["backend"]),
            ]
        )
    ]
    domains = build_domains(areas, "backend")

    assert domains[0]["counts"] == {"blog": 2}
    assert domains[0]["evidenceIds"] == ["ev-dup", "ev-uniq"]


def test_duplicate_keeps_first_occurrence() -> None:
    """첫 번째 등장이 유지됩니다 (소스 타입 포함)."""
    areas = [
        _area(
            evidence=[
                _ev("dup", ["backend"]),  # 첫 번째 → blog (default)
                _ev("dup", ["backend"]),  # 무시됨
            ]
        )
    ]
    source_by_id = {"dup": "job"}  # 첫 번째 ev는 job이어야 하지만…
    # article_id → source_by_id 매핑은 article_id 기준이라
    # 중복 제거 후 남은 하나에만 적용된다.
    domains = build_domains(areas, "backend", source_by_id=source_by_id)
    # "dup"이 1건, source="job". blog는 항상 0으로 포함됨.
    assert domains[0]["counts"] == {"blog": 0, "job": 1}


# ── build_domains: source_by_id (출처 지정) ───────────────────────────────────


def test_default_source_is_blog() -> None:
    areas = [_area(evidence=[_ev("a1", ["backend"]), _ev("a2", ["backend"])])]
    domains = build_domains(areas, "backend")
    assert domains[0]["counts"] == {"blog": 2}


def test_source_by_id_overrides_default() -> None:
    areas = [
        _area(
            evidence=[
                _ev("a1", ["backend"]),
                _ev("a2", ["backend"]),
                _ev("a3", ["backend"]),
            ]
        )
    ]
    source = {"a1": "blog", "a2": "job", "a3": "job"}
    domains = build_domains(areas, "backend", source_by_id=source)

    assert domains[0]["counts"] == {"blog": 1, "job": 2}


def test_unlisted_id_in_source_by_id_defaults_to_blog() -> None:
    areas = [_area(evidence=[_ev("unknown", ["backend"])])]
    domains = build_domains(areas, "backend", source_by_id={"other_id": "job"})
    assert domains[0]["counts"] == {"blog": 1}


def test_source_by_id_none_behaves_same_as_empty_dict() -> None:
    areas = [_area(evidence=[_ev("a", ["backend"])])]
    result_none = build_domains(areas, "backend", source_by_id=None)
    result_empty = build_domains(areas, "backend", source_by_id={})
    assert result_none == result_empty


def test_blog_key_always_present_even_if_all_evidence_is_job() -> None:
    """EvidenceCounts.blog는 required — job 데이터만 있어도 blog 키가 존재해야 합니다.

    DomainChips.tsx가 domain.counts.blog를 직접 참조하므로,
    blog 키가 없으면 화면에 'undefined'가 찍힙니다.
    """
    areas = [_area(evidence=[_ev("j1", ["backend"]), _ev("j2", ["backend"])])]
    domains = build_domains(
        areas, "backend", source_by_id={"j1": "job", "j2": "job"}
    )
    assert len(domains) == 1
    assert "blog" in domains[0]["counts"], "blog 키가 항상 포함되어야 합니다"
    assert domains[0]["counts"]["blog"] == 0
    assert domains[0]["counts"]["job"] == 2


def test_blog_key_zero_when_no_blog_evidence() -> None:
    """blog 근거가 0건이면 counts["blog"] == 0."""
    areas = [_area(evidence=[_ev("j1", ["backend"])])]
    domains = build_domains(areas, "backend", source_by_id={"j1": "job"})
    assert domains[0]["counts"] == {"blog": 0, "job": 1}


# ── build_domains: min_evidence 임계값 ───────────────────────────────────────


def test_min_evidence_1_keeps_single_evidence_area() -> None:
    areas = [_area(evidence=[_ev("e1", ["backend"])])]
    assert len(build_domains(areas, "backend", min_evidence=1)) == 1


def test_min_evidence_2_excludes_single_evidence_area() -> None:
    areas = [_area(evidence=[_ev("e1", ["backend"])])]
    assert build_domains(areas, "backend", min_evidence=2) == []


def test_min_evidence_filters_small_areas_keeps_large() -> None:
    areas = [
        _area(id="small-01", evidence=[_ev("s1", ["backend"])]),
        _area(
            id="large-01",
            evidence=[_ev("l1", ["backend"]), _ev("l2", ["backend"])],
        ),
    ]
    domains = build_domains(areas, "backend", min_evidence=2)

    assert len(domains) == 1
    assert domains[0]["id"] == "dom-large-01"


def test_min_evidence_0_includes_area_with_no_role_evidence() -> None:
    # min_evidence=0이면 role 근거가 0건인 Area도 포함
    areas = [_area(evidence=[_ev("e1", ["frontend"])])]
    domains = build_domains(areas, "backend", min_evidence=0)
    assert len(domains) == 1
    assert domains[0]["evidenceIds"] == []
    assert domains[0]["counts"] == {"blog": 0}  # 근거가 없어도 blog 키는 항상 포함


# ── build_domains: 여러 Area ──────────────────────────────────────────────────


def test_multiple_areas_all_included() -> None:
    areas = [
        _area(id="co-01", area_name="영역 A", evidence=[_ev("e1", ["backend"])]),
        _area(id="co-02", area_name="영역 B", evidence=[_ev("e2", ["backend"])]),
    ]
    domains = build_domains(areas, "backend")

    assert len(domains) == 2
    ids = {d["id"] for d in domains}
    assert ids == {"dom-co-01", "dom-co-02"}


def test_some_areas_excluded_by_role() -> None:
    areas = [
        _area(id="be-01", evidence=[_ev("b1", ["backend"])]),
        _area(id="fe-01", evidence=[_ev("f1", ["frontend"])]),   # 제외
        _area(id="be-02", evidence=[_ev("b2", ["backend"])]),
    ]
    domains = build_domains(areas, "backend")

    assert len(domains) == 2
    ids = {d["id"] for d in domains}
    assert "dom-be-01" in ids
    assert "dom-be-02" in ids
    assert "dom-fe-01" not in ids


def test_area_order_preserved_in_output() -> None:
    areas = [
        _area(id="c-03", evidence=[_ev("e3", ["backend"])]),
        _area(id="c-01", evidence=[_ev("e1", ["backend"])]),
        _area(id="c-02", evidence=[_ev("e2", ["backend"])]),
    ]
    domains = build_domains(areas, "backend")
    assert [d["id"] for d in domains] == ["dom-c-03", "dom-c-01", "dom-c-02"]


# ── build_domains: domain id 충돌 방지 ───────────────────────────────────────


def test_collision_when_areas_have_no_id() -> None:
    """id 필드가 없는 Area끼리 area_name이 달라도 slugify 결과가 같을 수 있다.
    충돌 시 자동으로 숫자 접미사가 붙어 고유성이 보장됩니다."""
    # 둘 다 id 없이 한글 이름만 → 같은 slug로 충돌 가능
    areas = [
        {"area_name": "영역 가", "evidence": [_ev("e1", ["backend"])]},
        {"area_name": "영역 나", "evidence": [_ev("e2", ["backend"])]},
    ]
    domains = build_domains(areas, "backend")
    domain_ids = [d["id"] for d in domains]
    assert len(domain_ids) == len(set(domain_ids)), "domain id 중복 발생"


def test_explicit_collision_resolved_with_suffix() -> None:
    """가상으로 동일한 id를 가진 두 Area의 충돌을 해결합니다."""
    # 같은 id를 가진 Area 두 개 (실제로는 발생하면 안 되지만 방어)
    areas = [
        _area(id="dup-01", evidence=[_ev("e1", ["backend"])]),
        _area(id="dup-01", evidence=[_ev("e2", ["backend"])]),
    ]
    domains = build_domains(areas, "backend")
    assert len(domains) == 2
    ids = [d["id"] for d in domains]
    assert ids[0] == "dom-dup-01"
    assert ids[1] == "dom-dup-01-2"


# ── 불변식: counts 합계 == evidenceIds 길이 ──────────────────────────────────


@pytest.mark.parametrize(
    "evidence,source_by_id",
    [
        (
            [_ev("a1", ["backend"]), _ev("a2", ["backend"]), _ev("a3", ["backend"])],
            {"a1": "blog", "a2": "blog", "a3": "job"},
        ),
        (
            [_ev("b1", ["backend"])],
            {},
        ),
        (
            [_ev("c1", ["backend"]), _ev("c2", ["backend"])],
            {"c1": "job", "c2": "job"},
        ),
    ],
)
def test_counts_total_equals_evidence_ids_length(
    evidence: list[dict], source_by_id: dict
) -> None:
    """counts 합계와 evidenceIds 길이는 항상 같아야 합니다."""
    areas = [_area(evidence=evidence)]
    domains = build_domains(areas, "backend", source_by_id=source_by_id)
    for d in domains:
        assert _total_counts(d) == len(d["evidenceIds"]), (
            f"counts 합계({_total_counts(d)}) != "
            f"evidenceIds 길이({len(d['evidenceIds'])})"
        )


# ── 실제 데이터 모양 시뮬레이션 ──────────────────────────────────────────────


def test_realistic_company_area_data() -> None:
    """group1_areas.json 형태의 실제 데이터와 유사한 구조로 검증합니다."""
    areas = [
        {
            "id": "socar-01",
            "area_name": "디자인 시스템과 크로스플랫폼 앱 프레임워크 설계",
            "article_count": 4,
            "evidence": [
                {
                    "article_id": "40ca85f39b5dc7ec",
                    "title": "쏘카 디자인 시스템 2.0 개발기 2편",
                    "url": "https://tech.socar.kr/fe/socar-frame2-web-part2",
                    "similarity": 0.9114,
                    "roles": ["backend", "frontend", "data-ai"],
                },
                {
                    "article_id": "f8ca35d83c532384",
                    "title": "쏘카 디자인 시스템 2.0 개발기 1편",
                    "url": "https://tech.socar.kr/fe/socar-frame2-web",
                    "similarity": 0.9125,
                    "roles": ["backend", "frontend"],
                },
                {
                    "article_id": "0a93ce2313cbe4b3",
                    "title": "쏘카프레임 - 블루투스 모듈",
                    "url": "https://tech.socar.kr/socarframe/socarframe-bluetooth",
                    "similarity": 0.9176,
                    "roles": ["backend", "mobile", "data-ai"],
                },
                {
                    "article_id": "c86984a9b70b3710",
                    "title": "쏘카프레임 - 앱 프레임워크와 개발자 경험",
                    "url": "https://tech.socar.kr/socarframe/socarframe-introduce",
                    "similarity": 0.8951,
                    "roles": ["backend", "mobile"],
                },
            ],
        }
    ]

    domains = build_domains(areas, "backend")

    assert len(domains) == 1
    d = domains[0]
    assert d["id"] == "dom-socar-01"
    assert d["label"] == "디자인 시스템과 크로스플랫폼 앱 프레임워크 설계"
    # backend role 4건 모두 포함
    assert d["counts"] == {"blog": 4}
    assert len(d["evidenceIds"]) == 4
    # 모두 ev- 접두사
    for eid in d["evidenceIds"]:
        assert eid.startswith("ev-")

    # frontend 필터 시: frontend role을 가진 글만
    fe_domains = build_domains(areas, "frontend")
    fe_eids = fe_domains[0]["evidenceIds"]
    assert "ev-40ca85f39b5dc7ec" in fe_eids
    assert "ev-f8ca35d83c532384" in fe_eids
    # mobile-only 글은 제외
    assert "ev-c86984a9b70b3710" not in fe_eids
