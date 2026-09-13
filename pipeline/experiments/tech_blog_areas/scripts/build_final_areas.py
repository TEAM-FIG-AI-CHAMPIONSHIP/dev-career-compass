import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]

EVIDENCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "area_evidence_final.json"
)

TAGS_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "area_tags.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "work"
    / "tech_blog_areas"
    / "areas_v1"
    / "final_areas.json"
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


def build_keyword_list(tag_area):
    ordered_tags = sorted(
        tag_area["tags"],
        key=lambda tag: tag[
            "matched_article_count"
        ],
        reverse=True
    )

    return [
        tag["tag"]
        for tag in ordered_tags
    ]


def main():
    evidence = load_json(
        EVIDENCE_FILE
    )

    tags_data = load_json(
        TAGS_FILE
    )

    tags_by_area = {
        area["area_name"]: area
        for area in tags_data["areas"]
    }

    final_areas = []

    for area in evidence:
        tag_area = tags_by_area.get(
            area["area_name"]
        )

        keywords = (
            build_keyword_list(
                tag_area
            )
            if tag_area
            else []
        )

        final_areas.append(
            {
                "area_name": (
                    area["area_name"]
                ),
                "area_description": (
                    area.get(
                        "area_description",
                        ""
                    )
                ),
                "article_count": (
                    area["article_count"]
                ),
                "keywords": keywords,
                "evidence": area[
                    "articles"
                ]
            }
        )

    save_json(
        OUTPUT_FILE,
        final_areas
    )

    print()
    print("=" * 60)
    print("FINAL AREAS")
    print("=" * 60)

    for area in final_areas:
        print()
        print(
            f"{area['area_name']}"
            f"  ({area['article_count']}개)"
        )

        print(
            "  keywords:",
            area["keywords"]
        )

    print()
    print("저장:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
