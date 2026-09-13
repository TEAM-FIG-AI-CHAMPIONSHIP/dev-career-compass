import json
import os

from pathlib import Path
from typing import List

import numpy as np

from anthropic import Anthropic
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[4]

WORK_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
)

EMBEDDINGS_FILE = (
    WORK_DIR
    / "embeddings_v4"
    / "article_embeddings.npy"
)

METADATA_FILE = (
    WORK_DIR
    / "embeddings_v4"
    / "articles.json"
)

AREAS_OUTPUT_DIR = (
    WORK_DIR
    / "areas_per_company"
)

RESEARCH_DIR = (
    PROJECT_ROOT
    / "data"
    / "research"
    / "tech_blog_engineering_focus_29"
)


MODEL_NAME = "claude-sonnet-5"

EMBED_MODEL_NAME = "intfloat/multilingual-e5-small"

LINKAGE = "complete"

THRESHOLD_MIN = 0.03
THRESHOLD_MAX = 0.25
THRESHOLD_STEP = 0.005

MIN_AREAS = 3
MAX_AREAS = 5

ASSIGN_THRESHOLD = 0.86
MARGIN_THRESHOLD = 0.0032

TAGS_PER_AREA_MIN = 5
TAGS_PER_AREA_MAX = 8


MERGE_SYSTEM_PROMPT = """
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

4. 한 cluster 안에 이질적인 게시글이 섞여 있는 게 보이면 note 필드에
   그 사실을 기록하세요. cluster를 쪼개지는 마세요.

5. Area는 콘텐츠 형식이나 게시물 유형이 아니라, 조직이 반복적으로
   다루는 엔지니어링 문제·시스템·기술적 과제를 나타내야 합니다.
   뉴스레터, 행사·컨퍼런스 소개, 조직 문화·메타 콘텐츠, 카테고리
   분류 그 자체는 Area로 만들지 마세요.
   어떤 cluster가 이런 성격이라면, 그 안에서 실제로 드러나는
   구체적인 엔지니어링 주제를 기준으로 다른 Area와 병합하거나
   이름을 다시 지으세요. 그래도 엔지니어링 실체가 없다면 note에
   그렇게 적고, 억지로 그럴듯한 Area 이름을 붙이지 마세요.

6. area_name은 한국어로 간결하게.

7. area_description은 이 Area가 실제로 다루는 엔지니어링 문제 범위를
   1~2문장으로 설명하세요. 공허한 설명은 금지합니다.

8. rationale에는 어떤 raw cluster들을 왜 합쳤는지(혹은 왜 안 합쳤는지)
   근거를 쓰세요.
"""

TAG_SYSTEM_PROMPT = """
당신은 기술블로그 게시글 묶음(Area)에서 대표 키워드 태그를 뽑는
분석기입니다.

각 Area마다 그 Area에 속한 게시글들의 engineering_focus에
실제로 등장하는 구체적인 기술/기법/프로토콜/도구 이름을
5~8개의 짧은 키워드 태그로 뽑으세요.

규칙:

1. 태그는 반드시 제공된 텍스트에 실제로 등장하는 표현이어야 합니다.

2. "AI", "백엔드", "최적화"처럼 지나치게 일반적인 단어는 태그로
   뽑지 마세요. 구체적인 기술/시스템/기법 이름을 우선하세요.

3. 여러 게시글에 걸쳐 반복되는 태그를 우선하되, 한 게시글에만
   등장해도 핵심적이면 포함할 수 있습니다.

4. 태그 개수는 5개 이상 8개 이하로 하세요.

5. 각 태그마다 왜 이 Area를 대표하는지 한 줄 근거를 작성하세요.
"""


class AreaAssignment(BaseModel):
    area_name: str
    area_description: str
    cluster_ranks: List[int]
    rationale: str
    note: str = ""


class AreaMergeResult(BaseModel):
    areas: List[AreaAssignment]


class AreaTagItem(BaseModel):
    tag: str
    rationale: str


class AreaTags(BaseModel):
    area_name: str
    tags: List[AreaTagItem]


class AreaTagBatch(BaseModel):
    areas: List[AreaTags]


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


def pick_cluster_target(n):
    return max(
        3,
        min(
            10,
            round(n / 12)
        )
    )


