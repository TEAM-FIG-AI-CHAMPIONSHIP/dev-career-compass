# Tech Blog Source Coverage

우아한형제들에서 검증한 generic collector(RSS 우선 → sitemap fallback)가
다른 기술블로그에서도 최근 12개월 글을 모을 수 있는지 확인하는 실험입니다.

Area, embedding, clustering, LLM은 다루지 않습니다.
`pipeline/experiments/tech_blog_areas/`는 수정하지 않습니다.

## 대상 회사

- 올리브영 (`https://oliveyoung.tech/`)
- 네이버 D2 (`https://d2.naver.com/`)
- 토스 (`https://toss.tech/`)
- 당근 (`https://medium.com/daangn`)

우아한형제들은 제외합니다.

## 수집기

팀원 `tech_blog_areas`의 `probe_sources.py`, `collect.py`, `extract.py`를
이 디렉터리로 복사하고 입출력 경로만 바꿨습니다.

한 가지 generic 가드만 추가했습니다. sitemap에서 모은 URL이
`blog_url` 접두어 밖이면 버립니다. Medium처럼 호스트 단위 sitemap이
나오는 곳에서 사이트 전체를 따라가지 않기 위해서입니다.
회사별 전용 크롤러는 아닙니다.

## 실행

저장소 루트에서 실험 의존성을 설치합니다.

```bash
python3 -m pip install -r pipeline/experiments/tech_blog_source_coverage/requirements.txt
```

```bash
python pipeline/experiments/tech_blog_source_coverage/scripts/probe_sources.py
python pipeline/experiments/tech_blog_source_coverage/scripts/collect.py
python pipeline/experiments/tech_blog_source_coverage/scripts/extract.py
python pipeline/experiments/tech_blog_source_coverage/scripts/summarize.py
```

회사 하나만 돌리려면 `--company "토스"`를 붙입니다.

## 출력

| 경로 | Git | 내용 |
| --- | --- | --- |
| `data/work/tech_blog_source_coverage/` | 제외 | probe, 메타데이터, 본문 |
| `data/research/tech_blog_source_coverage.md` | 커밋 | 회사별 수집 전략과 성공률 |

`content` 원문은 `data/work`에만 두고 커밋하지 않습니다.
