"""engineering_focus 추출을 API 대신 claude.ai 등 채팅 UI에서 수동으로
돌릴 수 있도록, 회사별(큰 회사는 여러 조각으로) 프롬프트 텍스트 파일을
만든다. API 키/크레딧을 쓰지 않는다.

각 파일은 시스템 프롬프트 + 작업 지시 + 데이터가 전부 한 파일 안에
들어있어서, 파일 내용을 그대로 복사해 새 대화에 붙여넣기만 하면 된다.
"""

import json
import math

from pathlib import Path

import sys

SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

from extract_engineering_focus import (  # noqa: E402
    SYSTEM_PROMPT,
    build_payload,
    load_target_articles
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
    / "manual_prompts"
)

FOCUS_DIR = (
    OUTPUT_DIR
    / "focus"
)

MANIFEST_FILE = (
    OUTPUT_DIR
    / "focus_manifest.json"
)

PILOT_COMPANIES = {
    "CJ올리브영",
    "NHN Cloud",
    "kt cloud",
    "라인플러스",
    "컬리"
}

MAX_ARTICLES_PER_FILE = 80


def safe_filename(name):
    return (
        name
        .replace("/", "_")
        .replace(" ", "_")
    )


def build_prompt_text(
    company,
    part_index,
    part_count,
    articles
):
    payload = build_payload(
        articles
    )

    header_lines = [
        (
            "아래는 기술블로그 게시글에서 "
            "engineering_focus를 뽑는 작업입니다."
        ),
        (
            f"회사: {company} "
            f"(조각 {part_index}/{part_count}, "
            f"이번 조각 {len(articles)}건)"
        ),
        "",
        (
            "지시사항: 아래 SYSTEM 규칙을 따라 "
            "DATA의 각 게시글마다 engineering_focus를 "
            "작성하세요."
        ),
        (
            "출력은 다른 설명 없이 JSON 배열 하나만 "
            "출력하세요. 코드블록(```) 없이, 다음 형식 "
            "그대로:"
        ),
        (
            '[{"article_id": "...", '
            '"engineering_focus": "..."}, ...]'
        ),
        (
            "DATA에 있는 article_id를 빠짐없이, "
            "정확히 한 번씩만 포함하세요."
        ),
        "",
        "=== SYSTEM ===",
        SYSTEM_PROMPT.strip(),
        "",
        "=== DATA ===",
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    ]

    return "\n".join(
        header_lines
    )


def main():
    target_articles, _ = (
        load_target_articles()
    )

    remaining = [
        article
        for article in target_articles
        if article["company"]
        not in PILOT_COMPANIES
    ]

    by_company = {}

    for article in remaining:
        by_company.setdefault(
            article["company"],
            []
        ).append(
            article
        )

    FOCUS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    manifest = []

    for company in sorted(
        by_company.keys()
    ):
        articles = by_company[
            company
        ]

        part_count = max(
            1,
            math.ceil(
                len(articles)
                / MAX_ARTICLES_PER_FILE
            )
        )

        chunk_size = math.ceil(
            len(articles)
            / part_count
        )

        safe_company = safe_filename(
            company
        )

        for part_index in range(
            1,
            part_count + 1
        ):
            start = (
                (part_index - 1)
                * chunk_size
            )

            chunk = articles[
                start:
                start + chunk_size
            ]

            if not chunk:
                continue

            text = build_prompt_text(
                company,
                part_index,
                part_count,
                chunk
            )

            filename = (
                f"{safe_company}"
                f"__part{part_index}"
                f"of{part_count}.txt"
            )

            file_path = (
                FOCUS_DIR
                / filename
            )

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(text)

            manifest.append(
                {
                    "company": company,
                    "part_index": part_index,
                    "part_count": part_count,
                    "article_count": len(
                        chunk
                    ),
                    "article_ids": [
                        a["article_id"]
                        for a in chunk
                    ],
                    "prompt_file": str(
                        file_path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "expected_response_file": (
                        f"focus_responses/"
                        f"{safe_company}"
                        f"__part{part_index}"
                        f"of{part_count}.json"
                    )
                }
            )

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            manifest,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("MANUAL FOCUS PROMPT 생성 완료")
    print("=" * 60)

    print(
        "회사 수:",
        len(by_company)
    )

    print(
        "생성된 파일 수:",
        len(manifest)
    )

    print(
        "총 게시글 수:",
        sum(
            m["article_count"]
            for m in manifest
        )
    )

    print(
        "저장 위치:",
        FOCUS_DIR
    )

    print(
        "매니페스트:",
        MANIFEST_FILE
    )


if __name__ == "__main__":
    main()
