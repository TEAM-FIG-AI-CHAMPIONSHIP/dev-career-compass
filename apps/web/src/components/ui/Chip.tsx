import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * 태그 한 종류.
 *
 * 영역 이름, 출처, 고른 경험, 3단계 배지가 모두 이 모양을 씁니다. 전에는
 * 영역이 농도 네 단계, 배지가 색 세 개로 서로 다른 체계였는데, 영역이
 * 무엇인지는 옆에 적힌 이름이 이미 말하고 있어 농도는 같은 정보를 한 번 더
 * 칠한 것이었습니다.
 *
 * 규칙은 하나입니다 — 상태가 있는 것만 색을 받습니다. 이름표는 색이 없습니다.
 */
type Tone = "neutral" | "selected" | "accent";

const TONES: Record<Tone, string> = {
  /* 이름표. 고를 수 있는 것이든 아니든 바탕은 창과 같은 흰색입니다 —
     회색 바탕을 깔면 눌리지 않게 막아 둔 것처럼 보입니다. */
  neutral: "border-line-strong bg-surface text-ink",
  /* 고른 것. 글자색은 그대로 두어 목록이 계속 읽힙니다. */
  selected: "border-accent bg-accent-tint text-ink",
  accent: "border-accent-line bg-accent-tint text-accent",
};

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
        "inline-flex items-center gap-2 rounded-pill border px-2.5 py-1",
        "text-caption leading-normal",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

/** 칩 안의 숫자. 자릿수가 늘어도 칩 높이가 흔들리지 않게 고정폭을 씁니다. */
export function ChipCount({ children }: { children: ReactNode }) {
  return (
    <span className="font-mono text-meta tracking-normal text-ink-muted tabular-nums">
      {children}
    </span>
  );
}
