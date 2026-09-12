# GitHub 저장소 키워드 추출 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/match/[role]/repository` 화면을 목업 구조로 교체하고, 사용자가 입력한 GitHub 공개 저장소 링크를 서버에서 탐색해 표준 기술 키워드를 추출·표시·세션 저장까지 구현한다.

**Architecture:** 브라우저(RepositoryForm)가 저장소 URL마다 신규 Next.js Route Handler(`POST /api/repo-keywords`)를 호출한다. 서버는 GitHub REST API(공개 데이터, 선택적 `GITHUB_TOKEN`)로 언어 비율·루트 설정 파일을 가져와 순수 함수 규칙 기반 추출기(`repo-keywords.ts`)로 키워드를 뽑아 응답하며 아무것도 저장하지 않는다. 브라우저는 응답을 화면에 칩으로 보여주고 세션 스토리지(`match-flow-store.ts`)에만 저장한다.

**Tech Stack:** Next.js 16 App Router (Route Handlers), React 19, TypeScript strict, Tailwind v4 토큰(`globals.css`), 표준 `fetch`/`AbortController`(Node 20 내장). 새 테스트 프레임워크는 추가하지 않는다.

**Spec:** `docs/superpowers/specs/2026-09-12-repository-keyword-extraction-design.md`

## Global Constraints

- 웹 영역 확인 명령은 `npm run lint`, `npm run build`다 (`docs/collaboration.md`).
- `apps/web`에는 테스트 러너가 없다 — 새 테스트 프레임워크를 추가하지 않는다(스펙의 "테스트" 절 결정). 순수 함수는 `npx --yes tsx`로 임시 스크립트를 돌려 수동 검증하고, 스크립트는 커밋하지 않는다.
- GitHub 저장소 URL, 추출 키워드, README/설정파일 원문 어느 것도 서버에 저장하지 않는다 — 세션 스토리지에만 둔다.
- 색·타이포·라운드는 `apps/web/src/app/globals.css`에 이미 정의된 토큰만 쓴다. 새 색상 값을 추가하지 않는다.
- `personalize.ts`의 `personalize()` / `reverseMatch()`와 `data/experience.json`의 기존 9개 체크 항목은 이번 작업 범위 밖이다 — 건드리지 않는다.
- 커밋 메시지는 `type: 내용` 형식(`docs/collaboration.md`), 이슈 연결은 PR에서 `Closes #15`.
- 브랜치는 이미 `feat/repository-link-keyword-extraction`으로 체크아웃돼 있다.

---

### Task 1: 규칙 기반 추출기 순수 함수

**Files:**
- Create: `apps/web/src/lib/repo-keywords.ts`

**Interfaces:**
- Produces:
  - `parseGithubUrl(input: string): { owner: string; repo: string } | null`
  - `extractKeywordsFromManifest(manifestText: string): string[]`
  - `pickLanguageKeywords(languages: Record<string, number>): string[]`
  - `mergeKeywords(...groups: string[][]): string[]`
  - `KEYWORD_RULES: { keyword: string; matches: string[] }[]`

- [ ] **Step 1: 파일 작성**

`apps/web/src/lib/repo-keywords.ts` 전체 내용:

