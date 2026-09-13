import html
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[4]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "extracted"
    / "articles.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "embeddings_v3"
)

EMBEDDINGS_FILE = (
    OUTPUT_DIR
    / "article_embeddings.npy"
)

METADATA_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "embed_report.json"
)


MODEL_NAME = "intfloat/multilingual-e5-small"


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


def normalize_text(text):
    if not text:
        return ""

    return html.unescape(
        text
    ).strip()


def create_article_embedding(
    model,
    article
):
    title = normalize_text(
        article["title"]
    )

    embedding = model.encode(
        "passage: " + title,
        normalize_embeddings=True
    )

    return (
        embedding,
        title
    )


def main():
    articles = load_json(
        INPUT_FILE
    )

    if not articles:
        raise ValueError(
            "입력 게시글이 없습니다."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("EMBED V3 시작 - TITLE ONLY")
    print("=" * 60)

    print(
        "모델:",
        MODEL_NAME
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "device:",
        model.device
    )

    embeddings = []
    metadata = []

    for index, article in enumerate(
        articles,
        start=1
    ):
        (
            embedding,
            normalized_title
        ) = create_article_embedding(
            model,
            article
        )

        print(
            f"[{index}/{len(articles)}]",
            normalized_title
        )

        embeddings.append(
            embedding
        )

        metadata.append(
            {
                "index": index - 1,
                "article_id": article[
                    "article_id"
                ],
                "company": article[
                    "company"
                ],
                "title": normalized_title,
                "published_at": article[
                    "published_at"
                ],
                "url": article[
                    "url"
                ]
            }
        )

    embedding_matrix = np.vstack(
        embeddings
    )

    np.save(
        EMBEDDINGS_FILE,
        embedding_matrix
    )

    save_json(
        METADATA_FILE,
        metadata
    )

    report = {
        "model": MODEL_NAME,
        "representation": "title_only",
        "article_count": len(
            articles
        ),
        "embedding_dimension": int(
            embedding_matrix.shape[1]
        )
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("EMBED V3 완료")
    print("=" * 60)

    print(
        "게시글:",
        len(articles)
    )

    print(
        "embedding shape:",
        embedding_matrix.shape
    )

    print(
        "저장:",
        EMBEDDINGS_FILE
    )


if __name__ == "__main__":
    main()
    