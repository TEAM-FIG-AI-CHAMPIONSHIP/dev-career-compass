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