```ts
/**
 * GitHub 저장소를 서버에서 훑어 표준 기술 키워드를 뽑는 규칙 기반 추출기.
 *
 * node:fs 등 서버 전용 API에 기대지 않는 순수 함수만 둔다 — API 라우트와
 * RepositoryForm(클라이언트)이 같은 파싱/검증 로직을 공유하기 위해서다.
 *
 * 매칭은 포맷별 파서 없이 파일 원문에서 소문자 부분일치로만 찾는다. 단순한 대신
 * "preact"가 "react" 토큰에 걸리는 것처럼 드물게 오탐이 날 수 있다 — 참고 정보
 * 표시가 목적이라 감수한다.
 */

export type KeywordRule = { keyword: string; matches: string[] };

export const KEYWORD_RULES: KeywordRule[] = [
  { keyword: "React", matches: ["react"] },
  { keyword: "Next.js", matches: ["next"] },
  { keyword: "Vue", matches: ["vue"] },
  { keyword: "Express", matches: ["express"] },
  { keyword: "NestJS", matches: ["nestjs"] },
  { keyword: "Django", matches: ["django"] },
  { keyword: "FastAPI", matches: ["fastapi"] },
  { keyword: "Flask", matches: ["flask"] },
  { keyword: "Spring Boot", matches: ["spring-boot", "springframework.boot"] },
  { keyword: "Redis", matches: ["ioredis", "redis"] },
  { keyword: "PostgreSQL", matches: ["postgres", "psycopg2"] },
  { keyword: "MySQL", matches: ["mysql2", "mysql"] },
  { keyword: "MongoDB", matches: ["mongoose", "pymongo", "mongodb"] },
  { keyword: "Prisma", matches: ["prisma"] },
  { keyword: "TypeORM", matches: ["typeorm"] },
  { keyword: "SQLAlchemy", matches: ["sqlalchemy"] },
  { keyword: "Kafka", matches: ["kafkajs", "kafka-python", "kafka"] },
  { keyword: "Celery", matches: ["celery"] },
  { keyword: "GraphQL", matches: ["graphql"] },
  { keyword: "Jest", matches: ["jest"] },
  { keyword: "pytest", matches: ["pytest"] },
  { keyword: "Tailwind CSS", matches: ["tailwindcss"] },
];

/** package.json/requirements.txt 등 설정 파일 원문에서 알려진 키워드를 찾는다. */
export function extractKeywordsFromManifest(manifestText: string): string[] {
  const lower = manifestText.toLowerCase();
  return KEYWORD_RULES.filter((rule) =>
    rule.matches.some((token) => lower.includes(token.toLowerCase())),
  ).map((rule) => rule.keyword);
}

/**
 * CSS/HTML은 다른 언어와 같이 나오면 거의 항상 노이즈다. 다른 신호가 있을 때만
 * 걸러내고, 그것만 있는 저장소라면 그대로 보여준다.
 */
const LANGUAGE_STOPLIST = new Set(["CSS", "HTML"]);

/** GitHub `/languages` 응답(언어→바이트)에서 상위 언어 이름을 뽑는다. */
export function pickLanguageKeywords(languages: Record<string, number>): string[] {
  const names = Object.entries(languages)
    .sort((a, b) => b[1] - a[1])
    .map(([name]) => name);
  const hasOtherSignal = names.some((name) => !LANGUAGE_STOPLIST.has(name));
  return names
    .filter((name) => !hasOtherSignal || !LANGUAGE_STOPLIST.has(name))
    .slice(0, 3);
}

/** 여러 키워드 목록을 순서를 지키며 합치고, 중복을 지우고, 최대 8개로 자른다. */
export function mergeKeywords(...groups: string[][]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const group of groups) {
    for (const keyword of group) {
      if (!seen.has(keyword)) {
        seen.add(keyword);
        out.push(keyword);
      }
    }
  }
  return out.slice(0, 8);
}

const GITHUB_URL_RE =
  /^(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?\/?$/;

/**
 * "https://github.com/owner/repo" 형태(.git 접미사·후행 슬래시·프로토콜 생략
 * 허용)만 owner/repo로 뽑는다. 추가 경로 세그먼트(/tree/main 등)가 붙으면 null.
 */
export function parseGithubUrl(input: string): { owner: string; repo: string } | null {
  const match = GITHUB_URL_RE.exec(input.trim());
  if (!match) return null;
  const [, owner, repo] = match;
  return { owner, repo };
}
```

- [ ] **Step 2: 임시 스크립트로 동작 검증**

`apps/web/scratch/verify-repo-keywords.ts` 생성(커밋하지 않음, 검증 후 삭제):

```ts
import {
  parseGithubUrl,
  extractKeywordsFromManifest,
  pickLanguageKeywords,
  mergeKeywords,
} from "../src/lib/repo-keywords";

function assertEqual(actual: unknown, expected: unknown, label: string) {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  console.log(a === e ? "PASS" : "FAIL", label, "actual=" + a, "expected=" + e);
}

assertEqual(
  parseGithubUrl("https://github.com/vercel/next.js"),
  { owner: "vercel", repo: "next.js" },
  "full url",
);
assertEqual(
  parseGithubUrl("https://github.com/vercel/next.js/"),
  { owner: "vercel", repo: "next.js" },
  "trailing slash",
);
assertEqual(
  parseGithubUrl("https://github.com/vercel/next.js.git"),
  { owner: "vercel", repo: "next.js" },
  ".git suffix",
);
assertEqual(
  parseGithubUrl("github.com/vercel/next.js"),
  { owner: "vercel", repo: "next.js" },
  "no protocol",
);
assertEqual(
  parseGithubUrl("https://github.com/vercel/next.js/tree/canary"),
  null,
  "extra path segments",
);
assertEqual(parseGithubUrl("not a url"), null, "garbage input");

assertEqual(
  extractKeywordsFromManifest('{"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}'),
  ["React", "Express"],
  "package.json react+express",
);
assertEqual(
  extractKeywordsFromManifest("Django==4.2\nfastapi>=0.100"),
  ["Django", "FastAPI"],
  "requirements.txt django+fastapi",
);

assertEqual(
  pickLanguageKeywords({ TypeScript: 50000, JavaScript: 20000, CSS: 5000 }),
  ["TypeScript", "JavaScript"],
  "languages with CSS filtered out",
);
assertEqual(pickLanguageKeywords({ CSS: 100 }), ["CSS"], "CSS-only repo keeps CSS");

assertEqual(mergeKeywords(["A", "B"], ["B", "C"], ["D"]), ["A", "B", "C", "D"], "merge dedupe order");
assertEqual(
  mergeKeywords(["1", "2", "3", "4", "5", "6", "7", "8", "9"]),
  ["1", "2", "3", "4", "5", "6", "7", "8"],
  "merge caps at 8",
);

console.log("Done. Check for any FAIL above.");
```

