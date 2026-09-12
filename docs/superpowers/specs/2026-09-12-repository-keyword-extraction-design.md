# GitHub 저장소 링크 기반 키워드 추출 — 설계

관련 이슈: [#15 [feat] GitHub 저장소 링크 기반 키워드 추출 기능 추가](https://github.com/TEAM-FIG-AI-CHAMPIONSHIP/dev-career-compass/issues/15)
브랜치: `feat/repository-link-keyword-extraction`

## 배경

`/match/[role]/repository` 화면은 지금 `owner/repo` 형식 문자열을 최대 3개까지 입력받아 세션 스토리지에 저장만 하고, 저장소 내용을 실제로 살펴보지 않는다(`apps/web/src/components/experience/RepositoryForm.tsx`). 이번 작업은 사용자가 GitHub 저장소 링크(URL)를 입력하면 그 저장소를 서버에서 탐색해 표준 기술 키워드를 추출하고, 화면에 보여준 뒤 세션 스토리지에 저장하는 것까지를 구현한다.

## 범위

**포함**
- 저장소 링크 입력 UI를 화면 목업(사용자 제공 스크린샷) 구조로 교체
- GitHub 공개 저장소를 서버(Next.js Route Handler)에서 탐색해 표준 기술 키워드 목록을 추출
- 추출 결과를 화면에 노출하고, 저장소 URL과 함께 세션 스토리지에 저장

**제외 (다음 작업으로 미룸)**
- `apps/web/src/lib/personalize.ts`의 `personalize()` / `reverseMatch()` — 기업 분석 결과와 비교하는 판단 규칙은 팀이 아직 정하지 않았다는 것이 코드에 명시돼 있어 이번 작업에서 건드리지 않는다.
- `data/experience.json`의 기존 9개 경험 체크 항목에 추출 키워드를 자동 매핑/자동 체크하는 것 — 이 카탈로그는 `data/README-experience.md`에 "아직 확정되지 않은 임시값"이라고 명시돼 있고, 추상적인 경험 유형(예: "캐시를 넣어 응답을 줄여 봤다")이라 저장소 설정 파일에서 신뢰성 있게 추론하기 어렵다. 대신 추출 결과는 독립된 "표준 기술 키워드" 목록으로만 제공한다.

## UI

`/match/[role]/repository`(`page.tsx` + `RepositoryForm.tsx`)만 바꾸고 다른 화면(경험 입력, 결과)은 그대로 둔다. 사용자가 제공한 스크린샷 구조를 따른다.

- **상단바**: 왼쪽 "← 처음으로"(홈), 오른쪽 "1. 직무 → 2. GitHub → 3. 경험" 스텝 표시(현재 단계만 accent 색). 이 페이지에서만 기존 `PageHeader`(로고+브레드크럼) 대신 이 스텝 네비게이션을 쓴다.
- **본문**: accent-tint 배경의 둥근 사각형 안에 GitHub 아이콘(신규 `GithubIcon`, `icons.tsx`에 추가) + 제목 "GitHub 저장소 (선택)" + 안내 문단 2개(공개 저장소만 조회, README/설정파일 원문은 서버에 저장하지 않음, private이거나 신호가 없으면 안내 후 계속 진행).
- **입력 필드**: `RepoField`를 전체 URL 입력(`https://github.com/username/repo` placeholder, 왼쪽 GitHub 아이콘)으로 변경. 최대 3개, "+ 저장소 추가"는 기존 `Button`(secondary) + `PlusIcon`.
- **분석 결과 표시**: 분석이 끝난 필드 아래에 `Chip` 컴포넌트로 키워드 나열. 진행 중에는 필드 옆에 로딩 표시, 실패하면 필드 아래 경고 톤(`text-warn`) 안내 문구.
- **하단 액션**: "← 직무로"(secondary), "분석하고 경험 선택으로"(primary — 클릭 시 입력된 저장소를 모두 분석한 뒤 저장하고 경험 입력 페이지로 이동), "GitHub 없이 진행"(ghost, 기존 스킵 동작 유지).
- 기존 오른쪽 안내 카드(aside)는 제거 — 같은 메시지가 본문 안내 문단에 들어간다.
- 저장소 URL 형식 검사는 "github.com URL처럼 보이는지" 정도로 느슨하게 두고(`parseGithubUrl`), 실제 존재 여부/공개 여부 판단은 서버 응답에 맡긴다.

## 아키텍처 / 데이터 흐름

```
브라우저 (RepositoryForm)
  └─ "분석하고 경험 선택으로" 클릭
       └─ 입력된 URL마다 POST /api/repo-keywords { url }
              └─ [서버] GitHub REST API 호출 (GITHUB_TOKEN 있으면 사용, 없으면 익명)
                   1. GET /repos/{owner}/{repo}            → 존재/공개 여부 확인
                   2. GET /repos/{owner}/{repo}/languages   → 언어 바이트 비율
                   3. GET /repos/{owner}/{repo}/contents    → 루트 파일 목록
                   4. 인식되는 설정 파일만 raw 내용을 가져와 규칙 기반 매칭
              └─ [서버] 언어 상위 항목 + 설정파일 내 알려진 패키지명 매칭 +
                 Dockerfile 존재 여부를 합쳐 표준 키워드 목록(최대 8개)으로 정리해
                 응답. 아무것도 저장하지 않고 응답만 반환한다.
       └─ 결과를 화면에 칩으로 표시, 성공한 저장소 URL+키워드를 세션 스토리지에 저장
       └─ 경험 입력 페이지로 이동 (자동 체크 없음 — 참고 정보로만 노출)
```

## API: `POST /api/repo-keywords`

파일: `apps/web/src/app/api/repo-keywords/route.ts`

**요청**
```json
{ "url": "https://github.com/owner/repo" }
```

**응답 (성공)**
```json
{ "ok": true, "keywords": ["TypeScript", "Next.js", "PostgreSQL", "Docker"] }
```

**응답 (실패)**
```json
{ "ok": false, "reason": "not_found" | "private" | "rate_limited" | "invalid_url" | "unknown" }
```

동작:
1. `parseGithubUrl(url)`로 owner/repo 추출. 실패하면 `invalid_url`.
2. `GET /repos/{owner}/{repo}` 호출. 404 → `not_found`, `private: true` → `private`, 403(레이트리밋) → `rate_limited`.
3. `GET /repos/{owner}/{repo}/languages` 호출해 바이트 비율 상위 언어 추출.
4. `GET /repos/{owner}/{repo}/contents` (루트) 호출해 파일명 목록 확보.
5. 인식 대상 설정 파일(`package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `pom.xml`, `build.gradle`, `build.gradle.kts`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`)이 루트에 있으면 각각의 raw 내용을 가져온다 (`contents` API의 `download_url` 사용).
6. `Dockerfile`이 루트에 있으면 "Docker" 키워드를 추가한다.
7. 서버 환경 변수 `GITHUB_TOKEN`이 설정돼 있으면 모든 GitHub 요청에 `Authorization: Bearer` 헤더를 붙인다(있으면 5000회/시간, 없으면 60회/시간). 값이 없어도 정상 동작해야 한다(선택적).
8. 각 GitHub 호출에 타임아웃(예: 8초)을 둔다. 네트워크 오류/타임아웃은 `unknown`으로 묶는다.
9. 결과가 비어 있어도(신호를 하나도 못 찾음) 실패가 아니라 `{ ok: true, keywords: [] }`로 응답한다 — 화면에서 "찾은 키워드가 없어요"로 안내한다.

루트 디렉터리만 확인하므로, 모노레포처럼 설정 파일이 하위 디렉터리에만 있는 저장소는 이번 버전에서 신호를 못 찾는 경우로 처리된다(향후 개선 여지로 남긴다).

## 규칙 기반 추출기

파일: `apps/web/src/lib/repo-keywords.ts` (순수 함수, `node:fs` 등 서버 전용 API에 의존하지 않아 유닛 테스트하기 쉽게 만든다)

```ts
export type KeywordRule = {
  keyword: string;
  /** 설정 파일 원문에서 이 토큰 중 하나라도 발견되면 매칭 */
  matches?: string[];
};

export const KEYWORD_RULES: KeywordRule[] = [
  { keyword: "React", matches: ["\"react\""] },
  { keyword: "Next.js", matches: ["\"next\""] },
  { keyword: "Express", matches: ["\"express\""] },
  { keyword: "NestJS", matches: ["@nestjs/core"] },
  { keyword: "Django", matches: ["django"] },
  { keyword: "FastAPI", matches: ["fastapi"] },
  { keyword: "Flask", matches: ["flask"] },
  { keyword: "Spring Boot", matches: ["spring-boot"] },
  { keyword: "Redis", matches: ["redis", "ioredis"] },
  { keyword: "PostgreSQL", matches: ["pg", "postgres", "psycopg2"] },
  { keyword: "MySQL", matches: ["mysql2", "mysql"] },
  { keyword: "MongoDB", matches: ["mongoose", "pymongo"] },
  { keyword: "Prisma", matches: ["prisma"] },
  { keyword: "TypeORM", matches: ["typeorm"] },
  { keyword: "SQLAlchemy", matches: ["sqlalchemy"] },
  { keyword: "Kafka", matches: ["kafkajs", "kafka-python"] },
  { keyword: "Celery", matches: ["celery"] },
  // ... 필요에 따라 추가
];

export function extractKeywordsFromManifest(manifestText: string): string[] {
  const lower = manifestText.toLowerCase();
  return KEYWORD_RULES
    .filter((rule) => rule.matches?.some((token) => lower.includes(token.toLowerCase())))
    .map((rule) => rule.keyword);
}

const LANGUAGE_STOPLIST = new Set(["CSS", "HTML"]);

export function pickLanguageKeywords(languages: Record<string, number>): string[] {
  const entries = Object.entries(languages).sort((a, b) => b[1] - a[1]);
  const names = entries.map(([name]) => name);
  const hasOtherSignal = names.some((n) => !LANGUAGE_STOPLIST.has(n));
  return names.filter((n) => !hasOtherSignal || !LANGUAGE_STOPLIST.has(n)).slice(0, 3);
}

export function mergeKeywords(...groups: string[][]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const group of groups) {
    for (const kw of group) {
      if (!seen.has(kw)) {
        seen.add(kw);
        out.push(kw);
      }
    }
  }
  return out.slice(0, 8);
}
```

`route.ts`는 `pickLanguageKeywords(언어 응답)`, 설정 파일마다 `extractKeywordsFromManifest(원문)`, `Dockerfile` 존재 시 `"Docker"`를 모아 `mergeKeywords(...)`로 합친다.

## 저장 위치

`apps/web/src/lib/match-flow-store.ts`의 `MatchFlow` 타입에 필드를 추가한다.

```ts
export type MatchFlow = {
  role: string;
  returnTo: string;
  repositories: string[];
  /** 저장소 URL → 추출된 키워드. 분석에 실패한 저장소는 키가 없다. */
  repositoryKeywords: Record<string, string[]>;
};
```

- `getSnapshot()`의 파싱 가드에 `repositoryKeywords`를 옵셔널로 읽고 없으면 `{}`로 채운다(구버전 세션 데이터와 호환).
- `saveMatchRepositories`를 `saveMatchRepositories(role, repositories, repositoryKeywords)`로 확장하거나, 별도 `saveRepositoryKeywords(role, keywords)`를 추가한다 — 구현 시 기존 호출부(`RepositoryForm.tsx`)와 자연스럽게 맞는 쪽으로 정리한다.
- 서버에는 어떤 것도 저장하지 않는다(결정 3번 유지) — 세션 스토리지만 사용.

## 에러 처리

| 상황 | 서버 응답 | 화면 |
|---|---|---|
| URL 형식이 github.com 저장소로 안 보임 | `invalid_url` | 필드 아래 "GitHub 저장소 주소 형태로 적어주세요" (기존 인라인 에러 패턴 재사용) |
| 저장소 없음/비공개 | `not_found` / `private` | "비공개 저장소이거나 찾을 수 없어요 — 이 저장소는 건너뜁니다", 키워드 없이 계속 진행 |
| GitHub API 레이트리밋 | `rate_limited` | "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요", 건너뛰고 진행 |
| 신호를 못 찾음 | `ok:true, keywords: []` | "찾은 키워드가 없어요" |
| 그 외 네트워크/타임아웃 | `unknown` | 위 레이트리밋과 동일한 안내 문구 재사용 |

실패한 저장소가 있어도 "GitHub 없이 진행"과 동일하게 다음 단계 진행을 막지 않는다(완료 기준 4번).

## 테스트

프로젝트의 `apps/web`에는 현재 테스트 러너가 없고, 이 영역의 확인 기준은 `docs/collaboration.md`에 `npm run lint` / `npm run build`로 명시돼 있다. 이번 작업에서 새 테스트 프레임워크를 들이는 대신:
- `repo-keywords.ts`의 순수 함수(`extractKeywordsFromManifest`, `pickLanguageKeywords`, `mergeKeywords`)는 로직이 단순하므로 구현 중 임시 스크립트로 수동 검증한다.
- `npm run lint`, `npm run build`를 통과시켜 타입/빌드 오류가 없는지 확인한다.
- 브라우저에서 공개 저장소 URL로 실제 흐름(성공/실패 케이스 각각)을 확인한다.

## 파일 변경 목록

- `apps/web/src/app/match/[role]/repository/page.tsx` — 헤더/카피 교체
- `apps/web/src/components/experience/RepositoryForm.tsx` — UI 구조 교체, 분석 호출·상태 관리 추가
- `apps/web/src/components/ui/RepoField.tsx` — URL 입력 형태로 변경
- `apps/web/src/components/ui/icons.tsx` — `GithubIcon`, `ArrowLeftIcon` 추가
- `apps/web/src/lib/routes.ts` — 필요 시 API 경로 상수 추가(선택)
- `apps/web/src/lib/match-flow-store.ts` — `repositoryKeywords` 필드 추가
- `apps/web/src/lib/repo-keywords.ts` — 신규, 규칙 기반 추출기
- `apps/web/src/app/api/repo-keywords/route.ts` — 신규, Route Handler
