# 기술블로그 34개 회사 데이터 수집 명세 (4인 분배용)

## 전체 파이프라인에서 지금 어디에 있는가

이번 작업(4인 분배)이 전체 과정 중 정확히 어디까지인지 먼저 짚는다.
아래에서 자기 팀이 맡은 범위가 어디부터 어디까지인지 확인하고 시작할 것.

```
1단계 (완료) 111개 회사 저비용 전수조사 (census)
             RSS/sitemap 존재 여부 + 직무당 글 8개 이상인지만 확인
             → 통과 34곳 확정 (selected_companies.json)
             ── 이 단계는 이미 끝났고, 다시 안 함 ──

2단계 (지금, 4인 분배)  ★ 이 명세가 다루는 범위 ★
             확정된 34개 회사 각각을 본격적으로:
               a. 12개월치 수집 (RSS/sitemap, 필요시 archive fallback)
               b. 기술글 여부·직무 분류 (규칙 기반, LLM 아님)
               c. engineering_focus(키워드) 추출 (LLM 필요 — claude.ai 수동 또는 API)
             결과물: 회사별 "기술글 + 직무 + engineering_focus 한 문장" 세트

3단계 (다음, 아직 시작 안 함)
             회사별로 engineering_focus를 임베딩 → 클러스터링
             (로컬 모델, LLM 아님, 코드로 자동)

4단계 (다음, 아직 시작 안 함)
             raw cluster를 LLM이 최종 Area 3~5개로 병합·명명
             + 글을 Area에 재배정(코드, 결정론적) + Area별 키워드 태깅(LLM)

5단계 (다음, 아직 시작 안 함)
             최종 노출 게이트 판정 (직무 관련 글 8개+, 반복 Area 3개+,
             Area당 근거 2개+) → 서비스에 노출할 회사×직무 확정

6단계 (다음, 아직 시작 안 함)
             뉴스·채용공고를 확정된 Area에 매칭
```

**헷갈리기 쉬운 포인트**: 2단계의 "직무 분류"는 1단계 census의 직무 게이트와
비슷해 보이지만, 1단계는 "일단 통과 여부만" 보는 거였고 2단계는 실제로
쓸 데이터(글 하나하나의 engineering_focus까지)를 만드는 단계다. 또한
2단계-c(키워드/engineering_focus)와 4단계(Area 명명·키워드 태깅)는 둘 다
"키워드"라는 말이 들어가지만 다른 거다 — 2단계-c는 **글 한 개당** 한 문장
요약이고, 4단계는 **Area(3~5개) 하나당** 대표 키워드 태그다.

## 0. 지금 로직을 그대로 쓰면 안 되는 이유

27개 회사를 검증해보니 두 가지 실제 버그/한계가 나왔다.

1. **sitemap lastmod를 무조건 신뢰하는 문제 (확인됨)**: 일부 사이트는
   sitemap의 `<lastmod>`가 실제 게시일이 아니라 "sitemap 생성 시각"이라
   전체 URL이 똑같은 날짜로 찍혀 있다. 삼성반도체는 383건 전부
   `2026-09-12`(수집 당일)로 찍혀 있었다 — 원본 sitemap.xml을 직접
   확인해보니 (`semiconductor.samsung.com/sitemap.xml`) 실제로 그
   도메인의 모든 URL이 그날 lastmod로 나온다. 우리 코드 버그는
   아니지만, lastmod를 검증 없이 그대로 믿고 있어서 이런 날짜가
   "진짜 게시일"인 것처럼 들어가 있었다.
2. **12개월 도달 여부를 아무도 확인 안 함**: 지금 게이트는 "기술글이
   직무당 8개 이상 있는가"만 보고, 그 8개가 실제로 12개월에 걸쳐 있는지는
   안 본다. 검증해보니 27개 중 10개 회사가 사실상 최근 1~2개월치 데이터로만
   게이트를 통과한 상태였다 (RSS/sitemap이 그 이상 못 감).

그래서 아래 명세는 기존 로직에 **두 가지를 반드시 추가**한다. 이 두 가지는
회사별 예외 처리가 아니라 전부에 동일하게 적용하는 일반 규칙이다.

---

## 1. 목표

