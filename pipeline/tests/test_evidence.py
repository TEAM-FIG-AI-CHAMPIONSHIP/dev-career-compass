"""build_evidence_catalog() 테스트 — F-04. 근거 타임라인.

검증 축:
 - role 필터링 (일치·불일치·교집합)
 - 여러 Area에 걸친 article_id 중복 제거
 - Evidence 필드 매핑 (id·title·source·url·publishedAt)
 - 발행일 역순 정렬 (최신→과거→날짜 없음)
 - source_by_id / published_at_by_id 오버라이드
 - 빈 입력 처리
 - build_domains evidenceIds와 id 일관성
"""

from __future__ import annotations

from career_compass_pipeline.aggregate import build_domains
from career_compass_pipeline.evidence import Evidence, build_evidence_catalog

# ── 테스트용 헬퍼 ─────────────────────────────────────────────────────────────


def _area(
    *,
    id: str = "co-01",
    area_name: str = "테스트 영역",
    evidence: list[dict] | None = None,
) -> dict:
    return {"id": id, "area_name": area_name, "evidence": evidence or []}


def _ev(
    article_id: str,
    roles: list[str],
    *,
    title: str = "",
    url: str = "",
) -> dict:
    return {
        "article_id": article_id,
        "title": title or f"title-{article_id}",
        "url": url or f"https://example.com/{article_id}",
        "roles": roles,
    }


def _ids(catalog: list[Evidence]) -> list[str]:
    return [e["id"] for e in catalog]


# ── 빈 입력 ───────────────────────────────────────────────────────────────────


def test_empty_areas_returns_empty() -> None:
    assert build_evidence_catalog([], "backend") == []


def test_area_with_no_evidence_returns_empty() -> None:
    assert build_evidence_catalog([_area(evidence=[])], "backend") == []


def test_no_role_match_returns_empty() -> None:
    areas = [_area(evidence=[_ev("a1", ["frontend"])])]
    assert build_evidence_catalog(areas, "backend") == []


# ── 기본 필드 매핑 ────────────────────────────────────────────────────────────


def test_basic_fields_mapped() -> None:
    areas = [
        _area(
            evidence=[
                _ev("abc123", ["backend"], title="Kafka 도입기", url="https://blog.co/kafka")
            ]
        )
    ]
    catalog = build_evidence_catalog(areas, "backend")

    assert len(catalog) == 1
    e = catalog[0]
    assert e["id"] == "ev-abc123"
    assert e["title"] == "Kafka 도입기"
    assert e["url"] == "https://blog.co/kafka"
    assert e["source"] == "blog"       # 기본값
    assert e["publishedAt"] == ""      # published_at_by_id 없음


def test_id_format_ev_prefix() -> None:
    areas = [_area(evidence=[_ev("deadbeef", ["backend"])])]
    catalog = build_evidence_catalog(areas, "backend")
    assert catalog[0]["id"] == "ev-deadbeef"


def test_missing_title_becomes_empty_string() -> None:
    ev = {"article_id": "x1", "title": None, "url": "https://x.com", "roles": ["backend"]}
    areas = [_area(evidence=[ev])]
    catalog = build_evidence_catalog(areas, "backend")
    assert catalog[0]["title"] == ""


def test_missing_url_becomes_empty_string() -> None:
    ev = {"article_id": "x1", "title": "T", "url": None, "roles": ["backend"]}
    areas = [_area(evidence=[ev])]
    catalog = build_evidence_catalog(areas, "backend")
    assert catalog[0]["url"] == ""


# ── role 필터링 ───────────────────────────────────────────────────────────────


def test_only_matching_role_included() -> None:
    areas = [
        _area(
            evidence=[
                _ev("be", ["backend"]),
                _ev("fe", ["frontend"]),
                _ev("both", ["backend", "frontend"]),
            ]
        )
    ]
    catalog = build_evidence_catalog(areas, "backend")
    ids = _ids(catalog)
    assert "ev-be" in ids
    assert "ev-both" in ids
    assert "ev-fe" not in ids


def test_multi_role_article_included_once() -> None:
    """backend+frontend 글은 backend 필터 시 1건으로 포함."""
    areas = [_area(evidence=[_ev("multi", ["backend", "frontend"])])]
    catalog = build_evidence_catalog(areas, "backend")
    assert len(catalog) == 1


# ── 중복 제거 ─────────────────────────────────────────────────────────────────