Run:

```bash
cd apps/web
npx --yes tsx scratch/verify-repo-keywords.ts
```

Expected: 모든 줄이 `PASS`로 시작한다. `FAIL`이 있으면 Step 1의 구현을 고친다.

- [ ] **Step 3: 스크래치 파일 정리 후 커밋**

```bash
rm -rf apps/web/scratch
git add apps/web/src/lib/repo-keywords.ts
git commit -m "feat: 저장소 키워드 규칙 기반 추출기 추가"
```

---

### Task 2: `/api/repo-keywords` Route Handler

**Files:**
- Create: `apps/web/src/app/api/repo-keywords/route.ts`

**Interfaces:**
- Consumes: Task 1의 `parseGithubUrl`, `extractKeywordsFromManifest`, `pickLanguageKeywords`, `mergeKeywords`
- Produces: `POST /api/repo-keywords`
  - 요청 바디: `{ url: string }`
  - 성공 응답(200): `{ ok: true, keywords: string[] }`
  - 실패 응답: `{ ok: false, reason: "invalid_url" | "not_found" | "private" | "rate_limited" | "unknown" }` (상태 코드는 각각 400/404/403/429/502)

- [ ] **Step 1: 파일 작성**

`apps/web/src/app/api/repo-keywords/route.ts` 전체 내용:

```ts
import {
  parseGithubUrl,
  extractKeywordsFromManifest,
  pickLanguageKeywords,
  mergeKeywords,
} from "@/lib/repo-keywords";

/**
 * GitHub 공개 저장소를 서버에서 훑어 표준 키워드를 뽑는다. 아무것도 저장하지
 * 않는다 — 요청마다 새로 조회하고 응답만 돌려준다.
 *
 * GITHUB_TOKEN 환경 변수가 있으면 시간당 5000회, 없으면 60회로 제한된다. 없어도
 * 정상 동작해야 한다(선택적).
 */

const GITHUB_API = "https://api.github.com";
const REQUEST_TIMEOUT_MS = 8000;

const RECOGNIZED_MANIFESTS = [
  "package.json",
  "requirements.txt",
  "pyproject.toml",
  "Pipfile",
  "pom.xml",
  "build.gradle",
  "build.gradle.kts",
  "go.mod",
  "Cargo.toml",
  "Gemfile",
  "composer.json",
];

type GithubRepoResponse = { private?: boolean };
type GithubContentEntry = { name: string; type: string; download_url: string | null };
type Reason = "invalid_url" | "not_found" | "private" | "rate_limited" | "unknown";

function githubHeaders(): HeadersInit {
  const headers: Record<string, string> = { Accept: "application/vnd.github+json" };
  if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  return headers;
}

async function fetchGithub(url: string): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { headers: githubHeaders(), signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

function errorResponse(reason: Reason, status: number): Response {
  return Response.json({ ok: false, reason }, { status });
}

export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return errorResponse("invalid_url", 400);
  }

  const url =
    typeof body === "object" && body !== null && "url" in body
      ? (body as { url: unknown }).url
      : undefined;

  if (typeof url !== "string") return errorResponse("invalid_url", 400);

  const parsed = parseGithubUrl(url);
  if (!parsed) return errorResponse("invalid_url", 400);

  const { owner, repo } = parsed;

  try {
    const repoRes = await fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}`);
    if (repoRes.status === 404) return errorResponse("not_found", 404);
    if (repoRes.status === 403) return errorResponse("rate_limited", 429);
    if (!repoRes.ok) return errorResponse("unknown", 502);

    const repoData = (await repoRes.json()) as GithubRepoResponse;
    if (repoData.private) return errorResponse("private", 403);

    const [languagesRes, contentsRes] = await Promise.all([
      fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}/languages`),
      fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}/contents`),
    ]);

    const languages = languagesRes.ok
      ? ((await languagesRes.json()) as Record<string, number>)
      : {};
    const contentsJson = contentsRes.ok ? await contentsRes.json() : [];
    const rootFiles: GithubContentEntry[] = Array.isArray(contentsJson) ? contentsJson : [];

    const manifestEntries = rootFiles.filter(
      (entry) => entry.type === "file" && RECOGNIZED_MANIFESTS.includes(entry.name),
    );

    const manifestTexts = await Promise.all(
      manifestEntries
        .filter((entry) => entry.download_url)
        .map(async (entry) => {
          const res = await fetchGithub(entry.download_url as string);
          return res.ok ? await res.text() : "";
        }),
    );

    const manifestKeywords = manifestTexts.flatMap((text) => extractKeywordsFromManifest(text));
    const languageKeywords = pickLanguageKeywords(languages);
    const dockerKeyword = rootFiles.some((entry) => entry.name === "Dockerfile") ? ["Docker"] : [];

    const keywords = mergeKeywords(languageKeywords, manifestKeywords, dockerKeyword);

    return Response.json({ ok: true, keywords });
  } catch {
    return errorResponse("unknown", 502);
  }
}
```

- [ ] **Step 2: 개발 서버로 수동 검증**

터미널 A:

```bash
cd apps/web
npm run dev
```

터미널 B (서버가 뜬 뒤):

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/expressjs/express"}' \
  http://localhost:3000/api/repo-keywords

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/this-owner-does-not-exist-zzz/this-repo-either"}' \
  http://localhost:3000/api/repo-keywords

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/foo/bar"}' \
  http://localhost:3000/api/repo-keywords
```

