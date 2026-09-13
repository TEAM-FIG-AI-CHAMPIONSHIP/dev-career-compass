import json
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "clustering_v4"
)

SCAN_REPORT_FILE = (
    OUTPUT_DIR
    / "cluster_scan_report.json"
)


LINKAGE_METHODS = [
    "average",
    "complete"
]

THRESHOLD_MIN = 0.03
THRESHOLD_MAX = 0.25
THRESHOLD_STEP = 0.005

TARGET_MIN_CLUSTERS = 6
TARGET_MAX_CLUSTERS = 10


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


def cluster_sizes(labels):
    sizes = {}

    for label in labels:
        sizes[label] = (
            sizes.get(label, 0) + 1
        )

    return sorted(
        sizes.values(),
        reverse=True
    )


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
                "cluster_label": label,
                "size": len(members),
                "members": [
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

    return detail


def print_cluster_detail(detail):
    for group in detail:
        print()
        print(
            f"--- cluster {group['cluster_rank']} "
            f"(size={group['size']}) ---"
        )

        for member in group["members"]:
            print(
                f"  [{member['company']}]",
                member["title"]
            )

            print(
                "    →",
                member["engineering_focus"]
            )


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

    distance_matrix = (
        1
        - cosine_similarity(
            embeddings
        )
    )

    distance_matrix = np.clip(
        distance_matrix,
        0,
        None
    )

    thresholds = np.round(
        np.arange(
            THRESHOLD_MIN,
            THRESHOLD_MAX
            + THRESHOLD_STEP,
            THRESHOLD_STEP
        ),
        4
    )

    print()
    print("=" * 60)
    print(
        "AGGLOMERATIVE CLUSTERING SCAN "
        "(cosine distance, v4 embedding)"
    )
    print("=" * 60)

    scan_rows = []
    candidates = []

    for linkage in LINKAGE_METHODS:
        print()
        print(
            f"[linkage={linkage}]"
        )

        prev_n_clusters = None

        for threshold in thresholds:
            model = AgglomerativeClustering(
                metric="precomputed",
                linkage=linkage,
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

            if (
                n_clusters
                == prev_n_clusters
            ):
                continue

            prev_n_clusters = (
                n_clusters
            )

            sizes = cluster_sizes(
                labels
            )

            singleton_count = sum(
                1
                for size in sizes
                if size == 1
            )

            row = {
                "linkage": linkage,
                "threshold": round(
                    float(threshold),
                    4
                ),
                "n_clusters": (
                    n_clusters
                ),
                "sizes": sizes,
                "singleton_count": (
                    singleton_count
                )
            }

            scan_rows.append(row)

            marker = (
                " <== target range"
                if (
                    TARGET_MIN_CLUSTERS
                    <= n_clusters
                    <= TARGET_MAX_CLUSTERS
                )
                else ""
            )

            print(
                f"  threshold={row['threshold']:.4f}"
                f"  n_clusters={n_clusters:2d}"
                f"  singletons={singleton_count}"
                f"  sizes={sizes}"
                f"{marker}"
            )

            if (
                TARGET_MIN_CLUSTERS
                <= n_clusters
                <= TARGET_MAX_CLUSTERS
            ):
                candidates.append(
                    (
                        linkage,
                        float(threshold),
                        labels
                    )
                )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    save_json(
        SCAN_REPORT_FILE,
        scan_rows
    )

    print()
    print("=" * 60)
    print(
        f"target range {TARGET_MIN_CLUSTERS}"
        f"~{TARGET_MAX_CLUSTERS} clusters 후보: "
        f"{len(candidates)}개"
    )
    print("=" * 60)

    seen_signatures = set()

    for (
        linkage,
        threshold,
        labels
    ) in candidates:
        signature = (
            linkage,
            tuple(
                sorted(
                    cluster_sizes(labels)
                )
            )
        )

        if signature in seen_signatures:
            continue

        seen_signatures.add(
            signature
        )

        detail = build_cluster_detail(
            labels,
            metadata
        )

        print()
        print(
            "#" * 60
        )
        print(
            f"linkage={linkage}  threshold={threshold:.4f}"
            f"  n_clusters={len(detail)}"
        )
        print(
            "#" * 60
        )

        print_cluster_detail(
            detail
        )

        detail_file = (
            OUTPUT_DIR
            / (
                f"cluster_detail_{linkage}_"
                f"{len(detail)}"
                f"_{threshold:.4f}.json"
            )
        )

        save_json(
            detail_file,
            {
                "linkage": linkage,
                "threshold": threshold,
                "n_clusters": len(
                    detail
                ),
                "clusters": detail
            }
        )

    print()
    print("=" * 60)
    print("SCAN 완료")
    print("=" * 60)

    print(
        "전체 스캔 결과:",
        SCAN_REPORT_FILE
    )

    print(
        "후보 상세 결과:",
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()
