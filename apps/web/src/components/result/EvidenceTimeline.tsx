"use client";

import { useState } from "react";
import type { Evidence } from "@/types/data";
import {
  BriefcaseIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentIcon,
  ExternalIcon,
} from "@/components/ui/icons";

const SOURCE = {
  blog: { label: "기술 블로그", Icon: DocumentIcon, tone: "bg-accent-tint text-accent" },
  job: {
    label: "채용 공고",
    Icon: BriefcaseIcon,
    tone: "bg-stage-fit-tint text-stage-fit",
  },
} as const;

/**
 * 근거 타임라인. 기본은 접혀 있고, 펼치면 시간 역순으로 보입니다.
 *
 * 제목·연월·출처·원문 링크까지만 보여줍니다. 본문은 싣지 않습니다 — 저작권
 * 문제이기도 하고, 원문을 직접 열어 확인하게 하는 것이 이 화면의 목적입니다.
 */
export function EvidenceTimeline({ evidence }: { evidence: Evidence[] }) {
  const [open, setOpen] = useState(false);
  const sorted = [...evidence].sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));

  return (
    <div className="flex flex-col rounded-card border border-line bg-surface">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="flex min-h-11 cursor-pointer items-center justify-between gap-3 p-4 text-left sm:px-[22px]"
      >
        <span className="text-[0.9375rem] leading-[1.6] font-medium">
          {open ? "접기" : "펼쳐서 근거 문서 확인"} ({evidence.length}건)
        </span>
        {open ? (
          <ChevronUpIcon size={18} className="shrink-0 text-ink-soft" />
        ) : (
          <ChevronDownIcon size={18} className="shrink-0 text-ink-soft" />
        )}
      </button>

      {open && (
        <div className="flex flex-col gap-1 border-t border-line p-3 sm:p-4">
          {sorted.map((e) => {
            const { label, Icon, tone } = SOURCE[e.source] ?? SOURCE.blog;
            return (
              <a
                key={e.id}
                href={e.url}
                target="_blank"
                rel="noreferrer"
                className="group flex items-start gap-3 rounded-card p-3 no-underline transition-colors hover:bg-sunken hover:no-underline"
              >
                <span
                  aria-hidden="true"
                  className={`flex size-8 shrink-0 items-center justify-center rounded-card ${tone}`}
                >
                  <Icon size={16} strokeWidth={1.6} />
                </span>
                <span className="flex min-w-0 grow flex-col gap-0.5">
                  <span className="text-[0.90625rem] leading-[1.6] text-ink group-hover:text-accent">
                    {e.title}
                  </span>
                  <span className="text-[0.8125rem] leading-[1.7] text-ink-muted">
                    {e.publishedAt.slice(0, 7)} · {label}
                  </span>
                </span>
                <ExternalIcon
                  size={15}
                  strokeWidth={1.5}
                  className="mt-1 shrink-0 text-ink-muted opacity-0 transition-opacity group-hover:opacity-100"
                />
              </a>
            );
          })}
          <p className="px-3 pt-2 text-[0.8125rem] leading-[1.7] text-ink-muted">
            본문은 싣지 않습니다. 제목과 발행일, 원문 링크까지만 보여드립니다.
          </p>
        </div>
      )}
    </div>
  );
}
