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
    return (
      statSync(path).isDirectory() &&
      readdirSync(path).some((f) => f.endsWith(".json"))
    );
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
      if (f.endsWith(".json"))
        out.push({ company, job: f.replace(/\.json$/, "") });
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

/**
 * 실제로 내용이 있는 분석만 "매칭 가능"으로 셉니다.
 *
 * fixture 파일은 빈 껍데기로도 미리 만들어 둡니다 — 영역도 제안도 없이
 * company/job 이름만 든 파일입니다. `getAnalysis`는 파일이 있으면 그대로
 * 돌려주므로, 이 함수가 안을 보고 걸러내지 않으면 "8곳 매칭 가능" 같은 숫자가
 * 실제로 만들 것이 하나도 없는 회사까지 셉니다.
 */
/**
 * 존재하는 직무 전부. 매칭 가능한 회사가 있는지와 무관합니다.
 *
 * `index.json`이 회사마다 내건 직무를 구조적으로 정의한 목록입니다 — 분석
 * 파일에 내용이 있는지 보지 않습니다. `/match/{role}/...` 세 화면과 정적 경로
 * 생성이 "이 직무가 있는가"를 물을 때는 이 함수를 씁니다. `listJobs()`는 그
 * 직무를 지금 골라도 되는지(매칭 가능한 회사가 있는지)를 답할 뿐이고, 둘을
 * 하나로 합쳐 두면 회사 데이터가 아직 없는 직무의 URL 자체가 사라집니다 —
 * 다른 직무를 개발·확인하는 사람까지 막게 됩니다.
 */
export function listRoles(): { slug: string; name: string }[] {
  const names = new Map<string, string>();
  for (const company of getCompanyIndex().companies) {
    for (const job of company.jobs ?? []) {
      if (!names.has(job.slug)) names.set(job.slug, job.name);
    }
  }
  return [...names.entries()].map(([slug, name]) => ({ slug, name }));
}

function hasContent(analysis: Analysis): boolean {
  return (
    analysis.domains.length > 0 ||
    analysis.suggestions.new.length > 0 ||
    analysis.suggestions.deepen.length > 0
  );
}

/**
 * 매칭 가능한 회사가 있는 직무만. 회사 수가 많은 순서입니다.
 *
 * 내용 있는 회사가 하나도 없는 직무는 목록에서 뺍니다 — "0곳 매칭 가능"은
 * 고를 이유가 없는 선택지라 안 보이는 편이 낫습니다. 화면은 이미 빈 결과를
 * 다루는 방법(`Empty`)을 갖고 있어서, 4개 직무가 모두 빠져도 화면이 깨지지
 * 않습니다.
 */
export function listJobs(): {
  slug: string;
  name: string;
  companyCount: number;
}[] {
  const counts = new Map<string, { name: string; count: number }>();
  for (const { company, job } of listCombinations()) {
    const analysis = getAnalysis(company, job);
    if (!analysis || !hasContent(analysis)) continue;
    const prev = counts.get(job);
    counts.set(job, { name: analysis.job.name, count: (prev?.count ?? 0) + 1 });
  }
  return [...counts.entries()]
    .map(([slug, v]) => ({ slug, name: v.name, companyCount: v.count }))
    .sort(
      (a, b) => b.companyCount - a.companyCount || a.slug.localeCompare(b.slug),
    );
}
