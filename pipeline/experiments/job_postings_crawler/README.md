# Job Postings Crawler

회사별 공개 채용 목록을 모아 스펙 4개 직무(서버·백엔드, 웹 프론트엔드, 모바일, 데이터·AI) 커버리지를 검증하는 실험입니다. LLM으로 분류하지 않습니다.

이전 독립 프로젝트 `job_postings_crawler`를 이 디렉터리로 옮겼습니다. 반복 로직은 이후 `pipeline/src/career_compass_pipeline`으로 옮깁니다.

## 입력과 출력

| 종류 | 위치 | Git |
| --- | --- | --- |
| 수집 원문 | `data/work/job_postings/raw/` | 제외 |
| 분류 결과 | `data/work/job_postings/processed/` | 제외 |
| 로그·probe | `data/work/job_postings/logs/`, `probe/` | 제외 |
| 공유 집계 | `data/research/job_postings/` | 커밋 |

원문 JSON은 커밋하지 않습니다. 로컬에 이미 수집한 24개 회사 결과는 `data/work/job_postings`에 복사해 두었습니다.

## 실행 방법

저장소 루트에서 파이프라인 가상환경을 켠 뒤 이 디렉터리로 이동합니다.

```bash
source pipeline/.venv/bin/activate
python -m pip install -r pipeline/experiments/job_postings_crawler/requirements.txt
python -m playwright install chromium
cd pipeline/experiments/job_postings_crawler
```

재수집과 집계 명령은 `docs/`에 있습니다.

- [설치](docs/install.md)
- [재수집](docs/recrawl.md)
- [집계](docs/aggregation.md)
- [프로젝트 구조](docs/structure.md)

1차 집계표: `data/research/job_postings/step6_summary.md`
