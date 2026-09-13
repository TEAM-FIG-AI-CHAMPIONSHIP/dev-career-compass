import html
import json
import os
import re

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from anthropic import Anthropic
from pydantic import BaseModel


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
    / "classified"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "classify_report.json"
)


MODEL_NAME = "claude-sonnet-5"

CLASSIFIER_VERSION = "v1"

BATCH_SIZE = 10
EXCERPT_CHARS = 1800


AREA_CATEGORIES = {
    "ENGINEERING_CASE",
    "TECH_RESEARCH",
}


SYSTEM_PROMPT = """
당신은 기업 기술블로그 게시글을 분류하는 분석기입니다.

목적은 회사의 반복적인 엔지니어링 영역을 추출하기 전에
Area 생성에 사용할 기술 게시글과 그렇지 않은 게시글을 구분하는 것입니다.

각 글의 제목만 보지 말고 제공된 본문 발췌까지 함께 판단하세요.

다음 category 중 하나만 선택하세요.

ENGINEERING_CASE
- 실제 시스템, 서비스, 도구를 구현하거나 개선한 경험
- 장애 해결, 성능 개선, 마이그레이션, 아키텍처 변경
- 운영 자동화, 트러블슈팅, 기술 도입
- 구체적인 엔지니어링 문제와 해결 과정이 중심인 글

TECH_RESEARCH
- 기술 개념, 방법론, 라이브러리, 아키텍처 등을 조사하거나 실험한 글
- 실제 서비스 적용을 위한 기술 비교, 검증, 연구
- 충분한 기술적 내용이 있는 연구/실험 글

TECH_CULTURE
- 개발 문화, 협업, 조직 변화, 코드 리뷰 문화, 업무 방식 등이 중심인 글
- 기술 구현보다 사람/프로세스/문화가 중심인 글

PROMOTION_EVENT
- 행사 안내, 행사 등록, 컨퍼런스 홍보, 책 출간 홍보 등이 중심인 글
- 행사 이름이 들어갔다는 이유만으로 이 category를 선택하면 안 됩니다.
- 행사나 해커톤을 소재로 하더라도 실제 시스템 구현 과정이 중심이면
  ENGINEERING_CASE로 분류하세요.

NOTICE_EDUCATION
- 개인정보처리방침 변경 등 일반 공지
- 교육 과정 모집, 교육 프로그램 소개 등이 중심인 글

OTHER
- 위 분류에 명확히 속하지 않는 글

technical_relevance는 다음 기준입니다.

HIGH
- 구체적인 엔지니어링 문제, 기술 선택, 구현, 운영 내용이 글의 중심

MEDIUM
- 의미 있는 기술 내용이 있지만 다른 목적과 섞여 있음

LOW
- 실질적인 엔지니어링 내용이 거의 없음

중요:
- 단순히 AI, Redis, Kafka 같은 기술 단어가 등장한다고 HIGH로 판단하지 마세요.
- 행사 글이라도 시스템 구현 내용이 중심이면 ENGINEERING_CASE가 될 수 있습니다.
- 제목에 기술적인 표현이 없어도 본문이 실제 구현 경험이면 ENGINEERING_CASE입니다.
- 제공된 텍스트에서 확인할 수 없는 내용은 추측하지 마세요.
- reason은 분류 근거를 짧은 한 문장으로 작성하세요.
"""


