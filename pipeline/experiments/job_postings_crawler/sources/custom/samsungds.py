"""삼성반도체 — samsungcareers.com 목록 중 DS부문.

dsrecruit.com은 직무 소개 사이트라 공고 목록이 없다. 지원 CTA가
삼성커리어스로 향하므로 같은 `list.data`에서 회사명이 DS부문인 행만 저장한다.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sources.custom.samsung import crawl as crawl_samsung

COMPANY_ID = "samsungds"
COMPANY_NAME = "삼성반도체"


def crawl():
    return crawl_samsung(company_id=COMPANY_ID, company_name=COMPANY_NAME, ds_only=True)


if __name__ == "__main__":
    print(json.dumps(crawl(), ensure_ascii=False, indent=2))