기대 결과:
- 첫 번째: `{"ok":true,"keywords":[...]}` 이고 `keywords`에 `"Express"`가 포함된다(언어 키워드로 `"JavaScript"`나 `"TypeScript"`도 함께 나올 수 있다).
- 두 번째: `{"ok":false,"reason":"not_found"}`
- 세 번째: `{"ok":false,"reason":"invalid_url"}`

private 저장소 케이스는 실제로 만들기 번거로우므로 Step 1 코드의 `if (repoData.private)` 분기를 눈으로 리뷰하는 것으로 갈음한다.

- [ ] **Step 3: 커밋**

```bash
git add apps/web/src/app/api/repo-keywords/route.ts
git commit -m "feat: GitHub 저장소 키워드 추출 API 라우트 추가"
```

---

### Task 3: 세션 저장소에 키워드 필드 추가

**Files:**
- Modify: `apps/web/src/lib/match-flow-store.ts`

**Interfaces:**
- Produces (변경): `MatchFlow` 타입에 `repositoryKeywords: Record<string, string[]>` 추가. `saveMatchRepositories(role: string, repositories: string[], repositoryKeywords: Record<string, string[]>): void`. `finishMatchFlow(role)`가 돌려주는 객체에도 `repositoryKeywords: Record<string, string[]>` 추가.
- Consumes (Task 6에서): 위 변경된 시그니처 그대로 사용.

- [ ] **Step 1: 타입과 파싱 가드 수정**

`apps/web/src/lib/match-flow-store.ts:6-56`을 아래로 교체:

```ts
export type MatchFlow = {
  role: string;
  returnTo: string;
  repositories: string[];
  /** 저장소 URL → 추출된 키워드. 분석에 실패한 저장소는 키가 없다. */
  repositoryKeywords: Record<string, string[]>;
};

const KEY = "refactor.me.match-flow.v1";
const LEGACY_KEY = "beforejoin.match-flow.v1";
const listeners = new Set<() => void>();

let lastRaw: string | null = null;
let lastParsed: MatchFlow | null = null;

function safeReturnTo(value: string | undefined, role: string): string {
  if (value?.startsWith("/") && !value.startsWith("//")) return value;
  return routes.matchResult(role);
}

function safeKeywords(value: unknown): Record<string, string[]> {
  if (typeof value !== "object" || value === null) return {};
  const out: Record<string, string[]> = {};
  for (const [url, keywords] of Object.entries(value as Record<string, unknown>)) {
    if (Array.isArray(keywords) && keywords.every((k) => typeof k === "string")) {
      out[url] = keywords;
    }
  }
  return out;
}

function readRaw(): string | null {
  try {
    return window.sessionStorage.getItem(KEY) ?? window.sessionStorage.getItem(LEGACY_KEY);
  } catch {
    return null;
  }
}

function getSnapshot(): MatchFlow | null {
  const raw = readRaw();
  if (raw !== lastRaw) {
    lastRaw = raw;
    try {
      const value = raw
        ? (JSON.parse(raw) as Partial<MatchFlow> & { repositoryKeywords?: unknown })
        : null;
      lastParsed =
        value &&
        typeof value.role === "string" &&
        typeof value.returnTo === "string" &&
        Array.isArray(value.repositories)
          ? {
              role: value.role,
              returnTo: safeReturnTo(value.returnTo, value.role),
              repositories: value.repositories.filter(
                (repository): repository is string => typeof repository === "string",
              ),
              repositoryKeywords: safeKeywords(value.repositoryKeywords),
            }
          : null;
    } catch {
      lastParsed = null;
    }
  }
  return lastParsed;
}
```

- [ ] **Step 2: 읽기/쓰기 함수 수정**

