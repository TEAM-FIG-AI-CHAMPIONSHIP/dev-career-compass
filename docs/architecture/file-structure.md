# 웹 파일 구조와 라우팅

`apps/web`의 화면 구조와 공개 URL 규칙을 정리합니다. 사용자가 랜딩에서 고르는
두 탐색 경로를 Next.js App Router의 폴더와 일치시키는 것이 목적입니다.

회사의 이름과 슬러그, 제공할 직무는 코드에 직접 적지 않고 `data/`에서 읽습니다.
사용자가 고른 저장소와 경험은 URL이나 서버 저장소에 넣지 않습니다.

## 공개 라우트

| URL | 역할 | URL에 남는 상태 |
|---|---|---|
| `/` | 두 탐색 방법을 고르는 랜딩 | 없음 |
| `/companies` | 관심 회사와 직무 선택 | 없음 |
| `/companies/[company]/[role]` | 회사 기본 결과 + 개인화 결과 | 회사, 직무 |
| `/match` | 경험 기반 탐색의 직무 선택 | 없음 |
| `/match/[role]/repository` | GitHub 저장소 선택 | 직무 |
| `/match/[role]/experience` | 경험 입력 | 직무 |
| `/match/[role]/result` | 경험 기반 회사 역매칭 결과 | 직무 |

`/ui`는 디자인 시스템 확인용 내부 페이지이며 사용자의 탐색 흐름에는 포함하지
않습니다.

핵심 화면을 구분하는 회사와 직무는 경로 세그먼트로 표현합니다. 저장소, 체크한
경험, 단계 번호처럼 개인적이거나 일시적인 값은 쿼리 파라미터로 만들지 않습니다.

## 사용자 흐름

### A. 내 경험으로 회사 찾기

```text
/
└─ /match
   └─ /match/[role]/repository
      └─ /match/[role]/experience
         └─ /match/[role]/result
```

1. 직무를 고르면 그 직무가 이후 모든 단계의 경로에 유지됩니다.
2. 저장소는 선택 사항이며 최대 3개까지 입력합니다.
3. 경험을 저장하면 역매칭 결과로 이동합니다.
4. 결과 URL에는 저장소와 경험값이 포함되지 않습니다.

### B. 관심 회사부터 보기

```text
/
└─ /companies
   └─ /companies/[company]/[role]
      └─ 개인화 입력 시 /match/[role]/repository
         └─ /match/[role]/experience
            └─ /companies/[company]/[role] 로 복귀
```

회사 결과에서 개인화를 시작하면 공통 저장소·경험 입력 화면을 재사용합니다. 이때
돌아갈 회사 결과 URL은 `sessionStorage`에 잠시 보관합니다. 입력이 끝나면 해당 값을
지우고 원래 회사 결과로 돌아갑니다. 따라서 기본 결과와 개인화 결과의 canonical
URL은 모두 `/companies/[company]/[role]`입니다.

## Next.js 폴더 구조

```text
apps/web/src/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx                            /
│   ├── companies/
│   │   ├── page.tsx                        /companies
│   │   └── [company]/[role]/
│   │       ├── page.tsx                    회사 기본·개인화 결과
│   │       └── PersonalizedPanel.tsx        브라우저 경험에 따른 개인화 영역
│   ├── match/
│   │   ├── page.tsx                        /match
│   │   └── [role]/
│   │       ├── layout.tsx                  유효 직무 정적 경로 생성
│   │       ├── repository/page.tsx         저장소 선택
│   │       ├── experience/page.tsx         경험 입력
│   │       └── result/
│   │           ├── page.tsx                역매칭 결과
│   │           └── ReverseResult.tsx        브라우저 경험 기반 결과 영역
│   └── ui/                                 디자인 시스템 확인용
├── components/
│   ├── company/CompanyList.tsx
│   ├── experience/
│   │   ├── RepositoryForm.tsx
│   │   └── ExperienceForm.tsx
│   ├── result/
│   └── ui/
├── lib/
│   ├── data.ts                             게시·fixture 데이터 읽기
│   ├── routes.ts                           공개 URL 생성 함수
│   ├── experience-store.ts                 완성된 경험 localStorage 상태
│   ├── match-flow-store.ts                 입력 중 복귀·저장소 sessionStorage 상태
│   └── personalize.ts
└── types/data.ts
```

