# 웹 파일 구조와 라우팅

`apps/web` 의 구조와 라우팅을 정리합니다. 프론트를 여러 명이 나눠 맡기 전에
화면과 경로를 맞추기 위한 문서입니다.

파이프라인과 데이터 수집 쪽은 이 문서의 범위가 아닙니다. 아래 트리에 함께
그려 둔 것은 웹이 무엇을 읽는지 보여주기 위한 것이며, 그쪽 구조와 산출물은
담당자가 정합니다.

회사 목록은 **기술 블로그·채용 공고 검증 결과로 확정될 예정**이므로, 웹은
회사 이름이나 슬러그를 코드에 적지 않고 항상 데이터에서 읽습니다.
뉴스는 MVP 범위에서 제외했습니다.

## 트리

```
dev-career-compass/
├── .github/workflows/
│   ├── collect.yml            매일 1회 공고 수집 (F-08)
│   └── verify.yml             lint + build + 근거 링크 검증
│
├── apps/web/
│   └── src/
│       ├── app/
│       │   ├── globals.css            디자인 토큰 (@theme)
│       │   ├── layout.tsx             폰트, metadata
│       │   ├── page.tsx               /                     S1 랜딩
│       │   ├── experience/page.tsx    /experience           S3 경험 입력
│       │   ├── match/page.tsx         /match                S5 직무 목록
│       │   │                          /match?job=backend    S6 역매칭 결과
│       │   ├── [company]/[job]/
│       │   │   └── page.tsx           /oliveyoung/backend   S2 결과 + S4 개인화
│       │   └── api/
│       │       ├── personalize/route.ts   S4 생성 (LLM, 무저장)
│       │       └── match/route.ts         S6 생성 (LLM, 무저장)
│       ├── components/
│       │   ├── ui/                    디자인 캔버스의 컴포넌트 시트와 1:1
│       │   │   ├── Button.tsx  Chip.tsx  StageBadge.tsx
│       │   │   ├── CheckOption.tsx  RepoField.tsx
│       │   │   └── state/{Empty,Loading,Error}.tsx
│       │   ├── company/{CompanyRow,JobButtons}.tsx
│       │   ├── result/{SuggestionCard,DomainChips,EvidenceTimeline}.tsx
│       │   └── experience/ExperienceForm.tsx
│       ├── lib/
│       │   ├── published.ts           data/ 읽기 (서버 전용)
│       │   ├── experience-store.ts    localStorage 읽기·쓰기·지우기
│       │   ├── github.ts              public README 조회 (서버 전용)
│       │   └── llm.ts                 Claude API 클라이언트
│       └── types/data.ts              data/ 를 읽기 위한 웹 내부 타입
│
├── pipeline/
│   ├── pyproject.toml
│   ├── src/career_compass_pipeline/
│   │   ├── collect/{blog,news,jobs}.py
│   │   ├── normalize.py
│   │   ├── extract.py      LLM — 영역 추출 (블로그만)
│   │   ├── aggregate.py    코드만 — 빈도 집계, LLM 금지
│   │   ├── recommend.py    LLM — 제안 생성, 근거 ID 필수
│   │   ├── validate.py     링크 200 · 근거 ID 존재 · 스키마
│   │   ├── publish.py
│   │   └── cli.py
│   └── tests/
│
├── data/
│   ├── index.json                     회사×직무 목록 (S1·S5가 읽음)
│   ├── research/                      연구 요약 (공유 가능한 통계·요약만)
│   ├── published/{회사}/{직무}.json     검증 통과분만
│   ├── fixtures/                      화면용 임시 데이터 (검증 결과 아님)
│   └── raw|work|intermediate/         gitignore됨
│
├── docs/
└── design/                            .dc.html 8개 + canvas.json
```

## 결정과 이유