`apps/web/src/lib/match-flow-store.ts`에서 `beginMatchFlow`, `saveMatchRepositories`, `finishMatchFlow`를 아래로 교체 (파일의 나머지 — `getServerSnapshot`, `subscribe`, `emit`, `write`, `useMatchFlow` — 는 그대로 둔다):

```ts
/** 회사 결과에서 시작한 경우, 완료 뒤 돌아갈 URL만 세션 동안 보관합니다. */
export function beginMatchFlow(role: string, returnTo?: string): void {
  const current = getSnapshot();
  write({
    role,
    returnTo: safeReturnTo(returnTo, role),
    repositories: current?.role === role ? current.repositories : [],
    repositoryKeywords: current?.role === role ? current.repositoryKeywords : {},
  });
}

export function saveMatchRepositories(
  role: string,
  repositories: string[],
  repositoryKeywords: Record<string, string[]>,
): void {
  const current = getSnapshot();
  write({
    role,
    returnTo:
      current?.role === role ? current.returnTo : routes.matchResult(role),
    repositories,
    repositoryKeywords,
  });
}

/** 경험 저장 직전에 임시 흐름을 꺼내고 지웁니다. */
export function finishMatchFlow(role: string): {
  active: boolean;
  returnTo: string;
  repositories: string[];
  repositoryKeywords: Record<string, string[]>;
} {
  const current = getSnapshot();
  const active = current?.role === role;
  const result = {
    active,
    returnTo: active ? current.returnTo : routes.matchResult(role),
    repositories: active ? current.repositories : [],
    repositoryKeywords: active ? current.repositoryKeywords : {},
  };

  try {
    window.sessionStorage.removeItem(KEY);
    window.sessionStorage.removeItem(LEGACY_KEY);
  } catch {
    // 다음 화면으로 가는 데 저장소 삭제 성공 여부는 영향을 주지 않습니다.
  }
  emit();
  return result;
}
```

`apps/web/src/components/experience/ExperienceForm.tsx:54`의 `finishMatchFlow(role)` 호출부는 반환 타입에 필드가 하나 늘 뿐 기존 사용(`flow.active`, `flow.returnTo`, `flow.repositories`)은 그대로 컴파일된다 — 수정하지 않는다.

- [ ] **Step 3: 타입 검증**

```bash
cd apps/web
npx tsc --noEmit
```

기대 결과: 에러 없음. (`RepositoryForm.tsx`는 아직 옛 2-인자 `saveMatchRepositories` 호출을 쓰고 있어 이 시점엔 타입 에러가 난다 — Task 6에서 그 파일을 고치면 해소된다. 지금은 `match-flow-store.ts` 자체에 새 에러가 없는지만 확인한다: `npx tsc --noEmit 2>&1 | grep match-flow-store` 결과가 비어 있어야 한다.)

- [ ] **Step 3: 커밋**

```bash
git add apps/web/src/lib/match-flow-store.ts
git commit -m "feat: 세션 저장소에 저장소 키워드 필드 추가"
```

---

### Task 4: 아이콘 추가 + RepoField를 URL 입력으로 변경

**Files:**
- Modify: `apps/web/src/components/ui/icons.tsx`
- Modify: `apps/web/src/components/ui/RepoField.tsx`

**Interfaces:**
- Produces: `GithubIcon(props: IconProps)`, `ArrowLeftIcon(props: IconProps)` (icons.tsx가 이미 export하는 `IconProps`와 동일한 시그니처). `RepoField`의 props 타입은 바뀌지 않는다(`value`, `onChange`, `error`) — 내부 표시만 바뀐다.

- [ ] **Step 1: 아이콘 추가**

`apps/web/src/components/ui/icons.tsx` 맨 끝(`DistantIcon` 정의 다음)에 추가:

```ts
/** GitHub 저장소 입력 배지에 쓰는 아이콘. 로고를 그대로 쓰지 않고 기존 선 굵기·그리드에 맞춘 단순화 버전. */
export const GithubIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M6.6 5.4L4.3 3.5M13.4 5.4l2.3-1.9" />
    <circle cx="10" cy="10.6" r="5.3" />
    <path d="M7.7 13.3c.6.5 1.4.8 2.3.8s1.7-.3 2.3-.8" />
  </Icon>
);

/** ArrowRightIcon의 좌우 반전. 뒤로 가기 링크에 쓴다. */
export const ArrowLeftIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M17 10H6" />
    <path d="M9 6l-4 4 4 4" />
  </Icon>
);
```

- [ ] **Step 2: RepoField를 URL 입력으로 교체**

`apps/web/src/components/ui/RepoField.tsx` 전체 내용을 아래로 교체:

