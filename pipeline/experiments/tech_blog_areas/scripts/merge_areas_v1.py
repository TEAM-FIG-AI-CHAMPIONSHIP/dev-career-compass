import json
import os
from pathlib import Path
from typing import List

from anthropic import Anthropic
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[4]

CLUSTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "clustering_v4"
    / "cluster_detail_complete_8_0.1200.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
)

AREAS_FILE = (
    OUTPUT_DIR
    / "areas.json"
)

EVIDENCE_FILE = (
    OUTPUT_DIR
    / "area_evidence.json"
)


MODEL_NAME = "claude-sonnet-5"

MIN_AREAS = 3
MAX_AREAS = 5


SYSTEM_PROMPT = """
당신은 기업 기술블로그 게시글의 raw semantic cluster를 검토해
개발자 취업준비생을 위한 최종 기술 Area로 병합·명명하는 분석기입니다.

입력은 임베딩 기반 계층적 군집화(agglomerative clustering)로 만들어진
raw cluster 목록입니다. 각 cluster는 제목과 engineering_focus를 가진
게시글들의 묶음입니다.

당신의 작업:

1. raw cluster들을 검토하고, 의미적으로 가까운 cluster끼리 병합하거나
   그대로 유지해서 최종 Area를 3개에서 5개 사이로 만드세요.

2. 각 raw cluster는 정확히 하나의 최종 Area에만 속해야 합니다.
   cluster를 누락하거나 두 Area에 중복 배정하지 마세요.

3. 억지로 큰 Area 몇 개로 뭉치지 말고, 실제로 다루는 엔지니어링 문제가
   비슷한 cluster끼리만 병합하세요. 정말 안 맞으면 cluster 하나가
   단독으로 Area가 되어도 괜찮습니다.

4. 한 cluster 안에 이질적인 게시글이 섞여 있는 게 보이면
   (예: 특정 게시글이 cluster의 주제와 명백히 다른 엔지니어링 문제를 다룸)
   note 필드에 그 사실을 기록하세요. cluster를 쪼개지는 마세요 —
   cluster 단위 병합만 수행합니다.

5. area_name은 한국어로 간결하게 (예: "AI 서비스 개발·운영",
   "서비스 안정성·운영", "웹·앱 클라이언트 구조 개선").

6. area_description은 이 Area가 실제로 다루는 엔지니어링 문제 범위를
   1~2문장으로 설명하세요. "여러 기술을 다룬 경험" 같은 공허한 설명은
   금지합니다.

7. rationale에는 어떤 raw cluster들을 왜 합쳤는지(혹은 왜 안 합쳤는지)
   근거를 쓰세요.
"""


class AreaAssignment(BaseModel):
    area_name: str
    area_description: str
    cluster_ranks: List[int]
    rationale: str
    note: str = ""


class AreaMergeResult(BaseModel):
    areas: List[AreaAssignment]


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def build_cluster_payload(clusters):
    payload = []

    for cluster in clusters:
        payload.append(
            {
                "cluster_rank": (
                    cluster["cluster_rank"]
                ),
                "size": cluster["size"],
                "members": [
                    {
                        "title": (
                            member["title"]
                        ),
                        "engineering_focus": (
                            member[
                                "engineering_focus"
                            ]
                        )
                    }
                    for member in cluster[
                        "members"
                    ]
                ]
            }
        )

    return payload


def validate_result(
    result,
    clusters
):
    expected_ranks = {
        cluster["cluster_rank"]
        for cluster in clusters
    }

    seen_ranks = []

    for area in result.areas:
        seen_ranks.extend(
            area.cluster_ranks
        )

    if len(
        seen_ranks
    ) != len(
        set(seen_ranks)
    ):
        raise ValueError(
            "동일 cluster_rank가 여러 Area에 중복 배정되었습니다."
        )

    if set(
        seen_ranks
    ) != expected_ranks:
        raise ValueError(
            "cluster_rank 배정이 입력 cluster 전체와 일치하지 않습니다: "
            f"expected={sorted(expected_ranks)} "
            f"got={sorted(seen_ranks)}"
        )

    if not (
        MIN_AREAS
        <= len(result.areas)
        <= MAX_AREAS
    ):
        raise ValueError(
            f"최종 Area 개수가 {MIN_AREAS}~{MAX_AREAS} 범위를 "
            f"벗어났습니다: {len(result.areas)}"
        )


