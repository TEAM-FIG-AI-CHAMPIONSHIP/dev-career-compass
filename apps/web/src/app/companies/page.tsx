import type { Metadata } from "next";
import { getCompanyIndex } from "@/lib/data";
import { CompanyList } from "@/components/company/CompanyList";
import { AppHeader } from "@/components/ui/AppHeader";
import { PageWidth } from "@/components/ui/PageWidth";

export const metadata: Metadata = {
  title: { absolute: "회사·직무 탐색 | Refactor.me" },
};

/** S1 회사 선택 — 회사를 고르면 그 자리에서 직무가 펼쳐집니다. */
export default function CompaniesPage() {
  const index = getCompanyIndex();

  return (
    <>
      <AppHeader />

      <main className="grow pb-16">
        <PageWidth>
          <header className="flex flex-col gap-3 pt-10 pb-8 lg:pt-12 lg:pb-10">
            <h1 className="text-display font-semibold text-balance sm:text-[2.125rem]">
              회사와 직무를 선택하세요
            </h1>
            <p className="text-body text-pretty text-ink-soft sm:text-base sm:leading-[1.8] lg:whitespace-nowrap">
              회사와 직무를 고르면 그 조직이 반복해서 다루는 문제와, 지금 만들
              다음 프로젝트를 근거와 함께 확인할 수 있습니다.
            </p>
          </header>

          <CompanyList companies={index.companies} />
        </PageWidth>
      </main>
    </>
  );
}
