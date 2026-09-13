import html
import json
import os
import re

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from anthropic import Anthropic
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[4]

EXTRACTED_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "extracted"
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "engineering_focus"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "focus_report.json"
)


MODEL_NAME = "claude-sonnet-5"

FOCUS_VERSION = "v2"

BATCH_SIZE = 8

EXCERPT_SECTION_CHARS = 1200


SYSTEM_PROMPT = """
당신은 기업 기술블로그의 엔지니어링 주제를 정규화하는 분석기입니다.

각 게시글에서 '이 글이 실제로 다루는 핵심 엔지니어링 문제와 접근 방식'을
engineering_focus 한 문장으로 작성하세요.

이 결과는 서로 비슷한 엔지니어링 게시글을 의미적으로 그룹화하는 데 사용됩니다.

규칙:

1. 회사명이나 글의 분위기가 아니라 실제 기술 문제를 중심으로 작성하세요.

2. 가능한 경우 다음 두 요소를 포함하세요.
   - 어떤 엔지니어링 문제/목표가 있었는지
   - 어떤 기술적 접근으로 해결하거나 검증했는지

3. 구체적인 기술이나 시스템이 글에 명시되어 있다면 포함하세요.
   예:
   Redis, SSE, RAG, Kafka, RDB Task Queue, React, Kubernetes

4. 다음과 같이 지나치게 일반적인 문장은 금지합니다.
   - 시스템을 개선한 경험
   - 개발 생산성을 높인 경험
   - 기술을 활용해 문제를 해결한 경험

5. 제공된 텍스트에 없는 내용을 추측하지 마세요.

6. 프로젝트명이나 행사명 자체보다 엔지니어링 의미가 드러나도록 작성하세요.

7. 한 문장으로 작성하세요.

8. 기술 영역 이름을 미리 정해서 붙이지 마세요.
   예:
   - "백엔드 영역"
   - "AI 영역"
   - "클라우드 영역"
   같은 사전 정의 taxonomy를 생성하지 마세요.

9. 본문은 앞부분, 중간부분, 뒷부분으로 나뉘어 제공될 수 있습니다.
   앞부분의 문제 설명만 보고 판단하지 말고,
   중간/뒷부분에서 실제로 선택·구현한 해결 방식까지 확인하세요.

10. 제목에서 핵심 기술이나 접근 방식이 명시되어 있다면,
    본문과 모순되지 않는 한 engineering_focus에 반영하세요.
"""


class FocusResult(BaseModel):
    article_id: str
    engineering_focus: str


class FocusBatch(BaseModel):
    results: List[FocusResult]


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

    length = len(content)

    section_size = (
        EXCERPT_SECTION_CHARS
    )

    if length <= (
        section_size * 3
    ):
        return content

    start = content[
        :section_size
    ]

    middle_start = max(
        0,
        (
            length // 2
            - section_size // 2
        )
    )

    middle = content[
        middle_start:
        middle_start + section_size
    ]

    end = content[
        -section_size:
    ]

    return (
        "[본문 앞부분]\n"
        + start
        + "\n\n"
        + "[본문 중간부분]\n"
        + middle
        + "\n\n"
        + "[본문 뒷부분]\n"
        + end
    )


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
        if (
            item.get("article_id")
            and item.get("content_hash")
            and item.get("focus_version")
            == FOCUS_VERSION
        ):
            cache[
                (
                    item["article_id"],
                    item["content_hash"]
                )
            ] = item

    return cache


def build_payload(
    articles
):
    return [
        {
            "article_id": (
                article["article_id"]
            ),
            "title": normalize_text(
                article["title"]
            ),
            "excerpt": create_excerpt(
                article["content"]
            )
        }
        for article in articles
    ]


def validate_results(
    articles,
    results
):
    expected_ids = {
        article["article_id"]
        for article in articles
    }

    returned_ids = [
        result.article_id
        for result in results
    ]

    if len(
        returned_ids
    ) != len(
        set(returned_ids)
    ):
        raise ValueError(
            "중복된 article_id가 반환되었습니다."
        )

    if set(
        returned_ids
    ) != expected_ids:
        raise ValueError(
            "LLM 응답의 article_id가 입력과 일치하지 않습니다."
        )