def scan_clusters(
    distance_matrix,
    target
):
    thresholds = np.round(
        np.arange(
            THRESHOLD_MIN,
            THRESHOLD_MAX + THRESHOLD_STEP,
            THRESHOLD_STEP
        ),
        4
    )

    best = None

    for threshold in thresholds:
        model = AgglomerativeClustering(
            metric="precomputed",
            linkage=LINKAGE,
            distance_threshold=float(
                threshold
            ),
            n_clusters=None
        )

        labels = model.fit_predict(
            distance_matrix
        )

        n_clusters = len(
            set(labels)
        )

        if n_clusters < 2:
            continue

        distance_from_target = abs(
            n_clusters - target
        )

        candidate = (
            distance_from_target,
            threshold,
            n_clusters,
            labels
        )

        if (
            best is None
            or candidate[:2]
            < best[:2]
        ):
            best = candidate

    return best


def build_cluster_detail(
    labels,
    metadata
):
    clusters = {}

    for index, label in enumerate(
        labels
    ):
        label = int(label)

        clusters.setdefault(
            label,
            []
        ).append(
            metadata[index]
        )

    ordered = sorted(
        clusters.items(),
        key=lambda item: len(
            item[1]
        ),
        reverse=True
    )

    detail = []

    for rank, (
        label,
        members
    ) in enumerate(
        ordered,
        start=1
    ):
        detail.append(
            {
                "cluster_rank": rank,
                "size": len(members),
                "members": members
            }
        )

    return detail


def merge_areas(
    client,
    clusters
):
    payload = [
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
        for cluster in clusters
    ]

    message = client.messages.parse(
        model=MODEL_NAME,
        max_tokens=4000,
        thinking={
            "type": "disabled"
        },
        system=MERGE_SYSTEM_PROMPT,
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

    result = message.parsed_output

    expected_ranks = {
        cluster["cluster_rank"]
        for cluster in clusters
    }

    seen_ranks = []

    for area in result.areas:
        seen_ranks.extend(
            area.cluster_ranks
        )

    if (
        len(seen_ranks)
        != len(set(seen_ranks))
        or set(seen_ranks)
        != expected_ranks
    ):
        raise ValueError(
            "cluster_rank 배정이 입력과 일치하지 않습니다."
        )

    if not (
        MIN_AREAS
        <= len(result.areas)
        <= MAX_AREAS
    ):
        raise ValueError(
            "최종 Area 개수가 범위를 벗어났습니다: "
            f"{len(result.areas)}"
        )

    return result


def match_articles_to_areas(
    embed_model,
    company_embeddings,
    company_metadata,
    areas
):
    area_texts = [
        "query: "
        + area.area_name
        + ". "
        + area.area_description
        for area in areas
    ]

    area_embeddings = embed_model.encode(
        area_texts,
        normalize_embeddings=True
    )

    similarity_matrix = cosine_similarity(
        company_embeddings,
        area_embeddings
    )

    rows = []

    for index, article in enumerate(
        company_metadata
    ):
        sims = similarity_matrix[
            index
        ]

        ranked = sorted(
            range(len(areas)),
            key=lambda i: sims[i],
            reverse=True
        )

        best_index = ranked[0]

        best_sim = float(
            sims[best_index]
        )

        second_sim = float(
            sims[ranked[1]]
        )

        margin = (
            best_sim - second_sim
        )

        assigned = (
            best_sim
            >= ASSIGN_THRESHOLD
            and margin
            >= MARGIN_THRESHOLD
        )

        rows.append(
            {
                "article_id": (
                    article["article_id"]
                ),
                "title": article["title"],
                "url": article["url"],
                "assigned_area": (
                    areas[
                        best_index
                    ].area_name
                    if assigned
                    else None
                ),
                "similarity": round(
                    best_sim,
                    4
                ),
                "margin": round(
                    margin,
                    4
                )
            }
        )

    return rows


def extract_tags(
    client,
    areas,
    membership
):
    members_by_area = {}

    for row in membership:
        if row["assigned_area"]:
            members_by_area.setdefault(
                row["assigned_area"],
                []
            ).append(row)

    payload = []

    metadata_by_id = {
        row["article_id"]: row
        for row in membership
    }

    for area in areas:
        members = members_by_area.get(
            area.area_name,
            []
        )

        if not members:
            continue

        payload.append(
            {
                "area_name": (
                    area.area_name
                ),
                "members": [
                    {
                        "title": (
                            metadata_by_id[
                                m["article_id"]
                            ]["title"]
                        ),
                        "engineering_focus": (
                            m.get(
                                "engineering_focus",
                                ""
                            )
                        )
                    }
                    for m in members
                ]
            }
        )

    if not payload:
        return AreaTagBatch(
            areas=[]
        )

    message = client.messages.parse(
        model=MODEL_NAME,
        max_tokens=4000,
        thinking={
            "type": "disabled"
        },
        system=TAG_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "다음 Area들에 대해 대표 키워드 "
                    "태그를 뽑으세요.\n\n"
                    + json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2
                    )
                )
            }
        ],
        output_format=AreaTagBatch
    )

    return message.parsed_output