```tsx
"use client";

import { cn } from "@/lib/cn";
import { GithubIcon } from "@/components/ui/icons";

/**
 * GitHub 저장소 링크 입력. 선택 항목이고 최대 3개까지 받습니다.
 *
 * README/설정 파일은 공개 저장소만 조회하고 원문을 저장하지 않습니다.
 * 읽을 수 없는 저장소는 막지 않고, 그 항목만 빼고 진행한다고 알립니다 —
 * 저장소를 평가하거나 첨삭하는 화면이 아닙니다.
 */
export function RepoField({
  value,
  onChange,
  error,
  ...props
}: {
  value: string;
  onChange: (next: string) => void;
  error?: string;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "value" | "onChange">) {
  return (
    <div className="flex flex-col gap-1.5">
      <div
        className={cn(
          "flex min-h-11 items-center gap-2.5 rounded-card border bg-surface px-3.5 py-3",
          "focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent",
          error ? "border-warn" : "border-line-strong",
        )}
      >
        <GithubIcon
          size={16}
          strokeWidth={1.6}
          className="shrink-0 text-ink-soft"
          aria-hidden="true"
        />
        <input
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          placeholder="https://github.com/username/repo"
          aria-label="GitHub 저장소 링크"
          aria-invalid={error ? true : undefined}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "min-w-0 flex-1 bg-transparent font-mono text-[0.84375rem] text-ink",
            "placeholder:font-sans placeholder:text-[0.8125rem] placeholder:text-ink-muted",
            "focus:outline-none",
          )}
          {...props}
        />
      </div>
      {error && (
        <span className="text-caption leading-[1.7] text-warn">{error}</span>
      )}
    </div>
  );
}
```

- [ ] **Step 3: 타입 검증 후 커밋**

```bash
cd apps/web
npx tsc --noEmit 2>&1 | grep -E "icons\.tsx|RepoField\.tsx"
```

기대 결과: 출력 없음(에러 없음).

```bash
git add apps/web/src/components/ui/icons.tsx apps/web/src/components/ui/RepoField.tsx
git commit -m "feat: GitHub 아이콘 추가 및 저장소 입력을 URL 형태로 변경"
```

---

### Task 5: RepositoryForm을 분석 흐름으로 재작성

**Files:**
- Modify: `apps/web/src/components/experience/RepositoryForm.tsx`

**Interfaces:**
- Consumes:
  - `parseGithubUrl` (Task 1, `@/lib/repo-keywords`)
  - `saveMatchRepositories(role, repositories, repositoryKeywords)` (Task 3, `@/lib/match-flow-store`)
  - `useMatchFlow(role): MatchFlow | null`에서 `flow.repositoryKeywords: Record<string, string[]>` (Task 3)
  - `RepoField` (Task 4, 동일 props)
  - `Chip` (`@/components/ui/Chip`, 기존)
- Produces: `RepositoryForm({ role, catalogVersion }: { role: string; catalogVersion: number })` — props 시그니처는 바뀌지 않는다.

- [ ] **Step 1: 전체 파일 교체**

`apps/web/src/components/experience/RepositoryForm.tsx` 전체 내용을 아래로 교체:

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { RepoField } from "@/components/ui/RepoField";
import { PlusIcon } from "@/components/ui/icons";
import { useExperience } from "@/lib/experience-store";
import { saveMatchRepositories, useMatchFlow } from "@/lib/match-flow-store";
import { parseGithubUrl } from "@/lib/repo-keywords";
import { routes } from "@/lib/routes";

const MAX_REPOSITORIES = 3;

type FieldStatus =
  | { kind: "loading" }
  | { kind: "done"; keywords: string[] }
  | { kind: "error"; message: string };

const REASON_MESSAGES: Record<string, string> = {
  not_found: "비공개 저장소이거나 찾을 수 없어요 — 이 저장소는 건너뜁니다.",
  private: "비공개 저장소이거나 찾을 수 없어요 — 이 저장소는 건너뜁니다.",
  rate_limited: "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요.",
  unknown: "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요.",
};