34개 회사(추후 확장 가능) 각각에 대해:
- 최근 12개월 기술 블로그 글의 URL·제목·게시일·본문을 확보한다. (수집 — LLM 아님)
- 기술글 여부와 직무(백엔드/프론트엔드/모바일/데이터·AI)를 규칙 기반으로 분류한다. (분류 — LLM 아님)
- 기술글로 분류된 글마다 engineering_focus(핵심 엔지니어링 문제·해결 방식
  한 문장)를 뽑는다. (이 부분만 LLM 필요)

**수집·분류는 전부 Python 코드**(requests/feedparser/trafilatura/정규식)로
한다. **engineering_focus만 LLM이 필요**하고, API 크레딧 대신 claude.ai
수동 프롬프팅으로 할 수도 있다 (2단계-c, 8번 참고).

이 4인 작업이 끝나면 나오는 결과물은 "회사별로 기술글 + 직무 + 한 줄
engineering_focus가 붙은 목록"까지다. **Area를 만들거나 이름 짓는 건
이번 작업 범위가 아니다** (전체 흐름 3~4단계, 다음에 진행).

## 2. 4인 분배 방법

34개 회사를 8~9개씩 4묶음으로 나눠 각자 독립적으로 진행한다. 회사 목록은
`data/research/tech_blog_company_role_census/selected_companies.json`을
기준으로 나누면 된다. 겹치지만 않으면 어떻게 나누든 상관없다.

## 3. 파이프라인 (기존 순서 + 수정사항 반영)

```
1. collect.py           RSS/Atom 우선 수집
2. collect_round2.py    RSS로 부족하면 sitemap. 목록/태그/페이지네이션
                        URL은 url_filters.py로 제외
3. [신규] 날짜 재확인    lastmod가 없어서 fallback 날짜가 들어간 글만,
                        상세 페이지에서 실제 날짜를 다시 확인
                        (아래 3-1 참고)
4. backfill_titles.py   빈 제목을 og:title 등에서 채움
5. extract.py           본문 추출 (trafilatura)
6. classify_and_gate.py 기술글 여부·직무 매핑·1차 게이트 집계
7. [신규] 커버리지 검증  회사별로 "가장 오래된 글이 12개월 선에
                        얼마나 가까운지" 기록 (아래 3-2 참고)
8. [신규] engineering_focus 추출   기술글로 분류된 것만 대상.
                        LLM 필요 — 아래 3-3 참고
```

### 3-1. 날짜 재확인 (의심스러운 lastmod 재검증)

**"의심스러운 날짜"의 정의** (회사별 분기 없이 전부 동일 규칙):
같은 회사 안에서 동일한 published_at 날짜를 가진 글이 비정상적으로
많으면(예: 5건 이상 동일 날짜) sitemap lastmod를 못 믿는 것으로 본다.
lastmod가 아예 없는 경우도 당연히 포함.

의심스러운 글만, 그 글의 실제 URL에 다시 접속해서 아래 순서로 진짜
게시일을 찾는다.

```
JSON-LD article.datePublished
  -> og:article:published_time 메타 태그 (census round2의 fetch_title_date가
     이미 이 패턴을 검사하지만, "lastmod 있음" 케이스는 건너뛰던 걸
     "의심스러우면 lastmod 있어도 재검증"으로 넓히는 것)
  -> <time datetime="..."> 태그
  -> 그래도 없으면 published_at = null (미상으로 남김, sitemap lastmod로
     되돌리지 않는다)
```

날짜가 끝내 null인 글은 "날짜 미상"으로 표시하고, 12개월 게이트 집계에서는
빼거나 별도 각주로 남긴다.

실행: `check_coverage.py`(3-2)를 먼저 돌리면 "의심 날짜" 회사·건수를
같이 알려준다. 의심 표시된 회사만 `repair_dates.py`를 돌린다.

(참고: 제목이 빈 경우를 고치는 같은 구조의 스크립트가
`pipeline/experiments/tech_blog_engineering_focus_29/scripts/repair_titles.py`에
이미 있다. `repair_dates.py`는 그 파일의 날짜 버전이다.)

### 3-2. 커버리지 검증 (12개월 도달 여부 기록)

회사 처리를 "완료"로 표시하기 전에 반드시 계산해서 기록한다.

```
gap_days = (오늘 - 12개월) - 그 회사에서 수집된 글 중 가장 오래된 published_at
```

