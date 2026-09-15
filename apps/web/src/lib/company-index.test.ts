import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import type { CompanyIndex } from "@/types/data";

const index = JSON.parse(
  readFileSync(
    new URL("../../../../data/fixtures/index.json", import.meta.url),
    "utf8",
  ),
) as CompanyIndex;

const ALL_ROLES = ["backend", "frontend", "mobile", "data-ai"];
const WITHOUT_MOBILE = ["backend", "frontend", "data-ai"];

const expectedJobsByCompany: Record<string, string[]> = {
  "CJ올리브영": ALL_ROLES,
  GS리테일: ALL_ROLES,
  "kt cloud": ALL_ROLES,
  "LG AI연구원": WITHOUT_MOBILE,
  "NHN Cloud": ALL_ROLES,
  SK플래닛: WITHOUT_MOBILE,
  가비아: WITHOUT_MOBILE,
  네이버: ALL_ROLES,
  넥스트리: ALL_ROLES,
  "농심데이터시스템(NDS)": WITHOUT_MOBILE,
  "당근마켓 / 당근": ALL_ROLES,
  라인플러스: ALL_ROLES,
  "라포랩스 / 퀸": WITHOUT_MOBILE,
  마이리얼트립: ALL_ROLES,
  메가존클라우드: WITHOUT_MOBILE,
  버즈빌: WITHOUT_MOBILE,
  "비바리퍼블리카 / 토스": ALL_ROLES,
  삼성: ALL_ROLES,
  삼성반도체: ["backend", "mobile", "data-ai"],
  쏘카: WITHOUT_MOBILE,
  아임웹: WITHOUT_MOBILE,
  안랩클라우드메이트: ["backend", "data-ai"],
  어피닛: ALL_ROLES,
  업스테이지: ["data-ai"],
  여기어때: ALL_ROLES,
  "우아한형제들 / 배달의민족": ALL_ROLES,
  "인프랩 / 인프런": WITHOUT_MOBILE,
  "채널코퍼레이션 / 채널톡": ALL_ROLES,
  카카오: ALL_ROLES,
  "카카오엔터프라이즈 / 카카오클라우드": ["backend", "data-ai"],
  컬리: WITHOUT_MOBILE,
  컴투스: ALL_ROLES,
  한컴: WITHOUT_MOBILE,
};

describe("companies fixture index", () => {
  it("contains the exact PR 96 + PR 100 company-role scope", () => {
    const actualJobsByCompany = Object.fromEntries(
      index.companies.map((company) => [
        company.name,
        (company.jobs ?? []).map((job) => job.slug),
      ]),
    );

    expect(actualJobsByCompany).toEqual(expectedJobsByCompany);
    expect(index.companies).toHaveLength(33);
    expect(
      index.companies.reduce(
        (total, company) => total + (company.jobs?.length ?? 0),
        0,
      ),
    ).toBe(112);
  });

  it("keeps the final per-role totals and evidence threshold", () => {
    const counts = Object.fromEntries(
      ALL_ROLES.map((role) => [
        role,
        index.companies.filter((company) =>
          company.jobs?.some((job) => job.slug === role),
        ).length,
      ]),
    );

    expect(counts).toEqual({
      backend: 32,
      frontend: 29,
      mobile: 18,
      "data-ai": 33,
    });
    expect(index.threshold).toBe(4);
    expect(index.pairCount).toBe(112);
    expect(index.sourcePullRequests).toEqual([96, 100]);
    expect(index.companies.some((company) => company.name === "구름")).toBe(
      false,
    );

    for (const company of index.companies) {
      expect(company.jobs?.length).toBeGreaterThan(0);
      for (const job of company.jobs ?? []) {
        expect(job.evidenceCount).toBeGreaterThanOrEqual(index.threshold ?? 4);
        expect(job.evidenceCount).toBeLessThanOrEqual(
          company.evidenceCount ?? Number.POSITIVE_INFINITY,
        );
      }
    }
  });

  it("uses unique company names and URL slugs", () => {
    expect(new Set(index.companies.map((company) => company.name)).size).toBe(
      index.companies.length,
    );
    expect(new Set(index.companies.map((company) => company.slug)).size).toBe(
      index.companies.length,
    );
  });
});