async function analyzeRepository(url: string): Promise<FieldStatus> {
  try {
    const res = await fetch("/api/repo-keywords", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = (await res.json()) as
      | { ok: true; keywords: string[] }
      | { ok: false; reason: string };
    if (data.ok) return { kind: "done", keywords: data.keywords };
    return { kind: "error", message: REASON_MESSAGES[data.reason] ?? REASON_MESSAGES.unknown };
  } catch {
    return { kind: "error", message: REASON_MESSAGES.unknown };
  }
}

export function RepositoryForm({
  role,
  catalogVersion,
}: {
  role: string;
  catalogVersion: number;
}) {
  const router = useRouter();
  const flow = useMatchFlow(role);
  const experience = useExperience(catalogVersion);
  const [draft, setDraft] = useState<string[] | null>(null);
  const [statuses, setStatuses] = useState<Record<string, FieldStatus>>(() => {
    const initial: Record<string, FieldStatus> = {};
    for (const [url, keywords] of Object.entries(flow?.repositoryKeywords ?? {})) {
      initial[url] = { kind: "done", keywords };
    }
    return initial;
  });
  const [analyzing, setAnalyzing] = useState(false);

  const repositories =
    draft ??
    (flow?.repositories.length
      ? flow.repositories
      : experience?.repos?.length
        ? experience.repos
        : [""]);

  const invalid = repositories.some(
    (repository) => repository.trim() !== "" && !parseGithubUrl(repository.trim()),
  );

  const updateField = (index: number, next: string) => {
    setDraft(
      repositories.map((current, currentIndex) => (currentIndex === index ? next : current)),
    );
  };

  const goWithoutAnalysis = () => {
    saveMatchRepositories(role, [], {});
    router.push(routes.matchExperience(role));
  };

  const analyzeAndContinue = async () => {
    const candidates = repositories
      .map((repository) => repository.trim())
      .filter((repository) => parseGithubUrl(repository) !== null);

    setAnalyzing(true);
    setStatuses((prev) => {
      const next = { ...prev };
      for (const url of candidates) next[url] = { kind: "loading" };
      return next;
    });

    const results = await Promise.all(
      candidates.map(async (url) => [url, await analyzeRepository(url)] as const),
    );

    const nextStatuses: Record<string, FieldStatus> = { ...statuses };
    const keywordsByUrl: Record<string, string[]> = {};
    for (const [url, status] of results) {
      nextStatuses[url] = status;
      if (status.kind === "done") keywordsByUrl[url] = status.keywords;
    }
    setStatuses(nextStatuses);
    setAnalyzing(false);

    saveMatchRepositories(role, candidates, keywordsByUrl);
    router.push(routes.matchExperience(role));
  };

  return (
    <div className="flex max-w-3xl flex-col gap-8">
      <div className="flex flex-col gap-3">
        {repositories.map((repository, index) => {
          const trimmed = repository.trim();
          const status = trimmed ? statuses[trimmed] : undefined;
          const formatError =
            trimmed !== "" && !parseGithubUrl(trimmed)
              ? "GitHub 저장소 링크 형태로 적어주세요."
              : status?.kind === "error"
                ? status.message
                : undefined;

          return (
            <div key={index} className="flex flex-col gap-2">
              <RepoField
                value={repository}
                onChange={(next) => updateField(index, next)}
                error={formatError}
              />
              {status?.kind === "loading" && (
                <span className="text-caption text-ink-soft">
                  저장소를 살펴보는 중이에요…
                </span>
              )}
              {status?.kind === "done" && status.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {status.keywords.map((keyword) => (
                    <Chip key={keyword} tone="accent">
                      {keyword}
                    </Chip>
                  ))}
                </div>
              )}
              {status?.kind === "done" && status.keywords.length === 0 && (
                <span className="text-caption text-ink-soft">찾은 키워드가 없어요.</span>
              )}
            </div>
          );
        })}

        {repositories.length < MAX_REPOSITORIES && (
          <Button
            variant="secondary"
            onClick={() => setDraft([...repositories, ""])}
            className="w-fit"
          >
            <PlusIcon size={14} strokeWidth={1.7} />
            저장소 추가
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3.5 border-t border-line pt-6">
        <Button
          variant="secondary"
          onClick={() => router.push(routes.match)}
          className="min-h-12 px-6 py-4 text-[0.9375rem]"
        >
          ← 직무로
        </Button>
        <Button
          variant="primary"
          onClick={analyzeAndContinue}
          disabled={invalid || analyzing}
          className="min-h-12 px-6 py-4 text-[0.9375rem]"
        >
          {analyzing ? "분석하는 중…" : "분석하고 경험 선택으로"}
        </Button>
        <Button variant="ghost" onClick={goWithoutAnalysis}>
          GitHub 없이 진행
        </Button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: 타입 검증**

```bash
cd apps/web
npx tsc --noEmit 2>&1 | grep RepositoryForm
```

기대 결과: 출력 없음.

- [ ] **Step 3: 커밋**

```bash
git add apps/web/src/components/experience/RepositoryForm.tsx
git commit -m "feat: RepositoryForm에 저장소 분석 흐름 연결"
```

---

### Task 6: 페이지 헤더/카피 교체 + 전체 수동 QA

**Files:**
- Modify: `apps/web/src/app/match/[role]/repository/page.tsx`

**Interfaces:**
- Consumes: `ArrowLeftIcon`, `GithubIcon` (Task 4), `RepositoryForm` (Task 5, 동일 props), `routes.home` (기존)

- [ ] **Step 1: 전체 파일 교체**

`apps/web/src/app/match/[role]/repository/page.tsx` 전체 내용을 아래로 교체:

```tsx
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { RepositoryForm } from "@/components/experience/RepositoryForm";
import { ArrowLeftIcon, GithubIcon } from "@/components/ui/icons";
import { routes } from "@/lib/routes";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "GitHub 저장소 선택" };

export default async function MatchRepositoryPage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-4 sm:px-8 lg:px-20">
        <Link
          href={routes.home}
          className="inline-flex items-center gap-1.5 text-[0.875rem] text-ink-soft no-underline hover:text-ink hover:no-underline"
        >
          <ArrowLeftIcon size={14} strokeWidth={1.7} />
          처음으로
        </Link>
        <ol className="flex items-center gap-2 text-[0.8125rem]">
          <li className="text-ink-soft">1. 직무</li>
          <li aria-hidden="true" className="text-line-strong">
            →
          </li>
          <li className="font-semibold text-accent">2. GitHub</li>
          <li aria-hidden="true" className="text-line-strong">
            →
          </li>
          <li className="text-ink-soft">3. 경험</li>
        </ol>
      </header>

      <main className="flex grow flex-col gap-11 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <div className="flex size-11 items-center justify-center rounded-card bg-accent-tint text-accent">
            <GithubIcon size={22} strokeWidth={1.5} />
          </div>
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
            GitHub 저장소 (선택)
          </h1>
          <p className="text-body text-ink-soft">
            공개 저장소를 살펴 표준 기술 키워드를 찾아 보여드립니다. 찾은 키워드는
            참고용이며, 다음 단계인 경험 입력에서 직접 고른 항목이 우선합니다.
          </p>
          <p className="text-body-sm text-ink-muted">
            저장소 원문은 서버에 저장하지 않고, 공개 저장소만 조회합니다. 비공개
            저장소이거나 신호를 찾지 못하면 안내 후 그 저장소만 건너뛰고 계속
            진행합니다.
          </p>
        </div>

        <RepositoryForm role={role} catalogVersion={catalog.version} />
      </main>
    </>
  );
}
```

- [ ] **Step 2: 전체 수동 QA**

```bash
cd apps/web
npm run dev
```

브라우저에서 확인:
1. `/match/{존재하는 role}/repository`로 접속 — 헤더에 "← 처음으로"와 "1. 직무 → 2. GitHub → 3. 경험"(2. GitHub만 강조)이 보이고, GitHub 아이콘 배지 + 제목 + 안내 문단 2개가 보인다.
2. 저장소 입력 필드에 `https://github.com/expressjs/express`를 넣고 "분석하고 경험 선택으로" 클릭 — 잠깐 "저장소를 살펴보는 중이에요…"가 보인 뒤 경험 입력 페이지로 이동한다.
3. 브라우저 뒤로 가기로 저장소 페이지에 돌아오면 방금 입력한 저장소와 키워드 칩이 그대로 남아 있다(세션 스토리지 유지 확인).
4. 존재하지 않는 저장소 주소(`https://github.com/this-owner-does-not-exist-zzz/nope`)를 넣고 분석 — 다음 단계로는 진행되지만(막히지 않음), 브라우저 개발자 도구의 `sessionStorage.getItem("refactor.me.match-flow.v1")`을 확인했을 때 그 저장소는 `repositoryKeywords`에 없어야 한다.
5. "GitHub 없이 진행"을 눌러도 바로 경험 입력 페이지로 이동한다.
6. "← 직무로"를 누르면 `/match`로 이동한다.

- [ ] **Step 3: 린트/빌드**

```bash
cd apps/web
npm run lint
npm run build
```

기대 결과: 둘 다 에러 없이 통과.

- [ ] **Step 4: 커밋**

```bash
git add apps/web/src/app/match/\[role\]/repository/page.tsx
git commit -m "feat: 저장소 선택 화면을 GitHub 키워드 분석 흐름으로 교체"
```

---

## Self-Review 결과

- **스펙 커버리지:** UI(헤더/본문/입력/칩/하단 액션) → Task 4~6, 아키텍처/API 계약 → Task 2, 규칙 기반 추출기 → Task 1, 세션 저장 → Task 3, 에러 처리 표 → Task 5의 `REASON_MESSAGES`와 Task 2의 `reason` 분기, 테스트 절(새 프레임워크 없이 lint/build+수동 검증) → 각 태스크의 검증 단계와 Task 6 Step 3. 누락 없음.
- **플레이스홀더 스캔:** "TBD"/"나중에" 표현 없음. 모든 단계에 실제 코드/명령을 넣었다.
- **타입 일관성:** `saveMatchRepositories(role, repositories, repositoryKeywords)` 시그니처가 Task 3 정의와 Task 5 호출부에서 동일. `FieldStatus`/`MatchFlow.repositoryKeywords`가 `Record<string, string[]>`로 전 태스크에서 일치. `parseGithubUrl` 반환 타입(`{owner, repo} | null`)이 Task 1~2~5에서 동일하게 쓰인다.
