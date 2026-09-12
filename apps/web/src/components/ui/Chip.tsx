import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

type Tone = "neutral" | "ink" | "accent";

const TONES: Record<Tone, string> = {
  neutral: "border-line-strong bg-surface text-ink",
  ink: "border-ink bg-ink text-paper",
  accent: "border-accent bg-accent-tint text-accent",
};

/** 알약 모양 기본 요소. 영역 칩과 3단계 배지가 이걸 씁니다. */
export function Chip({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2.5 rounded-pill border px-4 py-2",
        "text-[0.875rem] leading-normal font-medium",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

/** 뉴스는 MVP 범위에서 제외했습니다. 소스를 붙이면 "news" 를 되살립니다. */
export type EvidenceSource = "blog" | "job";

const SOURCE_LABEL: Record<EvidenceSource, string> = {
  blog: "블로그",
  job: "공고",
};

const SOURCE_COLOR: Record<EvidenceSource, string> = {
  blog: "text-src-blog",
  job: "text-src-job",
};

/**
 * 근거 건수 배지 — "블로그 5" 처럼 씁니다.
 * 색은 늘 글자 라벨과 함께 갑니다. 색만으로 출처를 구분하지 않습니다.
 */
export function EvidenceCount({
  source,
  count,
}: {
  source: EvidenceSource;
  count: number;
}) {
  return (
    <span
      className={cn(
        "flex items-center gap-1.5 font-mono text-[0.71875rem]",
        SOURCE_COLOR[source],
      )}
    >
      <span className="size-1.5 rounded-pill bg-current" aria-hidden="true" />
      {SOURCE_LABEL[source]} {count}
    </span>
  );
}
