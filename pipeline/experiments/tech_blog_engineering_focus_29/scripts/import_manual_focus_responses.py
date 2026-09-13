"""claude.ai 등에서 수동으로 프롬프팅해 얻은 engineering_focus 응답을
표준 결과 파일(articles.json)에 병합한다.

사용법:
  1. export_manual_focus_prompts.py / export_manual_focus_extra.py가
     만든 프롬프트 파일(data/work/.../manual_prompts/focus/*.txt)을
     그대로 복사해 claude.ai 새 대화에 붙여넣는다.
  2. 응답으로 나온 JSON 배열([{"article_id": "...",
     "engineering_focus": "..."}, ...])을 파일 하나로 저장한다 —
     manifest의 expected_response_file 경로 그대로:
     data/work/tech_blog_engineering_focus_29/manual_prompts/
       focus_responses/<회사>__partXofY.json
  3. 이 스크립트를 실행하면 저장된 응답 파일들을 찾아서
     검증(article_id 빠짐/중복 없는지) 후 articles.json에 병합한다.

API 경로(extract_engineering_focus.py)와 같은 스키마로 저장하므로
이후 embedding/clustering 단계는 API로 뽑았든 수동으로 뽑았든 구분
없이 그대로 쓸 수 있다.
"""

import json
import sys

from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(SCRIPTS_DIR)
)

from extract_engineering_focus import (  # noqa: E402
    EXCLUDED_FILE,
    FOCUS_VERSION,
    build_exclusion_reason,
    load_target_articles,
    normalize_text
)

from export_manual_focus_extra import (  # noqa: E402
    fetch_daangn_articles,
    load_naver_d2_articles
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_engineering_focus_29"
)

MANUAL_DIR = (
    OUTPUT_DIR
    / "manual_prompts"
)

RESPONSES_DIR = (
    MANUAL_DIR
    / "focus_responses"
)

MANIFEST_FILES = (
    MANUAL_DIR / "focus_manifest.json",
    MANUAL_DIR / "focus_manifest_extra.json"
)

RESULTS_FILE = (
    OUTPUT_DIR
    / "articles.json"
)

MODEL_NAME = "manual/claude.ai"

# 시스템 프롬프트가 이 문구를 강제 지시하지는 않지만, 실제 수동
# 프롬프팅 결과에서 비엔지니어링 글(사내 행사/문화 회고 등)에 대해
# 모델이 자발적으로 이 패턴으로 응답하는 것을 확인했다. 이 표시가
# 붙은 항목은 engineering_focus가 아니라 "추출할 내용 없음"이므로
# 최종 결과에서 제외하고 excluded_articles.json에 별도 기록한다.
NO_CONTENT_MARKERS = (
    "엔지니어링 내용이 없음",
    "기술적 내용 없음"
)


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


def load_manifest_rows():
    rows = []

    for path in MANIFEST_FILES:
        if not path.exists():
            continue

        rows.extend(
            load_json(path)
        )

    return rows


def build_metadata_index():
    """article_id -> {company, title, url, published_at,
    content_hash} 전체 인덱스. 표준 census 경로(load_target_articles)
    와 네이버 D2·당근 Medium RSS(export_manual_focus_extra) 양쪽을
    합친다."""

    index = {}

    standard_articles, _ = (
        load_target_articles()
    )

    for article in standard_articles:
        index[
            article["article_id"]
        ] = {
            "company": article["company"],
            "title": article["title"],
            "url": article["url"],
            "published_at": (
                article["published_at"]
            ),
            "content_hash": (
                article["content_hash"]
            )
        }

    for loader in (
        load_naver_d2_articles,
        fetch_daangn_articles
    ):
        try:
            extra_articles = loader()

        except Exception as error:  # noqa: BLE001
            print(
                f"[경고] {loader.__name__} "
                f"로드 실패, 건너뜀: {error}"
            )

            continue

        for article in extra_articles:
            import hashlib

            content_hash = hashlib.sha256(
                article["content"].encode(
                    "utf-8"
                )
            ).hexdigest()

            index[
                article["article_id"]
            ] = {
                "company": article["company"],
                "title": article["title"],
                "url": article["url"],
                "published_at": (
                    article["published_at"]
                ),
                "content_hash": content_hash
            }

    return index


