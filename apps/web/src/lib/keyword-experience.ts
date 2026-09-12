/**
 * 2단계가 남기는 건 경험 카드 id가 아니라 표준 기술 키워드(자유 텍스트)다.
 * 3단계는 그 키워드를 카탈로그 item id로 옮길 때만 초기 체크에 쓴다.
 *
 * 매핑은 알려진 키워드만 보수적으로 연결한다. 확신할 수 없으면 체크하지 않는다.
 */

const KEYWORD_TO_ITEM_IDS: Record<string, readonly string[]> = {
  Express: ["crud", "rest-api"],
  NestJS: ["crud", "rest-api", "microservices"],
  Django: ["crud", "rest-api"],
  FastAPI: ["crud", "rest-api"],
  Flask: ["crud", "rest-api"],
  "Spring Boot": ["crud", "rest-api"],
  PostgreSQL: ["db-design", "sql-analytics"],
  MySQL: ["db-design", "sql-analytics"],
  MongoDB: ["db-design"],
  Prisma: ["db-design"],
  TypeORM: ["db-design"],
  SQLAlchemy: ["db-design"],
  Kafka: ["big-data", "messaging-queue", "data-pipeline", "data-pipeline-ai"],
  Celery: ["messaging-queue", "data-pipeline", "data-pipeline-ai"],
  GraphQL: ["rest-api"],
  Redis: ["realtime"],
  React: ["crud", "component-ui", "state-management"],
  "Next.js": ["crud", "routing-ssr"],
  Vue: ["crud", "component-ui"],
  "Tailwind CSS": ["design-system"],
  Jest: ["testing-fe"],
};

export function itemIdsFromRepositoryKeywords(
  repositoryKeywords: Record<string, string[]> | undefined,
  allowedItemIds: ReadonlySet<string>,
): string[] {
  if (!repositoryKeywords) return [];

  const found = new Set<string>();
  for (const keywords of Object.values(repositoryKeywords)) {
    for (const keyword of keywords) {
      for (const id of KEYWORD_TO_ITEM_IDS[keyword] ?? []) {
        if (allowedItemIds.has(id)) found.add(id);
      }
    }
  }
  return [...found];
}