- `gap_days <= 30`: 정상 (그 근처에 원래 글이 없었을 가능성이 높음)
- `30 < gap_days <= 180`: 부분 커버리지 — 회사 옆에 표시해두고 그대로 진행
- `gap_days > 180`: 심각한 부분 커버리지 — RSS/sitemap만으로는 12개월에
  크게 못 미친다는 뜻. 이 경우 archive/pagination fallback을 한 번
  시도해본다 (아래 참고). 그래도 안 되면 "최근 N개월 스냅샷"이라고
  명시하고 넘어간다. 억지로 채우지 않는다.

필요하면 `pipeline/experiments/tech_blog_areas/scripts/archive_collector.py`에
이미 만들어둔 generic 목록 페이지네이션 수집기를 재사용할 수 있다
(RSS/sitemap이 부족할 때만 시도, 태그/페이지 URL은 자동 제외, 회사별
분기 없음).

### 3-3. engineering_focus 추출 (LLM 필요, 회사·직무 분류와는 별개 단계)

기술글로 분류된(`is_tech: true`) 글마다 "이 글이 실제로 다루는 핵심
엔지니어링 문제와 접근 방식"을 한 문장으로 뽑는다. 이건 4단계의
"Area별 대표 키워드 태깅"과 다른 것이다 — **여기서는 글 1개당 1문장**이고,
Area 키워드 태깅은 나중에 Area(3~5개) 하나당 여러 개 키워드를 뽑는 거다.

두 가지 방법 중 택 1 (팀 안에서 통일하지 않아도 됨, 사람별로 달라도 무방):

**(A) API로 직접**: `pipeline/experiments/tech_blog_engineering_focus_29/scripts/extract_engineering_focus.py`를
복사해서 `--companies` 인자에 자기 몫 회사만 넣고 실행. API 크레딧 소모됨.

**(B) claude.ai 수동 프롬프팅**: 같은 폴더의
`export_manual_focus_prompts.py`를 참고해서 자기 몫 회사용 프롬프트
파일을 만들고, claude.ai에 복붙해서 결과(JSON)를 받는 방식. 크레딧
안 씀, 대신 사람이 직접 복붙해야 함. (필요하면 내가 각자 몫으로 파일
생성해줄 수 있음)

어느 쪽이든 출력 스키마는 동일해야 한다: `{"article_id": "...", "engineering_focus": "..."}`

## 4. 완료 기준 (회사 1곳당)

- [ ] 최근 12개월 기술글 URL·제목·게시일·본문 확보 시도 완료
- [ ] 날짜가 fallback(가짜) 값이 아님을 확인 (3-1 적용)
- [ ] gap_days 계산해서 기록함 (3-2)
- [ ] 기술글 여부·직무 분류 완료 (`classify_and_gate.py` 그대로 사용)
- [ ] 직무당 8개 이상인지, 통과 직무가 1개 이상인지 판정 (`pass`/`fail`/`unknown`)
- [ ] 기술글로 분류된 글마다 engineering_focus 한 문장 확보 (3-3)
- [ ] 본문 원문은 `data/work/`에만 두고 커밋하지 않음

## 5. 산출물

각자 맡은 회사들에 대해 아래 형식으로 공유한다 (기존 census 산출물과 동일한 스키마).

```json
{
  "company": "회사명",
  "collected_count": 0,
  "tech_count": 0,
  "roles": {"backend": 0, "frontend": 0, "mobile": 0, "data-ai": 0},
  "gate": "pass|fail|unknown",
  "coverage": {
    "oldest_published_at": "YYYY-MM-DD 또는 null",
    "gap_days": 0,
    "status": "정상|부분|심각부분",
    "note": "필요하면 한 줄 설명"
  },
  "date_repair": {
    "fallback_dates_found": 0,
    "repaired": 0,
    "still_unknown": 0
  },
  "engineering_focus_count": 0
}
```

(engineering_focus 원문 한 문장씩은 이 요약 파일이 아니라 글 단위
목록 파일 — `article_id`, `title`, `engineering_focus` — 에 따로
저장한다. `data/work/`에 두고 커밋하지 않는다.)

## 6. 하지 말 것 (기존 컨벤션 유지)

- 회사 이름으로 분기하는 코드 추가 금지 (`if company == "X"` 형태)
- 60~80개(또는 34개)를 맞추려고 게이트 기준을 낮추지 않기
- `unknown`을 `fail`로 취급하지 않기
- engineering_focus까지만 하고, Area 생성(embedding/clustering/Area 병합·명명/
  Area별 키워드 태깅)은 이번 작업 범위 밖 — 전체 흐름 3~4단계, 다음에 진행
- 원문 전체를 Git에 커밋하지 않기