def test_duplicate_within_same_area_deduplicated() -> None:
    areas = [
        _area(
            evidence=[
                _ev("dup", ["backend"]),
                _ev("dup", ["backend"]),
                _ev("uniq", ["backend"]),
            ]
        )
    ]
    catalog = build_evidence_catalog(areas, "backend")
    assert len(catalog) == 2
    assert _ids(catalog).count("ev-dup") == 1


def test_duplicate_across_areas_deduplicated() -> None:
    """같은 article_id가 두 Area에 걸쳐 나와도 한 번만."""
    areas = [
        _area(id="a-01", evidence=[_ev("shared", ["backend"])]),
        _area(id="a-02", evidence=[_ev("shared", ["backend"]), _ev("only2", ["backend"])]),
    ]
    catalog = build_evidence_catalog(areas, "backend")
    assert _ids(catalog).count("ev-shared") == 1
    assert "ev-only2" in _ids(catalog)


def test_first_occurrence_metadata_used() -> None:
    """중복 시 첫 번째 Area의 title·url이 사용됨."""
    areas = [
        _area(id="a-01", evidence=[_ev("dup", ["backend"], title="First", url="https://first")]),
        _area(id="a-02", evidence=[_ev("dup", ["backend"], title="Second", url="https://second")]),
    ]
    catalog = build_evidence_catalog(areas, "backend")
    assert catalog[0]["title"] == "First"
    assert catalog[0]["url"] == "https://first"


# ── source_by_id ──────────────────────────────────────────────────────────────


def test_default_source_is_blog() -> None:
    areas = [_area(evidence=[_ev("a1", ["backend"])])]
    catalog = build_evidence_catalog(areas, "backend")
    assert catalog[0]["source"] == "blog"


def test_source_by_id_overrides() -> None:
    areas = [
        _area(
            evidence=[
                _ev("b1", ["backend"]),
                _ev("j1", ["backend"]),
            ]
        )
    ]
    catalog = build_evidence_catalog(
        areas, "backend", source_by_id={"b1": "blog", "j1": "job"}
    )
    by_id = {e["id"]: e["source"] for e in catalog}
    assert by_id["ev-b1"] == "blog"
    assert by_id["ev-j1"] == "job"


def test_unlisted_id_defaults_to_blog() -> None:
    areas = [_area(evidence=[_ev("x", ["backend"])])]
    catalog = build_evidence_catalog(
        areas, "backend", source_by_id={"other": "job"}
    )
    assert catalog[0]["source"] == "blog"


def test_source_by_id_none_same_as_empty() -> None:
    areas = [_area(evidence=[_ev("a", ["backend"])])]
    r1 = build_evidence_catalog(areas, "backend", source_by_id=None)
    r2 = build_evidence_catalog(areas, "backend", source_by_id={})
    assert r1 == r2


# ── published_at_by_id ────────────────────────────────────────────────────────


def test_published_at_mapped_from_dict() -> None:
    areas = [_area(evidence=[_ev("a1", ["backend"])])]
    catalog = build_evidence_catalog(
        areas, "backend", published_at_by_id={"a1": "2026-06-30"}
    )
    assert catalog[0]["publishedAt"] == "2026-06-30"


def test_missing_published_at_is_empty_string() -> None:
    areas = [_area(evidence=[_ev("a1", ["backend"])])]
    catalog = build_evidence_catalog(areas, "backend", published_at_by_id={})
    assert catalog[0]["publishedAt"] == ""


def test_published_at_none_same_as_empty() -> None:
    areas = [_area(evidence=[_ev("a", ["backend"])])]
    r1 = build_evidence_catalog(areas, "backend", published_at_by_id=None)
    r2 = build_evidence_catalog(areas, "backend", published_at_by_id={})
    assert r1 == r2


# ── 발행일 역순 정렬 (F-04: 시간 역순) ─────────────────────────────────────────


def test_sorted_newest_first() -> None:
    areas = [
        _area(
            evidence=[
                _ev("old", ["backend"]),
                _ev("new", ["backend"]),
                _ev("mid", ["backend"]),
            ]
        )
    ]
    pub = {"old": "2025-01-01", "new": "2026-09-01", "mid": "2025-12-15"}
    catalog = build_evidence_catalog(areas, "backend", published_at_by_id=pub)
    dates = [e["publishedAt"] for e in catalog]
    assert dates == sorted(dates, reverse=True)