def main():
    manifest_rows = load_manifest_rows()

    if not manifest_rows:
        print(
            "manifest 파일이 없습니다. "
            "export_manual_focus_prompts.py / "
            "export_manual_focus_extra.py를 먼저 "
            "실행하세요."
        )

        return

    print("메타데이터 인덱스 구성 중...")

    metadata_index = (
        build_metadata_index()
    )

    existing_results = {}

    if RESULTS_FILE.exists():
        for item in load_json(
            RESULTS_FILE
        ):
            existing_results[
                item["article_id"]
            ] = item

    existing_excluded = {}

    if EXCLUDED_FILE.exists():
        for item in load_json(
            EXCLUDED_FILE
        ):
            existing_excluded[
                item["article_id"]
            ] = item

    merged_count = 0
    excluded_count = 0
    skipped_parts = []

    for row in manifest_rows:
        company = row["company"]
        part_label = (
            f"{company} "
            f"part{row['part_index']}"
            f"of{row['part_count']}"
        )

        response_path = (
            MANUAL_DIR
            / row["expected_response_file"]
        )

        if not response_path.exists():
            skipped_parts.append(
                (part_label, "응답 파일 없음")
            )

            continue

        try:
            response = load_json(
                response_path
            )

        except json.JSONDecodeError as error:
            skipped_parts.append(
                (
                    part_label,
                    f"JSON 파싱 실패: {error}"
                )
            )

            continue

        if not isinstance(
            response, list
        ):
            skipped_parts.append(
                (
                    part_label,
                    "응답이 JSON 배열이 아님"
                )
            )

            continue

        response_by_id = {}
        duplicate_ids = set()

        for entry in response:
            article_id = entry.get(
                "article_id"
            )

            if not article_id:
                continue

            if article_id in response_by_id:
                duplicate_ids.add(
                    article_id
                )

            response_by_id[
                article_id
            ] = entry

        expected_ids = set(
            row["article_ids"]
        )

        missing_ids = (
            expected_ids
            - response_by_id.keys()
        )

        extra_ids = (
            response_by_id.keys()
            - expected_ids
        )

        if (
            missing_ids
            or extra_ids
            or duplicate_ids
        ):
            reason_parts = []

            if missing_ids:
                reason_parts.append(
                    f"누락 {len(missing_ids)}건"
                )

            if extra_ids:
                reason_parts.append(
                    f"모르는 id {len(extra_ids)}건"
                )

            if duplicate_ids:
                reason_parts.append(
                    f"중복 {len(duplicate_ids)}건"
                )

            skipped_parts.append(
                (
                    part_label,
                    ", ".join(reason_parts)
                )
            )

            continue

        for article_id, entry in (
            response_by_id.items()
        ):
            meta = metadata_index.get(
                article_id
            )

            if not meta:
                skipped_parts.append(
                    (
                        f"{part_label} "
                        f"({article_id})",
                        "메타데이터 없음 "
                        "(원본 목록에서 사라짐?)"
                    )
                )

                continue

            exclusion_reason = (
                build_exclusion_reason(
                    meta
                )
            )

            if exclusion_reason:
                existing_results.pop(
                    article_id,
                    None
                )

                existing_excluded[
                    article_id
                ] = {
                    "article_id": article_id,
                    "company": meta["company"],
                    "title": normalize_text(
                        meta["title"]
                    ),
                    "url": meta["url"],
                    "reason": exclusion_reason
                }

                excluded_count += 1

                continue

            focus_text = normalize_text(
                entry.get(
                    "engineering_focus",
                    ""
                )
            )

            if any(
                marker in focus_text
                for marker in NO_CONTENT_MARKERS
            ):
                existing_results.pop(
                    article_id,
                    None
                )

                existing_excluded[
                    article_id
                ] = {
                    "article_id": article_id,
                    "company": meta["company"],
                    "title": normalize_text(
                        meta["title"]
                    ),
                    "url": meta["url"],
                    "reason": (
                        "manual_no_"
                        "engineering_content"
                    )
                }

                excluded_count += 1

                continue

            existing_excluded.pop(
                article_id,
                None
            )

            existing_results[
                article_id
            ] = {
                "article_id": article_id,
                "company": meta["company"],
                "title": normalize_text(
                    meta["title"]
                ),
                "published_at": (
                    meta["published_at"]
                ),
                "url": meta["url"],
                "content_hash": (
                    meta["content_hash"]
                ),
                "engineering_focus": (
                    focus_text
                ),
                "focus_version": (
                    FOCUS_VERSION
                ),
                "model": MODEL_NAME
            }

            merged_count += 1

        print(
            f"[병합완료] {part_label} "
            f"({len(response_by_id)}건)"
        )

    save_json(
        RESULTS_FILE,
        list(
            existing_results.values()
        )
    )

    save_json(
        EXCLUDED_FILE,
        list(
            existing_excluded.values()
        )
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    print(
        "이번에 병합:",
        merged_count
    )

    print(
        "이번에 제외 "
        "(추출 가능한 엔지니어링 "
        "내용이 없음):",
        excluded_count
    )

    print(
        "전체 누적(병합):",
        len(existing_results)
    )

    print(
        "전체 누적(제외):",
        len(existing_excluded)
    )

    if skipped_parts:
        print()

        print(
            f"건너뜀 ({len(skipped_parts)}건):"
        )

        for label, reason in skipped_parts:
            print(
                f"  - {label}: {reason}"
            )

    print()

    print(
        "저장:",
        RESULTS_FILE
    )


if __name__ == "__main__":
    main()
