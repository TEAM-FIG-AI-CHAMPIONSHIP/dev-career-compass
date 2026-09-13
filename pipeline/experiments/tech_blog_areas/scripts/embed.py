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
    / "embeddings"
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

MAX_CHUNK_TOKENS = 400
CHUNK_OVERLAP = 50

TITLE_WEIGHT = 0.3
CONTENT_WEIGHT = 0.7


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

    text = html.unescape(
        text
    )

    return text.strip()


def split_into_chunks(
    text,
    tokenizer
):
    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False
    )

    chunks = []

    start = 0

    while start < len(token_ids):
        end = min(
            start + MAX_CHUNK_TOKENS,
            len(token_ids)
        )

        chunk_ids = token_ids[
            start:end
        ]

        chunk = tokenizer.decode(
            chunk_ids,
            skip_special_tokens=True
        ).strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= len(token_ids):
            break

        start = (
            end
            - CHUNK_OVERLAP
        )

    return chunks


def normalize_vector(vector):
    norm = np.linalg.norm(
        vector
    )

    if norm == 0:
        return vector

    return vector / norm


def create_article_embedding(
    model,
    article
):
    title = normalize_text(
        article["title"]
    )

    content = normalize_text(
        article["content"]
    )

    chunks = split_into_chunks(
        content,
        model.tokenizer
    )

    title_embedding = model.encode(
        "passage: " + title,
        normalize_embeddings=True
    )

    chunk_inputs = [
        "passage: " + chunk
        for chunk in chunks
    ]

    chunk_embeddings = model.encode(
        chunk_inputs,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    content_embedding = np.mean(
        chunk_embeddings,
        axis=0
    )

    article_embedding = (
        TITLE_WEIGHT
        * title_embedding
        + CONTENT_WEIGHT
        * content_embedding
    )

    article_embedding = normalize_vector(
        article_embedding
    )

    return (
        article_embedding,
        len(chunks),
        title
    )


def main():
    articles = load_json(
        INPUT_FILE
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("EMBED 시작")
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

    total_chunks = 0

    for index, article in enumerate(
        articles,
        start=1
    ):
        print(
            f"[{index}/{len(articles)}]",
            normalize_text(
                article["title"]
            )
        )

        (
            embedding,
            chunk_count,
            normalized_title
        ) = create_article_embedding(
            model,
            article
        )

        embeddings.append(
            embedding
        )

        total_chunks += chunk_count

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
                ],
                "chunk_count": (
                    chunk_count
                )
            }
        )

        print(
            "  →",
            chunk_count,
            "chunks"
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
        "article_count": (
            len(articles)
        ),
        "embedding_dimension": (
            int(
                embedding_matrix.shape[1]
            )
        ),
        "total_chunks": (
            total_chunks
        ),
        "average_chunks": (
            round(
                total_chunks
                / len(articles),
                2
            )
            if articles
            else 0
        ),
        "max_chunk_tokens": (
            MAX_CHUNK_TOKENS
        ),
        "chunk_overlap": (
            CHUNK_OVERLAP
        ),
        "title_weight": (
            TITLE_WEIGHT
        ),
        "content_weight": (
            CONTENT_WEIGHT
        )
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("EMBED 완료")
    print("=" * 60)

    print(
        "게시글:",
        len(articles)
    )

    print(
        "총 chunk:",
        total_chunks
    )

    print(
        "평균 chunk:",
        report[
            "average_chunks"
        ]
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
    