import type { Metadata } from "next";
import Link from "next/link";
import { getCompanyIndex, dataSource } from "@/lib/data";
import { CompanyList } from "@/components/company/CompanyList";
import { DataSourceNote, PageHeader } from "@/components/ui/PageHeader";
import { routes } from "@/lib/routes";

export const metadata: Metadata = { title: "회사 선택" };

/** S1 회사 선택 — 회사를 고르면 그 자리에서 직무가 펼쳐집니다. */
export default function CompaniesPage() {
  const index = getCompanyIndex();
  const source = dataSource();

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="here" className="text-[0.875rem] leading-[1.6] text-ink">
            회사 선택
          </span>,
        ]}
        right={
          <span className="font-mono text-meta text-ink-muted">
            최근 12개월 수집분
          </span>
        }
      />

      <main className="flex grow flex-col">
        <div className="flex max-w-4xl flex-col gap-4 px-4 pt-12 pb-10 sm:px-8 lg:px-20 lg:pt-16">
          <h1 className="text-[1.75rem] leading-[1.35] font-semibold tracking-[-0.015em] text-pretty sm:text-[2.375rem]">
            관심 있는 회사를 고르세요
          </h1>
          <p className="max-w-2xl text-body text-ink-soft sm:text-base sm:leading-[1.8]">
            회사와 직무를 고르면 그 조직이 반복해서 다루는 문제와, 지금 만들 다음
            프로젝트를 근거와 함께 확인할 수 있습니다.
          </p>
        </div>

        <section className="flex flex-col gap-4 px-4 sm:px-8 lg:px-20">
          <div className="flex items-baseline justify-between border-b border-ink pb-2.5">
            <h2 className="text-h3 font-semibold sm:text-[1.0625rem]">회사 목록</h2>
            <span className="font-mono text-[0.71875rem] text-ink-soft">
              {index.companies.length}곳
            </span>
          </div>
          <CompanyList companies={index.companies} />
        </section>

        <section className="px-4 py-10 sm:px-8 lg:px-20 lg:py-16">
          <div className="flex flex-col items-start justify-between gap-5 rounded-card border border-line-strong bg-surface p-[26px] sm:flex-row sm:items-center">
            <div className="flex flex-col gap-1.5">
              <p className="text-[1.03125rem] leading-[1.55] font-semibold">
                회사부터 정하기 어렵다면, 내가 만든 것부터 보여주세요
              </p>
              <p className="max-w-2xl text-[0.875rem] leading-[1.75] text-ink-soft">
                직무 하나만 고르고 지금까지 해본 것을 체크하면, 어느 조직이 지금의
                경험과 가까운지 되짚어 드립니다.
              </p>
            </div>
            <Link
              href={routes.match}
              className="inline-flex min-h-11 shrink-0 items-center rounded-btn border border-accent bg-accent px-5 py-3 text-[0.875rem] leading-none font-medium text-white no-underline transition-colors hover:border-accent-ink hover:bg-accent-ink hover:no-underline"
            >
              내 경험부터 보기
            </Link>
          </div>
        </section>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={source} />
        <div className="border-t border-line px-4 py-4 sm:px-8 lg:px-20">
          <p className="text-caption text-ink-muted">
            수집한 글의 본문은 저장하거나 다시 싣지 않습니다. 제목과 발행일, 원문
            링크만 보여드립니다.
          </p>
        </div>
      </footer>
    </>
  );
}
