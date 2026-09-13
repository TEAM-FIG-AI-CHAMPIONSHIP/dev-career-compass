import json
from pathlib import Path

import numpy as np
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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v4"
    / "similarity_report.json"
)


TOP_PAIR_COUNT = 20
NEIGHBOR_COUNT = 5


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


def calculate_distribution(
    similarity_matrix
):
    article_count = (
        similarity_matrix.shape[0]
    )

    values = []

    for i in range(article_count):
        for j in range(
            i + 1,
            article_count
        ):
            values.append(
                similarity_matrix[i][j]
            )

    values = np.array(
        values
    )

    percentiles = [
        0,
        10,
        25,
        50,
        75,
        90,
        95,
        99,
        100
    ]

    distribution = {}

    for percentile in percentiles:
        distribution[
            f"p{percentile}"
        ] = round(
            float(
                np.percentile(
                    values,
                    percentile
                )
            ),
            4
        )

    distribution["mean"] = round(
        float(
            np.mean(values)
        ),
        4
    )

    distribution["std"] = round(
        float(
            np.std(values)
        ),
        4
    )

    return distribution


def find_top_pairs(
    similarity_matrix,
    metadata
):
    pairs = []

    article_count = (
        similarity_matrix.shape[0]
    )

    for i in range(article_count):
        for j in range(
            i + 1,
            article_count
        ):
            pairs.append(
                {
                    "similarity": float(
                        similarity_matrix[i][j]
                    ),
                    "left": metadata[i],
                    "right": metadata[j]
                }
            )

    pairs.sort(
        key=lambda pair: (
            pair["similarity"]
        ),
        reverse=True
    )

    return pairs[
        :TOP_PAIR_COUNT
    ]


def find_neighbors(
    similarity_matrix,
    metadata
):
    results = []

    for i, article in enumerate(
        metadata
    ):
        similarities = []

        for j, other in enumerate(
            metadata
        ):
            if i == j:
                continue

            similarities.append(
                {
                    "index": j,
                    "similarity": float(
                        similarity_matrix[i][j]
                    ),
                    "article_id": (
                        other["article_id"]
                    ),
                    "title": (
                        other["title"]
                    ),
                    "url": (
                        other["url"]
                    )
                }
            )

        similarities.sort(
            key=lambda item: (
                item["similarity"]
            ),
            reverse=True
        )

        results.append(
            {
                "index": i,
                "article_id": (
                    article["article_id"]
                ),
                "title": (
                    article["title"]
                ),
                "neighbors": (
                    similarities[
                        :NEIGHBOR_COUNT
                    ]
                )
            }
        )

    return results


def main():
    embeddings = np.load(
        EMBEDDINGS_FILE
    )

    metadata = load_json(
        METADATA_FILE
    )

    if len(embeddings) != len(
        metadata
    ):
        raise ValueError(
            "embedding 개수와 metadata 개수가 다릅니다."
        )

    similarity_matrix = (
        cosine_similarity(
            embeddings
        )
    )

    distribution = (
        calculate_distribution(
            similarity_matrix
        )
    )

    top_pairs = find_top_pairs(
        similarity_matrix,
        metadata
    )

    neighbors = find_neighbors(
        similarity_matrix,
        metadata
    )

    report = {
        "article_count": len(
            metadata
        ),
        "distribution": (
            distribution
        ),
        "top_pairs": [
            {
                "similarity": round(
                    pair["similarity"],
                    4
                ),
                "left": {
                    "article_id": (
                        pair["left"][
                            "article_id"
                        ]
                    ),
                    "title": (
                        pair["left"][
                            "title"
                        ]
                    ),
                    "url": (
                        pair["left"][
                            "url"
                        ]
                    )
                },
                "right": {
                    "article_id": (
                        pair["right"][
                            "article_id"
                        ]
                    ),
                    "title": (
                        pair["right"][
                            "title"
                        ]
                    ),
                    "url": (
                        pair["right"][
                            "url"
                        ]
                    )
                }
            }
            for pair in top_pairs
        ],
        "neighbors": neighbors
    }

    save_json(
        OUTPUT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("SIMILARITY 검사")
    print("=" * 60)

    print()
    print("게시글:", len(metadata))

    print()
    print("전체 pair cosine similarity 분포")

    for key, value in (
        distribution.items()
    ):
        print(
            f"{key:>6}:",
            value
        )

    print()
    print("=" * 60)
    print(
        f"가장 유사한 {TOP_PAIR_COUNT}개 pair"
    )
    print("=" * 60)

    for rank, pair in enumerate(
        top_pairs,
        start=1
    ):
        print()
        print(
            f"{rank:02d}.",
            f"{pair['similarity']:.4f}"
        )

        print(
            " A:",
            pair["left"]["title"]
        )

        print(
            " B:",
            pair["right"]["title"]
        )

    print()
    print("상세 결과 저장:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
    