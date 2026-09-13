import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[4]

EMBEDDINGS_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v4"
    / "article_embeddings.npy"
)

METADATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v4"
    / "articles.json"
)

AREAS_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "areas.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
)

MEMBERSHIP_FILE = (
    OUTPUT_DIR
    / "area_membership.json"
)

EVIDENCE_FILE = (
    OUTPUT_DIR
    / "area_evidence_final.json"
)


MODEL_NAME = "intfloat/multilingual-e5-small"

ASSIGN_THRESHOLD = 0.86
MARGIN_THRESHOLD = 0.0032


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


def build_area_query_text(area):
    return (
        "query: "
        + area["area_name"]
        + ". "
        + area["area_description"]
    )


def build_original_area_lookup(
    areas,
    cluster_file
):
    cluster_data = load_json(
        cluster_file
    )

    clusters_by_rank = {
        cluster["cluster_rank"]: cluster
        for cluster in cluster_data[
            "clusters"
        ]
    }

    lookup = {}

    for area in areas:
        for rank in area[
            "cluster_ranks"
        ]:
            cluster = clusters_by_rank[
                rank
            ]

            for member in cluster[
                "members"
            ]:
                lookup[
                    member["title"]
                ] = area["area_name"]

    return lookup


def main():
    article_embeddings = np.load(
        EMBEDDINGS_FILE
    )

    articles = load_json(
        METADATA_FILE
    )

    areas_data = load_json(
        AREAS_FILE
    )

    areas = areas_data["areas"]

    original_area_by_title = (
        build_original_area_lookup(
            areas,
            Path(
                areas_data[
                    "source_cluster_file"
                ]
            )
        )
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    area_texts = [
        build_area_query_text(area)
        for area in areas
    ]

    area_embeddings = model.encode(
        area_texts,
        normalize_embeddings=True
    )

    similarity_matrix = (
        cosine_similarity(
            article_embeddings,
            area_embeddings
        )
    )

    print()
    print("=" * 60)
    print(
        "ARTICLE -> AREA 유사도 "
        f"(threshold={ASSIGN_THRESHOLD}, "
        f"margin>={MARGIN_THRESHOLD})"
    )
    print("=" * 60)

    rows = []

    for index, article in enumerate(
        articles
    ):
        sims = similarity_matrix[
            index
        ]

        ranked = sorted(
            range(
                len(areas)
            ),
            key=lambda i: sims[i],
            reverse=True
        )

        best_area_index = ranked[0]

        best_area_name = areas[
            best_area_index
        ]["area_name"]

        best_sim = float(
            sims[best_area_index]
        )

        second_sim = float(
            sims[ranked[1]]
        )

        margin_value = (
            best_sim - second_sim
        )

        assigned = (
            best_sim
            >= ASSIGN_THRESHOLD
            and margin_value
            >= MARGIN_THRESHOLD
        )

        assigned_area_name = (
            areas[
                best_area_index
            ]["area_name"]
            if assigned
            else None
        )

        original_area_name = (
            original_area_by_title.get(
                article["title"]
            )
        )

        changed = (
            assigned
            and original_area_name
            != assigned_area_name
        )

        row = {
            "article_id": (
                article["article_id"]
            ),
            "title": article["title"],
            "company": article["company"],
            "url": article["url"],
            "original_area": (
                original_area_name
            ),
            "assigned_area": (
                assigned_area_name
            ),
            "closest_area": (
                best_area_name
            ),
            "best_similarity": round(
                best_sim,
                4
            ),
            "margin": round(
                best_sim - second_sim,
                4
            ),
            "all_similarities": {
                areas[i]["area_name"]: round(
                    float(sims[i]),
                    4
                )
                for i in range(
                    len(areas)
                )
            }
        }

        rows.append(row)

    rows.sort(
        key=lambda row: (
            row["best_similarity"]
        ),
        reverse=True
    )

    for row in rows:
        status = (
            row["assigned_area"]
            if row["assigned_area"]
            else "UNASSIGNED"
        )

        change_marker = (
            "  [moved from "
            f"{row['original_area']}]"
            if row["assigned_area"]
            and row["original_area"]
            != row["assigned_area"]
            else ""
        )

        print(
            f"{row['best_similarity']:.4f}"
            f"  {status}"
            f"{change_marker}"
        )

        print(
            "   ",
            row["title"]
        )

    evidence = {}

    unassigned = []

    for row in rows:
        if row["assigned_area"]:
            evidence.setdefault(
                row["assigned_area"],
                []
            ).append(row)
        else:
            unassigned.append(row)

    print()
    print("=" * 60)
    print("최종 EVIDENCE COUNT")
    print("=" * 60)

    for area in areas:
        members = evidence.get(
            area["area_name"],
            []
        )

        print(
            f"{area['area_name']}:",
            len(members),
            "개"
        )

    print(
        "unassigned:",
        len(unassigned),
        "개"
    )

    for row in unassigned:
        print(
            "   -",
            row["title"],
            f"(best={row['best_similarity']:.4f}"
            f" margin={row['margin']:.4f}"
            f" -> {row['closest_area']})"
        )

    save_json(
        MEMBERSHIP_FILE,
        {
            "model": MODEL_NAME,
            "threshold": ASSIGN_THRESHOLD,
            "articles": rows
        }
    )

    final_evidence = []

    for area in areas:
        members = evidence.get(
            area["area_name"],
            []
        )

        final_evidence.append(
            {
                "area_name": (
                    area["area_name"]
                ),
                "area_description": (
                    area["area_description"]
                ),
                "article_count": len(
                    members
                ),
                "articles": [
                    {
                        "article_id": (
                            member[
                                "article_id"
                            ]
                        ),
                        "title": (
                            member["title"]
                        ),
                        "company": (
                            member["company"]
                        ),
                        "url": (
                            member["url"]
                        ),
                        "similarity": (
                            member[
                                "best_similarity"
                            ]
                        )
                    }
                    for member in members
                ]
            }
        )

    final_evidence.append(
        {
            "area_name": "unassigned",
            "area_description": (
                "threshold 미달로 어느 Area에도 "
                "충분히 가깝지 않은 게시글"
            ),
            "article_count": len(
                unassigned
            ),
            "articles": [
                {
                    "article_id": (
                        row["article_id"]
                    ),
                    "title": row["title"],
                    "company": row["company"],
                    "url": row["url"],
                    "best_similarity": (
                        row["best_similarity"]
                    ),
                    "closest_area": (
                        row["closest_area"]
                    )
                }
                for row in unassigned
            ]
        }
    )

    save_json(
        EVIDENCE_FILE,
        final_evidence
    )

    print()
    print("저장:", MEMBERSHIP_FILE)
    print("저장:", EVIDENCE_FILE)


if __name__ == "__main__":
    main()
