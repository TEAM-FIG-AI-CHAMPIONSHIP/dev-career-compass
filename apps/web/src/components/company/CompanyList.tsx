"use client";

import { useState } from "react";
import type { Company } from "@/types/data";
import { CompanyMark } from "./CompanyMark";
import {
  ArrowRightIcon,
  BuildingIcon,
  SearchIcon,
} from "@/components/ui/icons";
import { Button, ButtonLink } from "@/components/ui/Button";
import { cardStyle } from "@/components/ui/Card";
import { cn } from "@/lib/cn";
import { routes } from "@/lib/routes";

const COMPANIES_PER_PAGE = 12;

function filterCompanies(companies: Company[], query: string) {
  const normalizedQuery = query.trim().toLocaleLowerCase("ko-KR");
  return normalizedQuery
    ? companies.filter((company) =>
        company.name.toLocaleLowerCase("ko-KR").includes(normalizedQuery),
      )
    : companies;
}

/**
 * S1 회사 목록. 한 페이지에 12곳을 보여주고, 선택한 회사의 직무를 옆에 펼칩니다.
 * 회사 이름은 코드에 없습니다 — 전부 data/index.json 에서 옵니다.
 */
export function CompanyList({ companies }: { companies: Company[] }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCompanies = filterCompanies(companies, searchQuery);
  const totalPages = Math.max(
    1,
    Math.ceil(filteredCompanies.length / COMPANIES_PER_PAGE),
  );
  const pageStart = currentPage * COMPANIES_PER_PAGE;
  const pageCompanies = filteredCompanies.slice(
    pageStart,
    pageStart + COMPANIES_PER_PAGE,
  );
  const selectedCompany = companies.find(
    (company) => company.slug === selectedSlug,
  );

  function goToPage(page: number) {
    const nextPage = Math.min(Math.max(page, 0), totalPages - 1);
    const nextStart = nextPage * COMPANIES_PER_PAGE;
    const nextPageCompanies = filteredCompanies.slice(
      nextStart,
      nextStart + COMPANIES_PER_PAGE,
    );

    if (
      selectedSlug &&
      !nextPageCompanies.some((company) => company.slug === selectedSlug)
    ) {
      setSelectedSlug(null);
    }
    setCurrentPage(nextPage);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem] lg:gap-8">
      <section
        aria-labelledby="company-list-title"
        className="flex min-w-0 flex-col gap-4"
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2
              id="company-list-title"
              className="text-h2 font-semibold text-balance"
            >
              회사 선택
            </h2>
            <p className="mt-1 font-mono text-meta text-ink-muted tabular-nums">
              {filteredCompanies.length}곳
            </p>
          </div>

          <label className="relative block w-full sm:max-w-64">
            <span className="sr-only">회사명 검색</span>
            <SearchIcon
              size={17}
              className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-ink-muted"
            />
            <input
              type="search"
              value={searchQuery}
              onChange={(event) => {
                const nextQuery = event.target.value;
                const nextPageCompanies = filterCompanies(
                  companies,
                  nextQuery,
                ).slice(0, COMPANIES_PER_PAGE);

                setSearchQuery(nextQuery);
                setCurrentPage(0);
                if (
                  selectedSlug &&
                  !nextPageCompanies.some(
                    (company) => company.slug === selectedSlug,
                  )
                ) {
                  setSelectedSlug(null);
                }
              }}
              placeholder="회사명 검색"
              className="min-h-11 w-full rounded-btn border border-line-strong bg-sunken py-2.5 pr-3.5 pl-10 text-body-sm text-ink outline-none transition-colors duration-150 placeholder:text-ink-muted hover:border-ink-muted focus:border-accent"
            />
          </label>
        </div>

        {pageCompanies.length > 0 ? (
          <ul
            className="grid grid-cols-1 content-start gap-3 sm:grid-cols-2 lg:min-h-[39.125rem] xl:min-h-[25.875rem] xl:grid-cols-3"
            aria-label="회사 목록"
          >
            {pageCompanies.map((company) => {
              const isSelected = selectedSlug === company.slug;
              const jobCount = company.jobs?.length ?? 0;

              return (
                <li key={company.slug} className="flex">
                  <button
                    type="button"
                    aria-pressed={isSelected}
                    aria-controls="selected-company-jobs"
                    onClick={() => setSelectedSlug(company.slug)}
                    className={cardStyle("action", {
                      selected: isSelected,
                      className:
                        "flex min-h-24 w-full cursor-pointer items-center gap-3 p-4 text-left",
                    })}
                  >
                    <CompanyMark
                      name={company.name}
                      logoSrc={company.logoSrc}
                      mark={company.mark}
                    />

                    <span className="min-w-0">
                      <span className="block truncate text-h3 font-semibold">
                        {company.name}
                      </span>
                      <span className="mt-0.5 block font-mono text-meta text-ink-muted tabular-nums">
                        {jobCount}개 직무
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        ) : (
          <div
            className={cardStyle("empty", {
              className:
                "flex min-h-64 flex-col items-center justify-center p-6 text-center",
            })}
          >
            <h3 className="text-h3 font-semibold text-balance">
              검색 결과가 없습니다
            </h3>
            <p className="mt-1.5 text-body-sm text-pretty text-ink-soft">
              다른 회사명으로 다시 검색해보세요.
            </p>
            <Button
              onClick={() => {
                setSearchQuery("");
                setCurrentPage(0);
              }}
              className="mt-4"
            >
              검색 초기화
            </Button>
          </div>
        )}

        {totalPages > 1 && (
          <nav
            aria-label="회사 목록 페이지"
            className="flex items-center justify-between border-t border-line pt-3"
          >
            <p className="font-mono text-meta text-ink-muted tabular-nums">
              {pageStart + 1}–
              {Math.min(
                pageStart + COMPANIES_PER_PAGE,
                filteredCompanies.length,
              )}{" "}
              / {filteredCompanies.length}
            </p>
            {/* 이전·다음 화살표를 조건부로 없애지 않고 늘 자리를 차지하게
                둡니다. 첫 페이지에서 이전 화살표가 없다가 두 번째 페이지로
                가는 순간 나타나면, 그 한 칸만큼 숫자 버튼 전체가 오른쪽으로
                밀립니다 — 페이지를 넘기는 동작인데 화면이 그보다 크게
                움직여서 지금 어디로 이동했는지 혼란스럽습니다. 경계에서는
                비활성화만 합니다(Button 컴포넌트의 disabled: 규칙과 같은
                방식). */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                aria-label="이전 페이지"
                disabled={currentPage === 0}
                onClick={() => goToPage(currentPage - 1)}
                className="inline-flex size-11 items-center justify-center rounded-btn border border-line-strong bg-surface text-ink transition-colors duration-150 hover:border-accent hover:text-accent disabled:cursor-default disabled:border-line disabled:bg-sunken disabled:text-ink-muted disabled:hover:border-line disabled:hover:text-ink-muted"
              >
                <ArrowRightIcon size={16} className="rotate-180" />
              </button>

              {Array.from({ length: totalPages }, (_, page) => (
                <button
                  key={page}
                  type="button"
                  aria-label={`${page + 1}페이지`}
                  aria-current={page === currentPage ? "page" : undefined}
                  onClick={() => goToPage(page)}
                  className={cn(
                    "inline-flex size-11 items-center justify-center rounded-btn border font-mono text-meta tabular-nums transition-colors duration-150",
                    page === currentPage
                      ? "border-accent bg-accent text-accent-on"
                      : "border-line-strong bg-surface text-ink-soft hover:border-accent hover:text-accent",
                  )}
                >
                  {page + 1}
                </button>
              ))}

              <button
                type="button"
                aria-label="다음 페이지"
                disabled={currentPage === totalPages - 1}
                onClick={() => goToPage(currentPage + 1)}
                className="inline-flex size-11 items-center justify-center rounded-btn border border-line-strong bg-surface text-ink transition-colors duration-150 hover:border-accent hover:text-accent disabled:cursor-default disabled:border-line disabled:bg-sunken disabled:text-ink-muted disabled:hover:border-line disabled:hover:text-ink-muted"
              >
                <ArrowRightIcon size={16} />
              </button>
            </div>
          </nav>
        )}
      </section>

      <aside
        id="selected-company-jobs"
        aria-labelledby="selected-company-title"
        aria-live="polite"
        className="flex h-full flex-col rounded-card border border-line-strong bg-sunken p-5 lg:p-6"
      >
        {selectedCompany ? (
          <>
            <p className="font-mono text-meta text-accent">$ selected</p>
            <div className="mt-3 flex items-center gap-3 border-b border-line pb-5">
              <CompanyMark
                name={selectedCompany.name}
                logoSrc={selectedCompany.logoSrc}
                mark={selectedCompany.mark}
                size="md"
              />
              <div className="min-w-0">
                <h2
                  id="selected-company-title"
                  className="truncate text-h2 font-semibold"
                >
                  {selectedCompany.name}
                </h2>
                <p className="mt-0.5 font-mono text-meta text-ink-muted tabular-nums">
                  {selectedCompany.jobs?.length ?? 0}개 직무
                </p>
              </div>
            </div>

            <div className="mt-5">
              <h3 className="text-h3 font-semibold text-balance">
                어떤 직무로 볼까요?
              </h3>
              <p className="mt-1 text-body-sm text-pretty text-ink-soft">
                {selectedCompany.status === "published"
                  ? "확인할 직무를 선택하세요."
                  : "현재 분석을 준비하고 있는 회사입니다."}
              </p>
            </div>

            <div className="mt-4 flex flex-col gap-2">
              {(selectedCompany.jobs ?? []).map((job) =>
                selectedCompany.status === "published" ? (
                  <ButtonLink
                    key={job.slug}
                    href={routes.companyResult(selectedCompany.slug, job.slug)}
                    className="justify-between"
                  >
                    <span>{job.name}</span>
                    <ArrowRightIcon size={17} className="shrink-0" />
                  </ButtonLink>
                ) : (
                  <span
                    key={job.slug}
                    aria-disabled="true"
                    className="inline-flex min-h-11 cursor-not-allowed items-center justify-between gap-2 rounded-btn border border-dashed border-line-strong bg-sunken px-5 py-3 text-body-sm leading-none font-medium text-ink-muted"
                  >
                    <span>{job.name}</span>
                    <span className="shrink-0 font-mono text-meta text-ink-muted">
                      준비 중
                    </span>
                  </span>
                ),
              )}
            </div>
          </>
        ) : (
          <div className="flex grow flex-col items-center justify-center px-2 py-10 text-center">
            <span
              aria-hidden="true"
              className="flex size-12 items-center justify-center rounded-card bg-accent-tint text-accent"
            >
              <BuildingIcon size={24} />
            </span>
            <h2
              id="selected-company-title"
              className="mt-4 text-h3 font-semibold text-balance"
            >
              회사를 선택하세요
            </h2>
            <p className="mt-1.5 max-w-56 break-keep text-body-sm text-pretty text-ink-soft">
              왼쪽 회사 목록에서 관심 있는 회사를 고르면 직무를 확인할 수
              있습니다.
            </p>
          </div>
        )}
      </aside>
    </div>
  );
}