## URL과 브라우저 상태의 경계

| 값 | 저장 위치 | 수명 | 이유 |
|---|---|---|---|
| 회사 슬러그 | URL path | 공유 링크 수명 | 결과 화면을 식별함 |
| 직무 슬러그 | URL path | 공유 링크 수명 | 모든 분석 결과의 필수 맥락임 |
| 경험 항목·프로젝트 단계 | `localStorage` | 사용자가 지울 때까지 | 다른 회사에서도 재사용하지만 공유하면 안 됨 |
| 선택한 GitHub 저장소 | 최종 입력은 `localStorage` | 사용자가 지울 때까지 | 개인 입력이며 URL에 노출하지 않음 |
| 입력 중 저장소·복귀 URL | `sessionStorage` | 입력 완료 또는 탭 종료까지 | 두 진입로가 같은 입력 화면을 안전하게 재사용함 |

브라우저 저장소를 사용할 수 없는 환경에서도 흐름은 동작합니다. 복귀 상태를 읽지
못하면 `/match/[role]/result`를 기본 목적지로 사용합니다.

## 결정과 이유

| 결정 | 이유 |
|---|---|
| 핵심 흐름에서 쿼리 파라미터를 쓰지 않음 | 단계와 화면 맥락이 URL 경로만으로 읽히고, 새로고침·공유 시 의미가 흐려지지 않습니다 |
| 회사 결과를 `/companies/[company]/[role]`에 둠 | 회사와 직무가 모두 URL에 드러나며 `match`, `ui`, `api` 같은 최상위 경로와 회사 슬러그가 충돌하지 않습니다 |
| 회사 기본·개인화 결과가 같은 URL을 사용함 | 개인화는 브라우저 경험값에 따른 표현 차이입니다. 공유 링크에는 개인 경험이 포함되지 않아야 합니다 |
| 저장소와 경험 입력 화면을 두 진입로가 공유함 | 같은 입력 규칙과 저장 정책을 한 컴포넌트에서 유지하며 중복 화면을 만들지 않습니다 |
| 게시 데이터를 빌드 시점에 읽음 | `generateStaticParams`로 유효한 회사×직무와 직무 단계를 미리 만들 수 있고 결과가 즉시 열립니다 |
| `routes.ts`에서 경로를 생성함 | 링크 문자열이 여러 컴포넌트에서 어긋나는 것을 막습니다 |

상세한 선택 배경과 영향은
[`adr-001-route-structure.md`](./adr-001-route-structure.md)에 기록합니다.

## 데이터가 바뀌어도 지켜야 할 규칙

1. 웹 코드에 회사 이름이나 회사 슬러그를 직접 적지 않습니다.
2. 회사 결과의 `generateStaticParams`는 게시된 회사×직무 조합을
   `{ company, role }`로 변환합니다.
3. `/match/[role]`의 `generateStaticParams`는 게시된 분석이 있는 직무를 사용합니다.
4. 동적 경로는 `dynamicParams = false`로 제한해 존재하지 않는 조합을 404로 처리합니다.
5. 회사와 직무 슬러그는 한 번 게시하면 바꾸지 않습니다. 변경이 불가피하면 이전
   주소에서 새 주소로 명시적인 영구 리다이렉트를 추가합니다.

슬러그 형식은 소문자와 숫자, 구분은 하이픈입니다
(`^[a-z0-9]+(-[a-z0-9]+)*$`).

## 아직 정하지 않은 것

- 회사 목록과 실제 제공 직무
- 파이프라인 최종 산출물 스키마
- 회사 개인화의 다음 단계 선택 규칙
- 경험 역매칭의 3단계 분류 규칙
- GitHub README를 가져와 분석하는 서버 로직
