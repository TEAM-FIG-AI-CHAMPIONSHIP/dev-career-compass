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
