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
    / "embeddings_v2"
    / "article_embeddings.npy"
)

METADATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v2"
    / "articles.json"
)

CLASSIFIED_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "classified"
    / "articles.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v2"
    / "similarity_filtered_report.json"
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


def save_json(
    path,
    data
):
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


def filter_embeddings(
    embeddings,
    metadata,
    classified
):
    classification_by_id = {
        article["article_id"]: article
        for article in classified
    }

    selected_embeddings = []
    selected_metadata = []

    for index, article in enumerate(
        metadata
    ):
        article_id = article[
            "article_id"
        ]

        classification = (
            classification_by_id.get(
                article_id
            )
        )

        if not classification:
            continue

        if not classification.get(
            "include_for_area",
            False
        ):
            continue

        selected_embeddings.append(
            embeddings[index]
        )

        selected_metadata.append(
            {
                **article,
                "category": (
                    classification[
                        "category"
                    ]
                ),
                "technical_relevance": (
                    classification[
                        "technical_relevance"
                    ]
                )
            }
        )

    if not selected_embeddings:
        raise ValueError(
            "Area 생성 대상으로 남은 게시글이 없습니다."
        )

    return (
        np.vstack(
            selected_embeddings
        ),
        selected_metadata
    )


def calculate_distribution(
    similarity_matrix
):
    article_count = (
        similarity_matrix.shape[0]
    )

    values = []

    for i in range(
        article_count
    ):
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
            np.mean(
                values
            )
        ),
        4
    )

    distribution["std"] = round(
        float(
            np.std(
                values
            )
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

    for i in range(
        article_count
    ):
        for j in range(
            i + 1,
            article_count
        ):
            pairs.append(
                {
                    "similarity": float(
                        similarity_matrix[
                            i
                        ][
                            j
                        ]
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
        neighbors = []

        for j, other in enumerate(
            metadata
        ):
            if i == j:
                continue

            neighbors.append(
                {
                    "similarity": float(
                        similarity_matrix[
                            i
                        ][
                            j
                        ]
                    ),
                    "article_id": (
                        other[
                            "article_id"
                        ]
                    ),
                    "title": (
                        other[
                            "title"
                        ]
                    ),
                    "url": (
                        other[
                            "url"
                        ]
                    )
                }
            )

        neighbors.sort(
            key=lambda item: (
                item["similarity"]
            ),
            reverse=True
        )

        results.append(
            {
                "article_id": (
                    article[
                        "article_id"
                    ]
                ),
                "title": (
                    article[
                        "title"
                    ]
                ),
                "neighbors": (
                    neighbors[
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

    classified = load_json(
        CLASSIFIED_FILE
    )

    if len(embeddings) != len(
        metadata
    ):
        raise ValueError(
            "embedding 개수와 metadata 개수가 다릅니다."
        )

    (
        filtered_embeddings,
        filtered_metadata
    ) = filter_embeddings(
        embeddings,
        metadata,
        classified
    )

    similarity_matrix = (
        cosine_similarity(
            filtered_embeddings
        )
    )

    distribution = (
        calculate_distribution(
            similarity_matrix
        )
    )

    top_pairs = find_top_pairs(
        similarity_matrix,
        filtered_metadata
    )

    neighbors = find_neighbors(
        similarity_matrix,
        filtered_metadata
    )

    report = {
        "original_article_count": (
            len(metadata)
        ),
        "filtered_article_count": (
            len(filtered_metadata)
        ),
        "distribution": (
            distribution
        ),
        "top_pairs": [
            {
                "similarity": round(
                    pair[
                        "similarity"
                    ],
                    4
                ),
                "left": {
                    "article_id": (
                        pair[
                            "left"
                        ][
                            "article_id"
                        ]
                    ),
                    "title": (
                        pair[
                            "left"
                        ][
                            "title"
                        ]
                    ),
                    "category": (
                        pair[
                            "left"
                        ][
                            "category"
                        ]
                    )
                },
                "right": {
                    "article_id": (
                        pair[
                            "right"
                        ][
                            "article_id"
                        ]
                    ),
                    "title": (
                        pair[
                            "right"
                        ][
                            "title"
                        ]
                    ),
                    "category": (
                        pair[
                            "right"
                        ][
                            "category"
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
    print("FILTERED SIMILARITY 검사")
    print("=" * 60)

    print()
    print(
        "전체 게시글:",
        len(metadata)
    )

    print(
        "Area 대상:",
        len(filtered_metadata)
    )

    print(
        "제외:",
        len(metadata)
        - len(filtered_metadata)
    )

    print()
    print(
        "전체 pair cosine similarity 분포"
    )

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
        f"가장 유사한 "
        f"{TOP_PAIR_COUNT}개 pair"
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
            pair[
                "left"
            ][
                "title"
            ]
        )

        print(
            " B:",
            pair[
                "right"
            ][
                "title"
            ]
        )

    print()
    print(
        "상세 결과 저장:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
    