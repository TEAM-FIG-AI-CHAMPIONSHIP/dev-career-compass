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
    / "tech_blog_engineering_focus_29"
    / "articles.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
    / "embeddings_v4"
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

TITLE_WEIGHT = 0.3
FOCUS_WEIGHT = 0.7

# LLM이 실제로 다룰 엔지니어링 내용을 찾지 못했다고 스스로
# 밝힌 결과(예: 태그/목록 페이지가 잘못 수집된 경우)는
# 임베딩 대상에서 제외한다. 회사별 규칙이 아니라 결과
# 텍스트 자체를 보는 일반 규칙이다.
LOW_SIGNAL_MARKERS = (
    "확인할 수 없음",
    "판단할 수 없음",
    "알 수 없음"
)


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


def normalize_vector(vector):
    norm = np.linalg.norm(
        vector
    )

    if norm == 0:
        return vector

    return vector / norm


def is_low_signal(article):
    focus = article.get(
        "engineering_focus",
        ""
    )

    return any(
        marker in focus
        for marker in LOW_SIGNAL_MARKERS
    )


def create_article_embedding(
    model,
    article
):
    title = normalize_text(
        article["title"]
    )

    engineering_focus = normalize_text(
        article["engineering_focus"]
    )

    focus_embedding = model.encode(
        "passage: " + engineering_focus,
        normalize_embeddings=True
    )

    # title이 없으면(백필 실패 등) 30% 자리에 빈 문자열을
    # 그대로 넣지 않는다. 빈/무효 title은 임베딩에서 아예
    # 빼고 focus 100%로 재정규화한다 — 그래야 "제목이 없는
    # 글들끼리 비슷해 보이는" 인위적인 뭉침이 생기지 않는다.
    if not title:
        return (
            focus_embedding,
            title,
            engineering_focus
        )

    title_embedding = model.encode(
        "passage: " + title,
        normalize_embeddings=True
    )

    article_embedding = (
        TITLE_WEIGHT * title_embedding
        + FOCUS_WEIGHT * focus_embedding
    )

    article_embedding = normalize_vector(
        article_embedding
    )

    return (
        article_embedding,
        title,
        engineering_focus
    )


def main():
    articles = load_json(
        INPUT_FILE
    )

    if not articles:
        raise ValueError(
            "engineering focus 게시글이 없습니다."
        )

    before_filter = len(
        articles
    )

    articles = [
        article
        for article in articles
        if not is_low_signal(
            article
        )
    ]

    excluded_low_signal = (
        before_filter
        - len(articles)
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print(
        "EMBED V4 시작 - TITLE + ENGINEERING FOCUS "
        "(Track B 파일럿)"
    )
    print("=" * 60)

    print(
        "모델:",
        MODEL_NAME
    )

    print(
        "title weight:",
        TITLE_WEIGHT
    )

    print(
        "focus weight:",
        FOCUS_WEIGHT
    )

    print(
        "저신호로 제외:",
        excluded_low_signal
    )

    print(
        "임베딩 대상:",
        len(articles)
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
            normalized_title,
            engineering_focus
        ) = create_article_embedding(
            model,
            article
        )

        print(
            f"[{index}/{len(articles)}]",
            f"[{article['company']}]",
            normalized_title
            or "(제목 없음)"
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
                "engineering_focus": (
                    engineering_focus
                ),
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

    company_counts = {}

    for item in metadata:
        company_counts[
            item["company"]
        ] = (
            company_counts.get(
                item["company"],
                0
            )
            + 1
        )

    report = {
        "model": MODEL_NAME,
        "representation": (
            "title_30_focus_70"
        ),
        "article_count": len(
            articles
        ),
        "excluded_low_signal": (
            excluded_low_signal
        ),
        "embedding_dimension": int(
            embedding_matrix.shape[1]
        ),
        "title_weight": (
            TITLE_WEIGHT
        ),
        "focus_weight": (
            FOCUS_WEIGHT
        ),
        "company_counts": (
            company_counts
        )
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("EMBED V4 완료")
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
        "회사별:",
        company_counts
    )

    print(
        "저장:",
        EMBEDDINGS_FILE
    )


if __name__ == "__main__":
    main()