def extract_focus_batch(
    client,
    articles
):
    payload = build_payload(
        articles
    )

    message = client.messages.parse(
        model=MODEL_NAME,
        max_tokens=2500,
        thinking={
            "type": "disabled"
        },
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "다음 게시글 각각의 "
                    "engineering_focus를 작성하세요.\n\n"
                    + json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2
                    )
                )
            }
        ],
        output_format=FocusBatch
    )

    results = (
        message
        .parsed_output
        .results
    )

    validate_results(
        articles,
        results
    )

    return results


def save_current_results(
    target_articles,
    results_by_id
):
    ordered = []

    for article in target_articles:
        article_id = (
            article["article_id"]
        )

        if article_id in results_by_id:
            ordered.append(
                results_by_id[
                    article_id
                ]
            )

    save_json(
        OUTPUT_FILE,
        ordered
    )


def main():
    if not os.getenv(
        "ANTHROPIC_API_KEY"
    ):
        raise RuntimeError(
            "ANTHROPIC_API_KEY가 설정되어 있지 않습니다."
        )

    extracted = load_json(
        EXTRACTED_FILE
    )

    classified = load_json(
        CLASSIFIED_FILE
    )

    classification_by_id = {
        item["article_id"]: item
        for item in classified
    }

    target_articles = []

    for article in extracted:
        classification = (
            classification_by_id.get(
                article["article_id"]
            )
        )

        if not classification:
            continue

        if not classification.get(
            "include_for_area",
            False
        ):
            continue

        target_articles.append(
            article
        )

    if not target_articles:
        raise ValueError(
            "engineering focus를 추출할 게시글이 없습니다."
        )

    cache = load_cache()

    results_by_id = {}
    pending = []

    cache_count = 0

    for article in target_articles:
        cache_key = (
            article["article_id"],
            article["content_hash"]
        )

        cached = cache.get(
            cache_key
        )

        if cached:
            results_by_id[
                article["article_id"]
            ] = cached

            cache_count += 1
        else:
            pending.append(
                article
            )

    client = Anthropic()

    total_batches = (
        (
            len(pending)
            + BATCH_SIZE
            - 1
        )
        // BATCH_SIZE
    )

    print()
    print("=" * 60)
    print("ENGINEERING FOCUS 추출 시작")
    print("=" * 60)

    print(
        "Area 대상:",
        len(target_articles)
    )

    print(
        "cache 재사용:",
        cache_count
    )

    print(
        "새로 추출:",
        len(pending)
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
            f"[batch {batch_number}/{total_batches}]"
        )

        results = extract_focus_batch(
            client,
            batch
        )

        result_by_id = {
            result.article_id: result
            for result in results
        }

        for article in batch:
            result = result_by_id[
                article["article_id"]
            ]

            focus = normalize_text(
                result.engineering_focus
            )

            item = {
                "article_id": (
                    article["article_id"]
                ),
                "company": (
                    article["company"]
                ),
                "title": normalize_text(
                    article["title"]
                ),
                "published_at": (
                    article["published_at"]
                ),
                "url": (
                    article["url"]
                ),
                "content_hash": (
                    article["content_hash"]
                ),
                "engineering_focus": (
                    focus
                ),
                "focus_version": (
                    FOCUS_VERSION
                ),
                "model": (
                    MODEL_NAME
                )
            }

            results_by_id[
                article["article_id"]
            ] = item

            print(
                " -",
                article["title"]
            )

            print(
                "   →",
                focus
            )

        save_current_results(
            target_articles,
            results_by_id
        )

    final_results = [
        results_by_id[
            article["article_id"]
        ]
        for article
        in target_articles
    ]

    save_json(
        OUTPUT_FILE,
        final_results
    )

    report = {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "model": MODEL_NAME,
        "focus_version": (
            FOCUS_VERSION
        ),
        "article_count": (
            len(final_results)
        ),
        "cache_reused": (
            cache_count
        ),
        "api_extracted": (
            len(pending)
        ),
        "batch_size": (
            BATCH_SIZE
        ),
        "api_call_count": (
            total_batches
        )
    }

    save_json(
        REPORT_FILE,
        report
    )

    print()
    print("=" * 60)
    print("ENGINEERING FOCUS 추출 완료")
    print("=" * 60)

    print(
        "게시글:",
        len(final_results)
    )

    print(
        "API 호출:",
        total_batches
    )

    print(
        "결과:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
    