class ArticleClassification(BaseModel):
    article_id: str

    category: Literal[
        "ENGINEERING_CASE",
        "TECH_RESEARCH",
        "TECH_CULTURE",
        "PROMOTION_EVENT",
        "NOTICE_EDUCATION",
        "OTHER",
    ]

    technical_relevance: Literal[
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    reason: str


class ClassificationBatch(BaseModel):
    results: list[ArticleClassification]


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

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def create_excerpt(content):
    content = normalize_text(
        content
    )

    return content[
        :EXCERPT_CHARS
    ]


def load_cache():
    if not OUTPUT_FILE.exists():
        return {}

    try:
        data = load_json(
            OUTPUT_FILE
        )

    except (
        json.JSONDecodeError,
        OSError
    ):
        return {}

    cache = {}

    for item in data:
        article_id = item.get(
            "article_id"
        )

        content_hash = item.get(
            "content_hash"
        )

        classifier_version = item.get(
            "classifier_version"
        )

        if (
            article_id
            and content_hash
            and classifier_version
            == CLASSIFIER_VERSION
        ):
            cache[
                (
                    article_id,
                    content_hash
                )
            ] = item

    return cache


def build_batch_payload(
    articles
):
    payload = []

    for article in articles:
        payload.append(
            {
                "article_id": (
                    article[
                        "article_id"
                    ]
                ),
                "title": normalize_text(
                    article[
                        "title"
                    ]
                ),
                "excerpt": create_excerpt(
                    article[
                        "content"
                    ]
                ),
            }
        )

    return payload


def validate_batch_result(
    articles,
    classifications
):
    expected_ids = {
        article[
            "article_id"
        ]
        for article in articles
    }

    returned_ids = [
        classification.article_id
        for classification
        in classifications
    ]

    if len(returned_ids) != len(
        set(returned_ids)
    ):
        raise ValueError(
            "LLM 응답에 중복된 article_id가 있습니다."
        )

    if set(returned_ids) != expected_ids:
        missing = (
            expected_ids
            - set(returned_ids)
        )

        unexpected = (
            set(returned_ids)
            - expected_ids
        )

        raise ValueError(
            "LLM 응답의 article_id가 입력과 일치하지 않습니다. "
            f"missing={missing}, "
            f"unexpected={unexpected}"
        )


def classify_batch(
    client,
    articles
):
    payload = build_batch_payload(
        articles
    )

    user_prompt = (
        "다음 기술블로그 게시글을 각각 분류하세요.\n\n"
        + json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    )

    message = (
        client.messages.parse(
            model=MODEL_NAME,
            max_tokens=3000,
            thinking={
                "type": "disabled"
            },
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        user_prompt
                    ),
                }
            ],
            output_format=(
                ClassificationBatch
            ),
        )
    )

    parsed = (
        message.parsed_output
    )

    validate_batch_result(
        articles,
        parsed.results
    )

    return parsed.results


def should_include_for_area(
    category,
    relevance
):
    return (
        category
        in AREA_CATEGORIES
        and relevance
        in {
            "HIGH",
            "MEDIUM"
        }
    )


def create_result(
    article,
    classification
):
    include_for_area = (
        should_include_for_area(
            classification.category,
            classification.technical_relevance
        )
    )

    return {
        "article_id": (
            article[
                "article_id"
            ]
        ),
        "company": (
            article[
                "company"
            ]
        ),
        "title": normalize_text(
            article[
                "title"
            ]
        ),
        "published_at": (
            article[
                "published_at"
            ]
        ),
        "url": (
            article[
                "url"
            ]
        ),
        "content_hash": (
            article[
                "content_hash"
            ]
        ),
        "category": (
            classification.category
        ),
        "technical_relevance": (
            classification
            .technical_relevance
        ),
        "include_for_area": (
            include_for_area
        ),
        "reason": (
            classification.reason
        ),
        "classifier_version": (
            CLASSIFIER_VERSION
        ),
        "model": MODEL_NAME,
    }


def save_current_results(
    articles,
    results_by_id
):
    ordered_results = []

    for article in articles:
        article_id = article[
            "article_id"
        ]

        if article_id in results_by_id:
            ordered_results.append(
                results_by_id[
                    article_id
                ]
            )

    save_json(
        OUTPUT_FILE,
        ordered_results
    )


