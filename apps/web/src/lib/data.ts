import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";
import type {
  Analysis,
  CompanyIndex,
  Company,
  ExperienceCatalog,
} from "@/types/data";

/**
 * 게시 데이터를 읽습니다. 서버에서만 씁니다 — 클라이언트 컴포넌트에서 import 하면
 * node:fs 때문에 빌드가 깨집니다.
 *
 * 빌드 시점에 읽고 정적으로 굽습니다. "결과 페이지는 즉시" 라는 기준을 맞추는
 * 가장 단순한 방법이고, 덕분에 DB 가 없습니다.
 *
 * data/published 에 내용이 있으면 그쪽을, 없으면 data/fixtures 를 읽습니다.
 * 파이프라인 산출물이 들어오면 코드를 고치지 않아도 그쪽으로 넘어갑니다.
 */

const DATA_ROOT = join(process.cwd(), "..", "..", "data");

function hasCompanies(dir: string): boolean {
  if (!existsSync(dir)) return false;
  return readdirSync(dir).some((entry) => {
    const path = join(dir, entry);
    return statSync(path).isDirectory() && readdirSync(path).some((f) => f.endsWith(".json"));
  });
}

function sourceDir(): string {
  const published = join(DATA_ROOT, "published");
  return hasCompanies(published) ? published : join(DATA_ROOT, "fixtures");
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

/** 지금 어느 데이터를 읽고 있는지. 화면 하단에 표시해 헷갈리지 않게 합니다. */
export function dataSource(): "published" | "fixtures" {
  return sourceDir().endsWith("published") ? "published" : "fixtures";
}

export function getCompanyIndex(): CompanyIndex {
  return readJson<CompanyIndex>(join(sourceDir(), "index.json"));
}

export function getPublishedCompanies(): Company[] {
  return getCompanyIndex().companies.filter((c) => c.status === "published");
}

export function getExperienceCatalog(): ExperienceCatalog {
  return readJson<ExperienceCatalog>(join(DATA_ROOT, "experience.json"));
}

/** 게시된 회사×직무 조합 전부. generateStaticParams 가 씁니다. */
export function listCombinations(): { company: string; job: string }[] {
  const dir = sourceDir();
  const out: { company: string; job: string }[] = [];
  for (const company of readdirSync(dir)) {
    const cdir = join(dir, company);
    if (!statSync(cdir).isDirectory()) continue;
    for (const f of readdirSync(cdir)) {
      if (f.endsWith(".json")) out.push({ company, job: f.replace(/\.json$/, "") });
    }
  }
  return out;
}

export function getAnalysis(company: string, job: string): Analysis | null {
  const path = join(sourceDir(), company, `${job}.json`);
  if (!existsSync(path)) return null;
  return readJson<Analysis>(path);
}

/** 한 직무를 여는 모든 회사의 분석 결과. 역매칭(S6)이 씁니다. */
export function getAnalysesForJob(job: string): Analysis[] {
  return listCombinations()
    .filter((c) => c.job === job)
    .map((c) => getAnalysis(c.company, c.job))
    .filter((a): a is Analysis => a !== null);
}

/** 게시된 조합이 3곳 이상인 직무만. 회사 수가 많은 순서입니다. */
export function listJobs(): { slug: string; name: string; companyCount: number }[] {
  const counts = new Map<string, { name: string; count: number }>();
  for (const { company, job } of listCombinations()) {
    const analysis = getAnalysis(company, job);
    if (!analysis) continue;
    const prev = counts.get(job);
    counts.set(job, { name: analysis.job.name, count: (prev?.count ?? 0) + 1 });
  }
  return [...counts.entries()]
    .map(([slug, v]) => ({ slug, name: v.name, companyCount: v.count }))
    .sort((a, b) => b.companyCount - a.companyCount || a.slug.localeCompare(b.slug));
}
