"use client";

import { useState } from "react";
import type { Evidence } from "@/types/data";
import { ChevronDownIcon, ChevronUpIcon, ExternalIcon } from "@/components/ui/icons";

const SOURCE_LABEL: Record<string, string> = { blog: "기술 블로그", job: "채용 공고" };
const SOURCE_COLOR: Record<string, string> = {
  blog: "text-src-blog",
  job: "text-src-job",
};

/**
 * 근거 타임라인. 기본은 접혀 있고, 펼치면 시간 역순으로 보입니다.
 *
 * 제목·연월·출처·원문 링크까지만 보여줍니다. 본문은 싣지 않습니다 — 저작권
 * 문제이기도 하고, 원문을 직접 열어 확인하게 하는 것이 이 화면의 목적입니다.
 */
export function EvidenceTimeline({ evidence }: { evidence: Evidence[] }) {
  const [open, setOpen] = useState(false);

  const sorted = [...evidence].sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
  const newest = sorted[0]?.publishedAt.slice(0, 7).replace("-", ".");
  const oldest = sorted.at(-1)?.publishedAt.slice(0, 7).replace("-", ".");

  return (
    <div className="flex flex-col rounded-card border border-line bg-surface">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="flex min-h-11 cursor-pointer items-center justify-between gap-3 p-4 text-left sm:px-[22px]"
      >
        <span className="flex flex-wrap items-baseline gap-3">
          <span className="text-[0.9375rem] leading-[1.6] font-medium">
            근거 {evidence.length}건
          </span>
          <span className="font-mono text-[0.71875rem] text-ink-soft">
            {oldest} – {newest}
          </span>
          {!open && (
            <span className="text-[0.8125rem] leading-[1.7] text-ink-muted">
              펼쳐서 원문 보기
            </span>
          )}
        </span>
        {open ? (
          <ChevronUpIcon size={18} className="shrink-0 text-ink-soft" />
        ) : (
          <ChevronDownIcon size={18} className="shrink-0 text-ink-soft" />
        )}
      </button>

      {open && (
        <div className="flex flex-col border-t border-line">
          {sorted.map((e) => (
            <div
              key={e.id}
              className="flex flex-col gap-1.5 border-b border-sunken px-4 py-3.5 sm:flex-row sm:gap-[18px] sm:px-[22px]"
            >
              <span className="shrink-0 font-mono text-[0.71875rem] leading-[1.9] text-ink-soft sm:w-16">
                {e.publishedAt.slice(0, 7).replace("-", ".")}
              </span>
              <a
                href={e.url}
                target="_blank"
                rel="noreferrer"
                className="flex grow items-start gap-2 text-[0.90625rem] leading-[1.7]"
              >
                {e.title}
                <ExternalIcon
                  size={15}
                  strokeWidth={1.5}
                  className="mt-1 shrink-0 text-ink-muted"
                />
              </a>
              <span
                className={`shrink-0 font-mono text-[0.71875rem] leading-[1.9] ${SOURCE_COLOR[e.source] ?? "text-ink-soft"}`}
              >
                {SOURCE_LABEL[e.source] ?? e.source}
              </span>
            </div>
          ))}
          <p className="px-4 py-3.5 text-[0.8125rem] leading-[1.7] text-ink-muted sm:px-[22px]">
            본문은 싣지 않습니다. 제목과 발행일, 원문 링크까지만 보여드립니다.
          </p>
        </div>
      )}
    </div>
  );
}