MIN_UNASSIGNED_FOR_DIAGNOSIS = 8

DIAGNOSTIC_SAMPLE_TITLES = 5


def diagnose_unassigned(
    unassigned_rows,
    company_embeddings,
    company_metadata
):
    # unassigned를 강제로 어떤 Area에도 배정하지 않는다.
    # 대신 unassigned 안에 "사실은 하나의 반복 주제인데
    # 이번 threshold/target에서는 놓친" coherent subcluster가
    # 있는지만 진단해서 보여준다. 사람이 보고 다음 라운드에
    # target을 조정할지 판단하는 데 쓰는 정보다.
    if (
        len(unassigned_rows)
        < MIN_UNASSIGNED_FOR_DIAGNOSIS
    ):
        return []

    id_to_index = {
        article["article_id"]: index
        for index, article in enumerate(
            company_metadata
        )
    }

    indices = [
        id_to_index[row["article_id"]]
        for row in unassigned_rows
        if row["article_id"]
        in id_to_index
    ]

    if len(indices) < (
        MIN_UNASSIGNED_FOR_DIAGNOSIS
    ):
        return []

    subset_embeddings = (
        company_embeddings[indices]
    )

    subset_metadata = [
        company_metadata[i]
        for i in indices
    ]

    distance_matrix = (
        1
        - cosine_similarity(
            subset_embeddings
        )
    )

    distance_matrix = np.clip(
        distance_matrix,
        0,
        None
    )

    target = pick_cluster_target(
        len(subset_metadata)
    )

    best = scan_clusters(
        distance_matrix,
        target
    )

    if best is None:
        return []

    _, threshold, n_clusters, labels = (
        best
    )

    groups = {}

    for index, label in enumerate(
        labels
    ):
        groups.setdefault(
            int(label),
            []
        ).append(
            subset_metadata[index]
        )

    # 크기 2 이상인 subcluster만 "반복되는 묶음" 후보로
    # 본다. 크기 1은 그냥 개별 이상치다.
    coherent_groups = [
        members
        for members in groups.values()
        if len(members) >= 2
    ]

    coherent_groups.sort(
        key=len,
        reverse=True
    )

    return [
        {
            "size": len(members),
            "sample_titles": [
                (
                    member["title"]
                    or "(제목 없음)"
                )
                for member in members[
                    :DIAGNOSTIC_SAMPLE_TITLES
                ]
            ]
        }
        for members in coherent_groups[:5]
    ]