| 결정 | 이유 |
|---|---|
| **데이터 계약을 먼저 만들지 않음** | 파이프라인 산출물의 모양이 정해지지 않았습니다. 웹은 `types/data.ts` 에 손으로 쓴 내부 타입으로 fixture 를 읽고, 산출물이 나오면 거기에 맞춥니다. 계약을 웹이 먼저 못박으면 파이프라인 쪽을 제약하게 됩니다 |
| **S2와 S4가 같은 라우트** | "공유 URL에 개인화 미포함" 조건(F-06). 별도 URL을 만들면 그게 공유됩니다. 한 라우트에서 localStorage 유무로 S2/S4를 가르고, 공유받은 사람은 S2를 봅니다 |
| **회사 라우트가 루트** | 공유 링크가 제품 기능이라 URL이 사용자 눈에 띕니다. `/oliveyoung/backend` |
| **S6은 쿼리 파라미터** | `/match?job=backend`. 루트에 회사 라우트를 둔 이상 두 칸짜리 경로는 전부 회사 것이라 `/match/backend`를 쓸 수 없습니다. S6은 localStorage 경험값으로 그려지므로 URL이 결과를 대표하지 못하고, 공유해도 의미가 없어 경로를 파지 않는 편이 정직합니다 |
| **`data/published`를 빌드타임에 읽음** | "결과 페이지 즉시 응답" KPI. `generateStaticParams`로 전 조합을 정적 생성합니다. DB 없음 |
| **개인화만 Route Handler** | 10초 KPI + "README·입력값 서버 저장 금지"(F-05). 요청 안에서 처리하고 끝냅니다. 저장 계층을 아예 만들지 않는 것이 조건을 지키는 가장 확실한 방법입니다 |
| **공고는 optional 필드** | 채용 API 승인이 안 나도 동작해야 합니다(F-08). `analysis.json`의 공고 필드를 required로 걸지 않습니다 |

## 회사 목록이 바뀌어도 되게 하는 규칙

회사 목록은 확정되지 않았습니다. 아래를 지키면 회사를 넣고 빼는 일이 데이터 변경만으로 끝납니다.

1. **웹 코드에 회사 이름이나 슬러그를 적지 않습니다.** 전부 `data/index.json`과 `data/published/`에서 읽습니다.
2. `generateStaticParams`는 `data/published/` 디렉터리를 훑어 조합을 만듭니다. 파일을 지우면 그 페이지가 사라집니다.
3. `[company]/[job]/page.tsx`에 `dynamicParams = false`를 둡니다. 게시되지 않은 조합은 404가 되고, 루트 라우트가 아무 경로나 삼키지 않습니다.
4. 아직 근거가 모이지 않은 회사는 `status: "collecting"`으로 두면 S1에 준비 중 카드로만 보이고 결과 페이지를 만들지 않습니다.
5. **슬러그는 한 번 게시하면 바꾸지 않습니다.** 바꾸면 이미 공유된 링크가 죽습니다.

## 슬러그 금지 목록

회사 라우트가 루트에 있어 슬러그가 최상위 경로를 그대로 차지합니다. `match`라는 슬러그를 가진 회사가 생기면 그 회사 페이지는 영영 열리지 않습니다.

지금 웹이 쓰는 최상위 경로는 `experience` · `match` · `ui` · `api` 넷입니다. 회사 슬러그를 정할 때 이 넷과 겹치지 않게 해야 하고, 앞으로 최상위 경로를 늘릴 때도 같은 확인이 필요합니다.

슬러그 형식은 소문자와 숫자, 구분은 하이픈입니다 (`^[a-z0-9]+(-[a-z0-9]+)*$`).

## 구현 순서

1. `globals.css` @theme + `components/ui/` — 디자인 캔버스의 토큰·컴포넌트 시트 그대로
2. `data/fixtures/`에 한 조합을 채움
3. S1 → S2 를 fixture로 붙임 (파이프라인 없이 화면 완성)
4. S3 → S5, 그리고 S4·S6 의 자리 잡기
6. 파이프라인. **웹이 fixture로 완주한 뒤에 시작합니다** — 수집이 늦어져도 화면은 이미 서 있습니다

## 아직 정하지 못한 것

- **회사 목록과 슬러그** — 기술 블로그·채용 공고 검증 담당자가 확정합니다.
  웹은 그때까지 `data/fixtures` 로 화면을 완주시킵니다.
- **파이프라인 산출물의 모양** — 정해지면 `apps/web/src/types/data.ts` 와
  `lib/data.ts` 를 거기에 맞춥니다.
- **S4 의 다음 단계, S6 의 3단계 분류 규칙** — `lib/personalize.ts` 가 그 자리이며
  비어 있습니다.
- **경험 체크박스 항목** — `data/experience.json` 은 임시값 9개입니다.
