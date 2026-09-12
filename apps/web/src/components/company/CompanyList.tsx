"use client";

import { useState } from "react";
import Link from "next/link";
import type { Company } from "@/types/data";
import { ChevronDownIcon, ChevronUpIcon } from "@/components/ui/icons";
import { cn } from "@/lib/cn";

/**
 * S1 회사 목록. 회사를 누르면 페이지 이동 없이 그 자리에서 직무가 펼쳐집니다.
 * 회사 이름은 코드에 없습니다 — 전부 data/index.json 에서 옵니다.
 */
export function CompanyList({ companies }: { companies: Company[] }) {
  const [openSlug, setOpenSlug] = useState<string | null>(
    companies.find((c) => c.status === "published")?.slug ?? null,
  );

  return (
    <div className="flex flex-col gap-2">
      {companies.map((company) => {
        const isCollecting = company.status === "collecting";
        const isOpen = !isCollecting && openSlug === company.slug;

        return (
          <div
            key={company.slug}
            className={cn(
              "flex flex-col rounded-card border transition-colors",
              isCollecting
                ? "border-dashed border-line-strong bg-paper opacity-70"
                : isOpen
                  ? "border-ink bg-surface"
                  : "border-line bg-paper hover:border-ink-muted hover:bg-surface",
            )}
          >
            <button
              type="button"
              disabled={isCollecting}
              aria-expanded={isCollecting ? undefined : isOpen}
              onClick={() => setOpenSlug(isOpen ? null : company.slug)}
              className={cn(
                "flex min-h-11 items-center gap-4 p-4 text-left sm:gap-[18px] sm:px-[22px]",
                isCollecting ? "cursor-default" : "cursor-pointer",
              )}
            >
              <span
                aria-hidden="true"
                className="flex size-8 shrink-0 items-center justify-center rounded-card border border-line bg-sunken text-[0.84375rem] font-semibold text-ink-soft"
              >
                {company.mark ?? ""}
              </span>
              <span
                className={cn(
                  "shrink-0 text-[1.03125rem] leading-[1.5] font-semibold sm:w-32",
                  isCollecting && "text-ink-muted",
                )}
              >
                {company.name}
              </span>
              <span className="hidden grow text-[0.875rem] leading-[1.7] text-ink-soft sm:block">
                {company.summary ?? "근거가 모이면 공개합니다"}
              </span>
              <span className="ml-auto shrink-0 font-mono text-meta text-ink-muted">
                {isCollecting
                  ? "수집 중"
                  : `직무 ${company.jobs?.length ?? 0} · 근거 ${company.evidenceCount ?? 0}건`}
              </span>
              {!isCollecting &&
                (isOpen ? (
                  <ChevronUpIcon size={18} className="shrink-0 text-ink" />
                ) : (
                  <ChevronDownIcon size={18} className="shrink-0 text-ink-muted" />
                ))}
            </button>

            {isOpen && (
              <div className="flex flex-wrap items-center gap-2.5 border-t border-line bg-surface p-4 sm:px-[22px] sm:pb-5">
                <span className="mr-1 text-body-sm text-ink-soft">
                  어떤 직무로 볼까요?
                </span>
                {(company.jobs ?? []).map((job) => (
                  <Link
                    key={job.slug}
                    href={`/${company.slug}/${job.slug}`}
                    className="inline-flex min-h-11 items-center rounded-btn border border-line-strong bg-surface px-4 py-3 text-[0.875rem] leading-none text-ink no-underline transition-colors hover:border-ink hover:bg-ink hover:text-paper hover:no-underline"
                  >
                    {job.name}
                  </Link>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