def main():
    if not os.getenv(
        "ANTHROPIC_API_KEY"
    ):
        raise RuntimeError(
            "ANTHROPIC_API_KEY가 "
            "환경변수에 설정되어 있지 않습니다."
        )

    articles = load_json(
        INPUT_FILE
    )

    if not articles:
        raise ValueError(
            "분류할 게시글이 없습니다."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cache = load_cache()

    client = Anthropic()

    results_by_id = {}

    pending = []

    cache_count = 0

    print()
    print("=" * 60)
    print("RELEVANCE CLASSIFICATION 시작")
    print("=" * 60)

    print(
        "게시글:",
        len(articles)
    )

    print(
        "batch size:",
        BATCH_SIZE
    )

    for article in articles:
        cache_key = (
            article[
                "article_id"
            ],
            article[
                "content_hash"
            ]
        )

        cached = cache.get(
            cache_key
        )

        if cached:
            results_by_id[
                article[
                    "article_id"
                ]
            ] = cached

            cache_count += 1

        else:
            pending.append(
                article
            )

    print(
        "cache 재사용:",
        cache_count
    )

    print(
        "새로 분류:",
        len(pending)
    )

    total_batches = (
        (
            len(pending)
            + BATCH_SIZE
            - 1
        )
        // BATCH_SIZE
    )

    for start in range(
        0,
        len(pending),
        BATCH_SIZE
    ):
        batch = pending[
            start:
            start + BATCH_SIZE
        ]

        batch_number = (
            start
            // BATCH_SIZE
            + 1
        )

        print()
        print(
            f"[batch "
            f"{batch_number}/"
            f"{total_batches}]"
        )

        for article in batch:
            print(
                " -",
                normalize_text(
                    article[
                        "title"
                    ]
                )
            )

        classifications = (
            classify_batch(
                client,
                batch
            )
        )

        classification_by_id = {
            classification.article_id:
            classification
            for classification
            in classifications
        }

        for article in batch:
            classification = (
                classification_by_id[
                    article[
                        "article_id"
                    ]
                ]
            )

            result = create_result(
                article,
                classification
            )

            results_by_id[
                article[
                    "article_id"
                ]
            ] = result

            area_mark = (
                "AREA"
                if result[
                    "include_for_area"
                ]
                else "제외"
            )

            print(
                "   →",
                classification.category,
                "/",
                classification
                .technical_relevance,
                "/",
                area_mark
            )

        # 중간에 프로그램이 중단되어도
        # 이미 분류한 결과는 다시 호출하지 않도록
        # batch마다 저장한다.
        save_current_results(
            articles,
            results_by_id
        )

    final_results = []

    for article in articles:
        final_results.append(
            results_by_id[
                article[
                    "article_id"
                ]
            ]
        )

    category_counts = Counter(
        result[
            "category"
        ]
        for result
        in final_results
    )

    relevance_counts = Counter(
        result[
            "technical_relevance"
        ]
        for result
        in final_results
    )

    included_count = sum(
        1
        for result
        in final_results
        if result[
            "include_for_area"
        ]
    )

    report = {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "model": MODEL_NAME,
        "classifier_version": (
            CLASSIFIER_VERSION
        ),
        "article_count": (
            len(final_results)
        ),
        "cache_reused": (
            cache_count
        ),
        "api_classified": (
            len(pending)
        ),
        "batch_size": (
            BATCH_SIZE
        ),
        "api_call_count": (
            total_batches
        ),
        "category_counts": dict(
            category_counts
        ),
        "relevance_counts": dict(
            relevance_counts
        ),
        "included_for_area": (
            included_count
        ),
        "excluded_from_area": (
            len(final_results)
            - included_count
        ),
    }

    save_json(
        OUTPUT_FILE,
        final_results
    )

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("RELEVANCE CLASSIFICATION 완료")
    print("=" * 60)

    print(
        "전체:",
        len(final_results)
    )

    print(
        "Area 사용:",
        included_count
    )

    print(
        "Area 제외:",
        len(final_results)
        - included_count
    )

    print()
    print(
        "category:",
        dict(category_counts)
    )

    print(
        "technical relevance:",
        dict(relevance_counts)
    )

    print()
    print(
        "API 호출:",
        total_batches
    )

    print(
        "결과:",
        OUTPUT_FILE
    )

    print(
        "리포트:",
        REPORT_FILE
    )


if __name__ == "__main__":
    main()
    