"""build_areas_per_company.py의 LLM 두 단계(merge/tag)를 API 대신
claude.ai 수동 프롬프팅으로 처리하기 위한 3단계 CLI.

클러스터링·membership 매칭은 로컬 결정적 계산이라 그대로 재사용하고
(회사명 분기 없음, LLM은 병합·태깅에만 사용한다는 기존 원칙 유지),
LLM이 필요한 두 지점만 프롬프트 파일로 내보내고 응답을 다시 읽어들인다.

사용 순서 (회사 하나당):
  1. export-merge  --company "X" --output-suffix group3
     -> raw cluster를 계산해 merge 프롬프트 텍스트 파일을 만든다.
  2. (claude.ai에 붙여넣고 JSON 응답을 저장)
  3. import-merge  --company "X" --output-suffix group3 --response-file ...
     -> 응답을 검증(누락/중복 cluster_rank, Area 개수 3~5)하고,
        membership을 로컬에서 계산한 뒤 tag 프롬프트를 만든다.
  4. (claude.ai에 붙여넣고 JSON 응답을 저장)
  5. import-tags   --company "X" --output-suffix group3 --response-file ...
     -> 태그를 합쳐 회사별 최종 결과를 저장한다.

  8개 회사를 전부 끝낸 뒤:
  6. finalize --output-suffix group3
     -> 회사별 결과를 모아 data/research에 요약 json/md를 만든다
        (build_areas_per_company.py의 main() 마지막 부분과 동일한 형식).
"""

import argparse
import json
import sys

from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

from build_areas_per_company import (  # noqa: E402
    AreaAssignment,
    MAX_AREAS,
    MERGE_SYSTEM_PROMPT,
    MIN_AREAS,
    RESEARCH_DIR,
    TAG_SYSTEM_PROMPT,
    WORK_DIR,
    assign_area_ids,
    build_cluster_detail,
    diagnose_unassigned,
    load_json,
    match_articles_to_areas,
    pick_cluster_target,
    save_json,
    scan_clusters
)


STATE_DIR = (
    WORK_DIR
    / "manual_area_pipeline"
)


def safe_filename(name):
    return (
        name
        .replace("/", "_")
        .replace(" ", "_")
    )


def company_state_dir(company, suffix):
    return (
        STATE_DIR
        / (suffix or "default")
        / safe_filename(company)
    )


def embeddings_dir(suffix):
    name = (
        "embeddings_v4"
        if not suffix
        else f"embeddings_v4_{suffix}"
    )

    return WORK_DIR / name


def areas_output_dir(suffix):
    name = (
        "areas_per_company"
        if not suffix
        else f"areas_per_company_{suffix}"
    )

    return WORK_DIR / name


def load_company_embeddings(company, suffix):
    emb_dir = embeddings_dir(suffix)

    embeddings = np.load(
        emb_dir / "article_embeddings.npy"
    )

    metadata = load_json(
        emb_dir / "articles.json"
    )

    indices = [
        i
        for i, item in enumerate(metadata)
        if item["company"] == company
    ]

    if not indices:
        raise ValueError(
            f"'{company}' 회사의 임베딩을 찾을 수 없습니다. "
            f"embed_v4.py --output-suffix {suffix!r}로 먼저 "
            "임베딩했는지 확인하세요."
        )

    return (
        embeddings[indices],
        [metadata[i] for i in indices]
    )