def process_company(
    client,
    embed_model,
    company,
    company_embeddings,
    company_metadata
):
    print()
    print("#" * 60)
    print(
        f"{company} ({len(company_metadata)}개 글)"
    )
    print("#" * 60)

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
            "클러스터링 실패 (데이터 부족)"
        )

        return None

    _, threshold, n_clusters, labels = best

    print(
        f"threshold={threshold:.4f} "
        f"n_clusters={n_clusters} "
        f"(목표 {target})"
    )

    raw_clusters = build_cluster_detail(
        labels,
        company_metadata
    )

    merge_result = None
    last_error = None

    for attempt in range(3):
        try:
            merge_result = merge_areas(
                client,
                raw_clusters
            )

            break

        except ValueError as error:
            last_error = error

            print(
                f"  merge 재시도 "
                f"({attempt + 1}/3): {error}"
            )

    if merge_result is None:
        print(
            f"  {company} merge 실패, 건너뜀: "
            f"{last_error}"
        )

        return None

    for area in merge_result.areas:
        print(
            f" - {area.area_name} "
            f"(cluster {area.cluster_ranks})"
        )

    membership = match_articles_to_areas(
        embed_model,
        company_embeddings,
        company_metadata,
        merge_result.areas
    )

    # membership 행에 engineering_focus를 채운다
    # (태그 추출에서 재사용).
    focus_by_id = {
        m["article_id"]: m[
            "engineering_focus"
        ]
        for m in company_metadata
    }

    for row in membership:
        row["engineering_focus"] = (
            focus_by_id.get(
                row["article_id"],
                ""
            )
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

    for area in merge_result.areas:
        print(
            f"   evidence: "
            f"{assigned_counts.get(area.area_name, 0)}"
        )

    print(
        "unassigned:",
        unassigned_count
    )

    tag_result = extract_tags(
        client,
        merge_result.areas,
        membership
    )

    tags_by_area = {
        area.area_name: [
            tag.tag
            for tag in area.tags
        ]
        for area in tag_result.areas
    }

    final_areas = []

    for area in merge_result.areas:
        members = [
            row
            for row in membership
            if row["assigned_area"]
            == area.area_name
        ]

        final_areas.append(
            {
                "area_name": (
                    area.area_name
                ),
                "area_description": (
                    area.area_description
                ),
                "rationale": (
                    area.rationale
                ),
                "note": area.note,
                "keywords": (
                    tags_by_area.get(
                        area.area_name,
                        []
                    )
                ),
                "article_count": len(
                    members
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
                        )
                    }
                    for m in members
                ]
            }
        )

    unassigned_rows = [
        row
        for row in membership
        if not row["assigned_area"]
    ]

    unassigned_diagnostic = (
        diagnose_unassigned(
            unassigned_rows,
            company_embeddings,
            company_metadata
        )
    )

    if unassigned_diagnostic:
        print(
            "  unassigned 내부 subcluster "
            "진단:"
        )

        for group in (
            unassigned_diagnostic
        ):
            print(
                f"    size={group['size']}"
            )

            for title in group[
                "sample_titles"
            ]:
                print(
                    "      -",
                    title
                )

    company_result = {
        "company": company,
        "article_count": len(
            company_metadata
        ),
        "clustering": {
            "linkage": LINKAGE,
            "threshold": threshold,
            "raw_cluster_count": (
                n_clusters
            ),
            "target": target
        },
        "areas": final_areas,
        "unassigned_count": len(
            unassigned_rows
        ),
        "unassigned_diagnostic": (
            unassigned_diagnostic
        )
    }

    save_json(
        AREAS_OUTPUT_DIR
        / f"{company}.json",
        company_result
    )

    return company_result


def main():
    if not os.getenv(
        "ANTHROPIC_API_KEY"
    ):
        raise RuntimeError(
            "ANTHROPIC_API_KEY가 설정되어 있지 않습니다."
        )

    embeddings = np.load(
        EMBEDDINGS_FILE
    )

    metadata = load_json(
        METADATA_FILE
    )

    client = Anthropic()

    embed_model = SentenceTransformer(
        EMBED_MODEL_NAME
    )

    companies = sorted(
        {
            item["company"]
            for item in metadata
        }
    )

    all_results = []

    for company in companies:
        indices = [
            i
            for i, item in enumerate(
                metadata
            )
            if item["company"]
            == company
        ]

        company_embeddings = (
            embeddings[indices]
        )

        company_metadata = [
            metadata[i]
            for i in indices
        ]

        result = process_company(
            client,
            embed_model,
            company,
            company_embeddings,
            company_metadata
        )

        if result:
            all_results.append(
                result
            )

    save_json(
        RESEARCH_DIR
        / "track_b_pilot_areas.json",
        all_results
    )

    lines = [
        "# Track B: 파일럿 5개 회사 Area 생성 결과",
        "",
        (
            "engineering_focus -> v4 embedding -> "
            "clustering(complete linkage) -> LLM 병합 -> "
            "deterministic membership -> 키워드 태깅 "
            "전체 파이프라인을 5개 회사에 독립적으로 적용한 "
            "결과다."
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
        RESEARCH_DIR
        / "track_b_pilot_areas.md",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(lines)
        )

    print()
    print("=" * 60)
    print("TRACK B 파일럿 완료")
    print("=" * 60)

    print(
        "저장:",
        RESEARCH_DIR
        / "track_b_pilot_areas.md"
    )


if __name__ == "__main__":
    main()