def merge_areas(
    client,
    clusters
):
    payload = build_cluster_payload(
        clusters
    )

    message = client.messages.parse(
        model=MODEL_NAME,
        max_tokens=4000,
        thinking={
            "type": "disabled"
        },
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "다음 raw cluster들을 검토해 "
                    f"최종 Area {MIN_AREAS}~{MAX_AREAS}개로 "
                    "병합·명명하세요.\n\n"
                    + json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2
                    )
                )
            }
        ],
        output_format=AreaMergeResult
    )

    result = (
        message
        .parsed_output
    )

    validate_result(
        result,
        clusters
    )

    return result


def build_evidence_report(
    result,
    clusters
):
    clusters_by_rank = {
        cluster["cluster_rank"]: cluster
        for cluster in clusters
    }

    evidence = []

    for area in result.areas:
        members = []

        company_counts = {}

        for rank in area.cluster_ranks:
            cluster = clusters_by_rank[
                rank
            ]

            for member in cluster[
                "members"
            ]:
                members.append(
                    member
                )

                company = member[
                    "company"
                ]

                company_counts[
                    company
                ] = (
                    company_counts.get(
                        company,
                        0
                    )
                    + 1
                )

        evidence.append(
            {
                "area_name": (
                    area.area_name
                ),
                "area_description": (
                    area.area_description
                ),
                "cluster_ranks": (
                    area.cluster_ranks
                ),
                "rationale": (
                    area.rationale
                ),
                "note": area.note,
                "article_count": len(
                    members
                ),
                "company_counts": (
                    company_counts
                ),
                "articles": [
                    {
                        "company": (
                            member["company"]
                        ),
                        "title": (
                            member["title"]
                        ),
                        "engineering_focus": (
                            member[
                                "engineering_focus"
                            ]
                        ),
                        "url": (
                            member["url"]
                        )
                    }
                    for member in members
                ]
            }
        )

    return evidence


def print_evidence(evidence):
    total_articles = sum(
        area["article_count"]
        for area in evidence
    )

    print()
    print("=" * 60)
    print(
        f"최종 Area: {len(evidence)}개"
        f" / 전체 게시글 {total_articles}개"
    )
    print("=" * 60)

    for rank, area in enumerate(
        evidence,
        start=1
    ):
        print()
        print(
            f"[{rank}] {area['area_name']}"
            f"  (cluster {area['cluster_ranks']},"
            f" {area['article_count']}개)"
        )

        print(
            "  설명:",
            area["area_description"]
        )

        print(
            "  근거:",
            area["rationale"]
        )

        if area["note"]:
            print(
                "  주의:",
                area["note"]
            )

        for article in area["articles"]:
            print(
                "   -",
                article["title"]
            )


def main():
    if not os.getenv(
        "ANTHROPIC_API_KEY"
    ):
        raise RuntimeError(
            "ANTHROPIC_API_KEY가 설정되어 있지 않습니다."
        )

    cluster_data = load_json(
        CLUSTER_FILE
    )

    clusters = cluster_data[
        "clusters"
    ]

    client = Anthropic()

    print()
    print("=" * 60)
    print("AREA 병합·명명 시작")
    print("=" * 60)

    print(
        "입력 cluster 수:",
        len(clusters)
    )

    result = merge_areas(
        client,
        clusters
    )

    evidence = build_evidence_report(
        result,
        clusters
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    save_json(
        AREAS_FILE,
        {
            "source_cluster_file": str(
                CLUSTER_FILE
            ),
            "model": MODEL_NAME,
            "areas": [
                area.model_dump()
                for area in result.areas
            ]
        }
    )

    save_json(
        EVIDENCE_FILE,
        evidence
    )

    print_evidence(
        evidence
    )

    print()
    print("=" * 60)
    print("AREA 병합·명명 완료")
    print("=" * 60)

    print(
        "areas:",
        AREAS_FILE
    )

    print(
        "evidence:",
        EVIDENCE_FILE
    )


if __name__ == "__main__":
    main()