def test_no_date_items_go_to_end() -> None:
    areas = [
        _area(
            evidence=[
                _ev("nodateA", ["backend"]),
                _ev("dated", ["backend"]),
                _ev("nodateB", ["backend"]),
            ]
        )
    ]
    pub = {"dated": "2026-01-15"}
    catalog = build_evidence_catalog(areas, "backend", published_at_by_id=pub)
    ids = _ids(catalog)
    # 날짜 있는 항목이 먼저
    assert ids[0] == "ev-dated"
    # 날짜 없는 항목이 뒤
    assert set(ids[1:]) == {"ev-nodateA", "ev-nodateB"}


def test_all_same_date_order_stable() -> None:
    """같은 날짜면 입력 순서가 유지됩니다."""
    areas = [
        _area(
            evidence=[
                _ev("a", ["backend"]),
                _ev("b", ["backend"]),
                _ev("c", ["backend"]),
            ]
        )
    ]
    pub = {"a": "2026-05-01", "b": "2026-05-01", "c": "2026-05-01"}
    catalog = build_evidence_catalog(areas, "backend", published_at_by_id=pub)
    assert _ids(catalog) == ["ev-a", "ev-b", "ev-c"]


def test_all_no_date_order_stable() -> None:
    areas = [
        _area(
            evidence=[_ev("a", ["backend"]), _ev("b", ["backend"]), _ev("c", ["backend"])]
        )
    ]
    catalog = build_evidence_catalog(areas, "backend")
    assert _ids(catalog) == ["ev-a", "ev-b", "ev-c"]


# ── build_domains evidenceIds와 id 일관성 ─────────────────────────────────────


def test_evidence_ids_consistent_with_build_domains() -> None:
    """build_domains의 evidenceIds와 build_evidence_catalog의 id가 1:1 매핑됩니다."""
    areas = [
        _area(
            id="co-01",
            evidence=[
                _ev("a1", ["backend"]),
                _ev("a2", ["backend"]),
                _ev("a3", ["frontend"]),  # backend 아님
            ],
        ),
        _area(
            id="co-02",
            evidence=[
                _ev("b1", ["backend"]),
                _ev("a1", ["backend"]),   # 중복 (co-01에도 있음)
            ],
        ),
    ]
    domains = build_domains(areas, "backend")
    catalog = build_evidence_catalog(areas, "backend")

    # domains의 모든 evidenceId가 catalog에 존재해야 함
    catalog_ids = {e["id"] for e in catalog}
    for domain in domains:
        for eid in domain["evidenceIds"]:
            assert eid in catalog_ids, f"{eid} not in catalog"

    # catalog에 frontend-only 글은 없어야 함
    assert "ev-a3" not in catalog_ids


# ── 실제 데이터 모양 시뮬레이션 ──────────────────────────────────────────────


def test_realistic_data() -> None:
    """group1_areas.json 형태의 실제 데이터 구조로 검증합니다."""
    areas = [
        {
            "id": "socar-01",
            "area_name": "디자인 시스템과 크로스플랫폼 앱 프레임워크 설계",
            "evidence": [
                {
                    "article_id": "40ca85f39b5dc7ec",
                    "title": "쏘카 디자인 시스템 2.0 개발기 2편",
                    "url": "https://tech.socar.kr/socar-frame2-web-part2",
                    "roles": ["backend", "frontend", "data-ai"],
                },
                {
                    "article_id": "f8ca35d83c532384",
                    "title": "쏘카 디자인 시스템 2.0 개발기 1편",
                    "url": "https://tech.socar.kr/socar-frame2-web",
                    "roles": ["backend", "frontend"],
                },
                {
                    "article_id": "c86984a9b70b3710",
                    "title": "쏘카프레임 - 앱 프레임워크와 개발자 경험",
                    "url": "https://tech.socar.kr/socarframe-introduce",
                    "roles": ["backend", "mobile"],
                },
            ],
        }
    ]
    pub = {
        "40ca85f39b5dc7ec": "2026-02-25",
        "f8ca35d83c532384": "2026-02-24",
        "c86984a9b70b3710": "2026-01-07",
    }

    catalog = build_evidence_catalog(areas, "backend", published_at_by_id=pub)

    assert len(catalog) == 3

    # 발행일 역순 확인
    dates = [e["publishedAt"] for e in catalog]
    assert dates == ["2026-02-25", "2026-02-24", "2026-01-07"]

    # 필드 형식 확인
    for e in catalog:
        assert e["id"].startswith("ev-")
        assert e["source"] == "blog"
        assert e["title"]
        assert e["url"].startswith("https://")

    # frontend 전용 글은 없음 (소카 데이터엔 없지만 방어)
    # mobile-only가 없으므로 3건 모두 backend 포함
    assert len(catalog) == 3