def cmd_export_merge(args):
    company = args.company
    suffix = args.output_suffix

    company_embeddings, company_metadata = (
        load_company_embeddings(
            company,
            suffix
        )
    )

    distance_matrix = (
        1
        - cosine_similarity(
            company_embeddings
        )
    )

    distance_matrix = np.clip(
        distance_matrix,
        0,
        None
    )

    target = pick_cluster_target(
        len(company_metadata)
    )

    best = scan_clusters(
        distance_matrix,
        target
    )

    if best is None:
        print(
            f"'{company}': 클러스터링 실패 "
            "(데이터 부족, 3명 이상 필요)"
        )

        return

    _, threshold, n_clusters, labels = best

    raw_clusters = build_cluster_detail(
        labels,
        company_metadata
    )

    state_dir = company_state_dir(
        company,
        suffix
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    save_json(
        state_dir / "raw_clusters.json",
        raw_clusters
    )

    save_json(
        state_dir / "clustering_meta.json",
        {
            "threshold": threshold,
            "n_clusters": n_clusters,
            "target": target
        }
    )

    payload = [
        {
            "cluster_rank": cluster["cluster_rank"],
            "size": cluster["size"],
            "members": [
                {
                    "title": member["title"],
                    "engineering_focus": (
                        member["engineering_focus"]
                    )
                }
                for member in cluster["members"]
            ]
        }
        for cluster in raw_clusters
    ]

    prompt_lines = [
        "아래는 기술블로그 raw cluster를 최종 Area로 "
        "병합·명명하는 작업입니다.",
        f"회사: {company} ({len(company_metadata)}건, "
        f"raw cluster {n_clusters}개, 목표 Area {target}개)",
        "",
        "지시사항: 아래 SYSTEM 규칙을 따라 DATA의 cluster들을 "
        f"최종 Area {MIN_AREAS}~{MAX_AREAS}개로 병합·명명하세요.",
        (
            "출력은 다른 설명 없이 JSON 객체 하나만 출력하세요. "
            "코드블록(```) 없이, 다음 형식 그대로:"
        ),
        (
            '{"areas": [{"area_name": "...", '
            '"area_description": "...", '
            '"cluster_ranks": [1, 2], '
            '"rationale": "...", "note": ""}, ...]}'
        ),
        (
            "DATA에 있는 cluster_rank를 빠짐없이, "
            "정확히 하나의 Area에만 배정하세요."
        ),
        "",
        "=== SYSTEM ===",
        MERGE_SYSTEM_PROMPT.strip(),
        "",
        "=== DATA ===",
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    ]

    prompt_file = (
        state_dir / "merge_prompt.txt"
    )

    with open(
        prompt_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(prompt_lines)
        )

    print(
        f"'{company}': raw cluster {n_clusters}개 "
        f"(threshold={threshold:.4f})"
    )

    print(
        "merge 프롬프트 저장:",
        prompt_file
    )


def validate_merge_response(data, expected_ranks):
    if (
        not isinstance(data, dict)
        or "areas" not in data
    ):
        raise ValueError(
            "응답이 {\"areas\": [...]} 형식이 아닙니다."
        )

    areas = [
        AreaAssignment(**area)
        for area in data["areas"]
    ]

    seen_ranks = []

    for area in areas:
        seen_ranks.extend(
            area.cluster_ranks
        )

    if len(seen_ranks) != len(set(seen_ranks)):
        raise ValueError(
            "같은 cluster_rank가 두 Area에 중복 배정됨: "
            f"{sorted(seen_ranks)}"
        )

    if set(seen_ranks) != expected_ranks:
        missing = expected_ranks - set(seen_ranks)
        extra = set(seen_ranks) - expected_ranks

        raise ValueError(
            f"cluster_rank 불일치 (누락: {sorted(missing)}, "
            f"모르는 값: {sorted(extra)})"
        )

    if not (MIN_AREAS <= len(areas) <= MAX_AREAS):
        raise ValueError(
            f"최종 Area 개수가 범위를 벗어남: {len(areas)} "
            f"(허용 {MIN_AREAS}~{MAX_AREAS})"
        )

    return areas


def cmd_import_merge(args):
    company = args.company
    suffix = args.output_suffix

    state_dir = company_state_dir(
        company,
        suffix
    )

    raw_clusters = load_json(
        state_dir / "raw_clusters.json"
    )

    expected_ranks = {
        cluster["cluster_rank"]
        for cluster in raw_clusters
    }

    response_data = load_json(
        Path(args.response_file)
    )

    areas = validate_merge_response(
        response_data,
        expected_ranks
    )

    save_json(
        state_dir / "merge_result.json",
        {
            "areas": [
                area.model_dump()
                for area in areas
            ]
        }
    )

    print(
        f"'{company}': merge 검증 통과, "
        f"Area {len(areas)}개"
    )

    for area in areas:
        print(
            f" - {area.area_name} "
            f"(cluster {area.cluster_ranks})"
        )

    company_embeddings, company_metadata = (
        load_company_embeddings(
            company,
            suffix
        )
    )

    membership = match_articles_to_areas(
        _load_embed_model(),
        company_embeddings,
        company_metadata,
        areas
    )

    focus_by_id = {
        m["article_id"]: m["engineering_focus"]
        for m in company_metadata
    }

    roles_by_id = {
        m["article_id"]: m.get(
            "roles",
            []
        )
        for m in company_metadata
    }

    for row in membership:
        row["engineering_focus"] = (
            focus_by_id.get(
                row["article_id"],
                ""
            )
        )

        row["roles"] = roles_by_id.get(
            row["article_id"],
            []
        )

    save_json(
        state_dir / "membership.json",
        membership
    )

    assigned_counts = {}
    unassigned_count = 0

    for row in membership:
        if row["assigned_area"]:
            assigned_counts[
                row["assigned_area"]
            ] = (
                assigned_counts.get(
                    row["assigned_area"],
                    0
                )
                + 1
            )

        else:
            unassigned_count += 1

    for area in areas:
        print(
            "   evidence:",
            assigned_counts.get(
                area.area_name,
                0
            )
        )

    print(
        "unassigned:",
        unassigned_count
    )

    members_by_area = {}

    for row in membership:
        if row["assigned_area"]:
            members_by_area.setdefault(
                row["assigned_area"],
                []
            ).append(row)

    tag_payload = [
        {
            "area_name": area.area_name,
            "members": [
                {
                    "title": m["title"],
                    "engineering_focus": (
                        m.get(
                            "engineering_focus",
                            ""
                        )
                    )
                }
                for m in members_by_area.get(
                    area.area_name,
                    []
                )
            ]
        }
        for area in areas
        if members_by_area.get(area.area_name)
    ]

    prompt_lines = [
        "아래는 각 Area의 대표 키워드 태그를 뽑는 작업입니다.",
        f"회사: {company} (Area {len(tag_payload)}개)",
        "",
        "지시사항: 아래 SYSTEM 규칙을 따라 DATA의 Area마다 "
        "5~8개의 키워드 태그를 뽑으세요.",
        (
            "출력은 다른 설명 없이 JSON 객체 하나만 출력하세요. "
            "코드블록(```) 없이, 다음 형식 그대로:"
        ),
        (
            '{"areas": [{"area_name": "...", '
            '"tags": [{"tag": "...", "rationale": "..."}, ...]}'
            ', ...]}'
        ),
        (
            "DATA에 있는 area_name을 빠짐없이, "
            "정확히 한 번씩만 포함하세요."
        ),
        "",
        "=== SYSTEM ===",
        TAG_SYSTEM_PROMPT.strip(),
        "",
        "=== DATA ===",
        json.dumps(
            tag_payload,
            ensure_ascii=False,
            indent=2
        )
    ]

    prompt_file = (
        state_dir / "tag_prompt.txt"
    )

    with open(
        prompt_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(prompt_lines)
        )

    print(
        "tag 프롬프트 저장:",
        prompt_file
    )


_EMBED_MODEL_CACHE = {}


def _load_embed_model():
    if "model" not in _EMBED_MODEL_CACHE:
        from build_areas_per_company import (
            EMBED_MODEL_NAME
        )

        from sentence_transformers import (
            SentenceTransformer
        )

        _EMBED_MODEL_CACHE["model"] = (
            SentenceTransformer(
                EMBED_MODEL_NAME
            )
        )

    return _EMBED_MODEL_CACHE["model"]


def cmd_import_tags(args):
    company = args.company
    suffix = args.output_suffix

    state_dir = company_state_dir(
        company,
        suffix
    )

    merge_result = load_json(
        state_dir / "merge_result.json"
    )

    areas = [
        AreaAssignment(**area)
        for area in merge_result["areas"]
    ]

    membership = load_json(
        state_dir / "membership.json"
    )

    tag_response = load_json(
        Path(args.response_file)
    )

    if (
        not isinstance(tag_response, dict)
        or "areas" not in tag_response
    ):
        raise ValueError(
            "응답이 {\"areas\": [...]} 형식이 아닙니다."
        )

    tags_by_area = {}

    for entry in tag_response["areas"]:
        tags = [
            item["tag"]
            for item in entry["tags"]
        ]

        if not (5 <= len(tags) <= 8):
            print(
                f"[경고] '{entry['area_name']}' "
                f"태그 개수={len(tags)} (5~8 권장, "
                "그대로 진행)"
            )

        tags_by_area[
            entry["area_name"]
        ] = tags

    company_embeddings, company_metadata = (
        load_company_embeddings(
            company,
            suffix
        )
    )

    final_areas = []

    for area in areas:
        members = [
            row
            for row in membership
            if row["assigned_area"]
            == area.area_name
        ]

        # Area의 roles는 LLM이 새로 판단하지 않는다. 이미 이 Area에
        # 배정된(임베딩 유사도 기반 deterministic 매칭) evidence
        # article들의 roles(census가 결정적으로 계산한 값)를
        # 합집합·집계해서 만든다.
        role_counter = Counter()

        for m in members:
            for role in m.get(
                "roles",
                []
            ):
                role_counter[role] += 1

        final_areas.append(
            {
                "area_name": area.area_name,
                "area_description": (
                    area.area_description
                ),
                "rationale": area.rationale,
                "note": area.note,
                "keywords": tags_by_area.get(
                    area.area_name,
                    []
                ),
                "article_count": len(members),
                "roles": sorted(
                    role_counter.keys()
                ),
                "role_counts": dict(
                    role_counter
                ),
                "evidence": [
                    {
                        "article_id": (
                            m["article_id"]
                        ),
                        "title": m["title"],
                        "url": m["url"],
                        "similarity": (
                            m["similarity"]
                        ),
                        "roles": m.get(
                            "roles",
                            []
                        )
                    }
                    for m in members
                ]
            }
        )

    final_areas = assign_area_ids(
        company,
        final_areas
    )

    unassigned_rows = [
        row
        for row in membership
        if not row["assigned_area"]
    ]

    unassigned_diagnostic = diagnose_unassigned(
        unassigned_rows,
        company_embeddings,
        company_metadata
    )

    # 회사 전체 roles 집계는 Area 소속과 무관하게 전체 기술글
    # 기준으로 낸다 — census 1차 게이트와 같은 집계 단위를 유지해야
    # "이 회사가 이 직무 페이지에 나올 만큼 근거가 있는지"를 Area
    # 구성과 별개로 판단할 수 있다.
    company_role_counter = Counter()

    for row in membership:
        for role in row.get(
            "roles",
            []
        ):
            company_role_counter[role] += 1

    company_result = {
        "company": company,
        "article_count": len(company_metadata),
        "areas": final_areas,
        "unassigned_count": len(unassigned_rows),
        "unassigned_diagnostic": (
            unassigned_diagnostic
        ),
        "role_counts": dict(
            company_role_counter
        )
    }

    out_dir = areas_output_dir(suffix)

    save_json(
        out_dir / f"{safe_filename(company)}.json",
        company_result
    )

    print(
        f"'{company}': 최종 결과 저장 완료 -> "
        f"{out_dir / (safe_filename(company) + '.json')}"
    )

    print(
        "Area:",
        len(final_areas),
        "unassigned:",
        len(unassigned_rows)
    )


def cmd_finalize(args):
    suffix = args.output_suffix

    out_dir = areas_output_dir(suffix)

    result_files = sorted(
        out_dir.glob("*.json")
    )

    if not result_files:
        print(
            "완료된 회사 결과가 없습니다:",
            out_dir
        )

        return

    all_results = [
        load_json(path)
        for path in result_files
    ]

    output_basename = (
        "track_b_pilot_areas"
        if not suffix
        else f"{suffix}_areas"
    )

    save_json(
        RESEARCH_DIR / f"{output_basename}.json",
        all_results
    )

    lines = [
        f"# {output_basename}: "
        f"{len(all_results)}개 회사 Area 생성 결과 "
        "(수동 프롬프팅)",
        "",
        (
            "engineering_focus -> v4 embedding -> "
            "clustering(complete linkage) -> LLM 병합 -> "
            "deterministic membership -> 키워드 태깅 "
            f"전체 파이프라인을 {len(all_results)}개 회사에 "
            "독립적으로 적용한 결과다 (LLM 두 단계는 "
            "claude.ai 수동 프롬프팅으로 수행)."
        ),
        ""
    ]

    for result in all_results:
        lines.append(
            f"## {result['company']} "
            f"({result['article_count']}개 글)"
        )

        lines.append("")

        lines.append(
            "| Area | 근거 수 | 키워드 |"
        )

        lines.append(
            "|---|---:|---|"
        )

        for area in result["areas"]:
            keywords = ", ".join(
                area["keywords"]
            )

            lines.append(
                f"| {area['area_name']} "
                f"| {area['article_count']} "
                f"| {keywords} |"
            )

        lines.append(
            f"\nunassigned: "
            f"{result['unassigned_count']}"
        )

        lines.append("")

    with open(
        RESEARCH_DIR / f"{output_basename}.md",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(lines)
        )

    print(
        "완료된 회사:",
        len(all_results)
    )

    print(
        "저장:",
        RESEARCH_DIR / f"{output_basename}.md"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "stage",
        choices=[
            "export-merge",
            "import-merge",
            "import-tags",
            "finalize"
        ]
    )

    parser.add_argument("--company", type=str, default="")
    parser.add_argument("--output-suffix", type=str, default="")
    parser.add_argument("--response-file", type=str, default="")

    args = parser.parse_args()

    if (
        args.stage != "finalize"
        and not args.company
    ):
        raise SystemExit(
            "--company가 필요합니다."
        )

    if (
        args.stage in ("import-merge", "import-tags")
        and not args.response_file
    ):
        raise SystemExit(
            "--response-file이 필요합니다."
        )

    if args.stage == "export-merge":
        cmd_export_merge(args)

    elif args.stage == "import-merge":
        cmd_import_merge(args)

    elif args.stage == "import-tags":
        cmd_import_tags(args)

    elif args.stage == "finalize":
        cmd_finalize(args)


if __name__ == "__main__":
    main()
