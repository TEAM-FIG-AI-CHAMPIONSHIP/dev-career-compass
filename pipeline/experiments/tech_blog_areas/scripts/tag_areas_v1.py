import json
import os
from pathlib import Path
from typing import List

from anthropic import Anthropic
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[4]

EVIDENCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "area_evidence_final.json"
)

FOCUS_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "engineering_focus"
    / "articles.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "area_tags.json"
)


MODEL_NAME = "claude-sonnet-5"

TAGS_PER_AREA_MIN = 5
TAGS_PER_AREA_MAX = 8


SYSTEM_PROMPT = """
당신은 기술블로그 게시글 묶음(Area)에서 대표 키워드 태그를 뽑는
분석기입니다.

각 Area마다 그 Area에 속한 게시글들의 engineering_focus에
실제로 등장하는 구체적인 기술/기법/프로토콜/도구 이름을
5~8개의 짧은 키워드 태그로 뽑으세요.

규칙:

1. 태그는 반드시 제공된 텍스트에 실제로 등장하는 표현이어야 합니다.
   텍스트에 없는 단어를 만들어내지 마세요.

2. "AI", "백엔드", "최적화"처럼 지나치게 일반적인 단어는
   태그로 뽑지 마세요. 구체적인 기술/시스템/기법 이름을 우선하세요.
   예: Redis, SSE, Kafka, RAG, LLMOps, ArchUnit, KEDA, Flutter,
   Vite, ELECTRA, Item2Vec, Lettuce

3. 여러 게시글에 걸쳐 반복되는 태그를 우선하되, 한 게시글에만
   등장해도 그 Area를 대표할 만큼 핵심적이면 포함할 수 있습니다.

4. 태그 개수는 5개 이상 8개 이하로 하세요.

5. 각 태그마다 그 태그가 왜 이 Area를 대표하는지 한 줄 근거를
   작성하세요.
"""


class AreaTagItem(BaseModel):
    tag: str
    rationale: str


class AreaTags(BaseModel):
    area_name: str
    tags: List[AreaTagItem]


class AreaTagBatch(BaseModel):
    areas: List[AreaTags]


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


def load_focus_by_id():
    focus_articles = load_json(
        FOCUS_FILE
    )

    return {
        article["article_id"]: article[
            "engineering_focus"
        ]
        for article in focus_articles
    }


def build_area_payload(
    evidence,
    focus_by_id
):
    payload = []

    for area in evidence:
        if (
            area["area_name"]
            == "unassigned"
        ):
            continue

        members = []

        for article in area[
            "articles"
        ]:
            members.append(
                {
                    "title": (
                        article["title"]
                    ),
                    "engineering_focus": (
                        focus_by_id.get(
                            article[
                                "article_id"
                            ],
                            ""
                        )
                    )
                }
            )

        payload.append(
            {
                "area_name": (
                    area["area_name"]
                ),
                "members": members
            }
        )

    return payload


def validate_result(
    result,
    payload
):
    expected_names = {
        area["area_name"]
        for area in payload
    }

    returned_names = [
        area.area_name
        for area in result.areas
    ]

    if len(
        returned_names
    ) != len(
        set(returned_names)
    ):
        raise ValueError(
            "동일 area_name이 중복 반환되었습니다."
        )

    if set(
        returned_names
    ) != expected_names:
        raise ValueError(
            "반환된 area_name이 입력과 일치하지 않습니다: "
            f"expected={sorted(expected_names)} "
            f"got={sorted(returned_names)}"
        )

    for area in result.areas:
        if not (
            TAGS_PER_AREA_MIN
            <= len(area.tags)
            <= TAGS_PER_AREA_MAX
        ):
            raise ValueError(
                f"'{area.area_name}' 태그 개수가 "
                f"{TAGS_PER_AREA_MIN}~{TAGS_PER_AREA_MAX}"
                f" 범위를 벗어났습니다: {len(area.tags)}"
            )


def extract_tags(
    client,
    payload
):
    message = client.messages.parse(
        model=MODEL_NAME,
        max_tokens=4000,
        thinking={
            "type": "disabled"
        },
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "다음 Area들에 대해 대표 키워드 태그를 "
                    "뽑으세요.\n\n"
                    + json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2
                    )
                )
            }
        ],
        output_format=AreaTagBatch
    )

    result = (
        message
        .parsed_output
    )

    validate_result(
        result,
        payload
    )

    return result


def ground_tags(
    result,
    payload
):
    members_by_area = {
        area["area_name"]: area[
            "members"
        ]
        for area in payload
    }

    grounded = []

    for area in result.areas:
        members = members_by_area[
            area.area_name
        ]

        haystacks = [
            (
                member["title"]
                + " "
                + member[
                    "engineering_focus"
                ]
            ).lower()
            for member in members
        ]

        tag_entries = []

        for tag_item in area.tags:
            tag_lower = (
                tag_item.tag.lower()
            )

            matched_titles = [
                members[i]["title"]
                for i, haystack in enumerate(
                    haystacks
                )
                if tag_lower in haystack
            ]

            tag_entries.append(
                {
                    "tag": tag_item.tag,
                    "rationale": (
                        tag_item.rationale
                    ),
                    "matched_article_count": len(
                        matched_titles
                    ),
                    "matched_titles": (
                        matched_titles
                    ),
                    "grounded": len(
                        matched_titles
                    )
                    > 0
                }
            )

        ungrounded_count = sum(
            1
            for entry in tag_entries
            if not entry["grounded"]
        )

        grounded.append(
            {
                "area_name": (
                    area.area_name
                ),
                "tags": tag_entries,
                "ungrounded_tag_count": (
                    ungrounded_count
                )
            }
        )

    return grounded


def print_report(grounded):
    print()
    print("=" * 60)
    print("AREA 대표 키워드 태그")
    print("=" * 60)

    for area in grounded:
        print()
        print(
            f"[{area['area_name']}]"
        )

        for tag in area["tags"]:
            marker = (
                ""
                if tag["grounded"]
                else "  !! UNGROUNDED"
            )

            print(
                f"  - {tag['tag']}"
                f" ({tag['matched_article_count']}건)"
                f"{marker}"
            )

            print(
                "     ",
                tag["rationale"]
            )

        if area["ungrounded_tag_count"] > 0:
            print(
                "  경고: 텍스트에서 확인 안 되는 태그",
                area["ungrounded_tag_count"],
                "개"
            )


def main():
    if not os.getenv(
        "ANTHROPIC_API_KEY"
    ):
        raise RuntimeError(
            "ANTHROPIC_API_KEY가 설정되어 있지 않습니다."
        )

    evidence = load_json(
        EVIDENCE_FILE
    )

    focus_by_id = load_focus_by_id()

    payload = build_area_payload(
        evidence,
        focus_by_id
    )

    client = Anthropic()

    print()
    print("=" * 60)
    print("AREA 키워드 태그 추출 시작")
    print("=" * 60)

    print(
        "Area 수:",
        len(payload)
    )

    result = extract_tags(
        client,
        payload
    )

    grounded = ground_tags(
        result,
        payload
    )

    save_json(
        OUTPUT_FILE,
        {
            "model": MODEL_NAME,
            "areas": grounded
        }
    )

    print_report(
        grounded
    )

    print()
    print("=" * 60)
    print("완료")
    print("=" * 60)

    print(
        "저장:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
