# 설치

저장소 루트에서 파이프라인 가상환경을 활성화한 뒤 실행합니다.

```bash
source pipeline/.venv/bin/activate
python -m pip install -r pipeline/experiments/job_postings_crawler/requirements.txt
```

카카오는 Playwright로 페이지를 연 뒤 공개 API만 호출합니다. Chromium이 필요합니다.

```bash
python -m playwright install chromium
```

재수집·집계 명령은 `pipeline/experiments/job_postings_crawler`에서 실행합니다.

```bash
cd pipeline/experiments/job_postings_crawler
```

## 패키지

| 패키지 | 용도 |
|---|---|
| `requests` | 대부분의 HTTP |
| `beautifulsoup4` | `__NEXT_DATA__` · HTML |
| `playwright` | 카카오 |

표준 라이브러리만 쓰는 모듈은 `common/job_classifier.py`, `common/store.py`입니다.

## 요청 규칙

`common/http_utils.py` 기본값입니다.

- User-Agent: `BeforeJoinCrawler/1.0 (Wanted AI Hackathon project)` (ASCII만)
- 요청 사이 대기: 1초
- robots가 막는 경로(`/apply`, `/o/*/apply`, `/api` on ninehire.site 등)는 요청하지 않습니다
