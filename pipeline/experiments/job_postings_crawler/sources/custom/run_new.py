"""선정 표에서 아직 모듈이 없던 회사만 수집한다.

배민(우아한형제들)·어피닛·넥스트리는 채용 사이트가 없거나 목록이 차단되어 제외.
그리팅·리크루터·기존 자체구축은 각 run.py를 쓴다.
"""

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from common.paths import LOG_DIR  # noqa: E402
from sources.ninehire.crawler import NINEHIRE_COMPANIES, crawl_company  # noqa: E402

from sources.custom import (  # noqa: E402
    gabia,
    goorm,
    imweb,
    inflab,
    ktcloud,
    lgresearch,
    nds,
    nhncloud,
    samsung,
    samsungds,
)

CUSTOM = [
    lgresearch,
    nhncloud,
    ktcloud,
    gabia,
    goorm,
    nds,
    samsung,
    samsungds,
    imweb,
    inflab,
]


def run_one(label, fn):
    print(f"  수집 중: {label} ...", flush=True)
    try:
        return fn()
    except Exception as exc:
        traceback.print_exc()
        return {"company_id": label, "company_name": label, "error": str(exc), "url": ""}


def main():
    results = []
    for module in CUSTOM:
        results.append(run_one(module.COMPANY_ID, module.crawl))

    meta = NINEHIRE_COMPANIES["rapportlabs"]
    results.append(
        run_one(
            "rapportlabs",
            lambda: crawl_company(
                "rapportlabs",
                meta["name"],
                meta["base_url"],
                mode=meta["mode"],
                company_uuid=meta.get("company_uuid"),
            ),
        )
    )

    print()
    print("=" * 96)
    print("[신규 채용 사이트 수집]")
    print("=" * 96)
    print(f"{'company_id':<16}{'회사명':<22}{'raw':>6}{'deploy=T':>10}{'분류됨':>8}")
    print("-" * 96)
    errors = []
    for row in results:
        if "error" in row:
            errors.append(row)
            print(f"{row['company_id']:<16}{row.get('company_name', ''):<22}  ❌ {row['error'][:50]}")
            continue
        print(
            f"{row['company_id']:<16}{row.get('company_name', ''):<22}"
            f"{row.get('raw_count', 0):>6}{row.get('deploy_true', 0):>10}"
            f"{row.get('classified_active', 0):>8}"
        )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "selected33_new_crawl.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    if errors:
        print()
        print("[실패]", len(errors), "곳 — 나머지 raw는 저장됨")
        for row in errors:
            print(f"  {row['company_id']}: {row['error']}")


if __name__ == "__main__":
    main()
