import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * 태그 한 종류.
 *
 * 영역 이름, 출처, 고른 경험, 저장소 키워드가 모두 이 모양을 씁니다. 전에는
 * 영역이 농도 네 단계, 배지가 색 세 개로 서로 다른 체계였는데, 영역이
 * 무엇인지는 옆에 적힌 이름이 이미 말하고 있어 농도는 같은 정보를 한 번 더
 * 칠한 것이었습니다.
 *
 * **이 제품의 칩은 모두 이름표입니다.** 누를 수 있는 칩은 없습니다 — 고르는
 * 일은 `CheckboxCard` 와 `RadioCard` 가 맡습니다. 그래서 칩은 "누를 수 있게"
 * 보일 필요가 없고, 대신 **읽히기만 하면 됩니다**.
 *
 * 그래서 테두리로 형태를 만들지 않고 바탕 한 톤으로 만듭니다. 진한 테두리는
 * 조작할 수 있다는 약속이라 이름표에 붙이면 거짓말이 되고, 흐린 테두리는
 * 바탕과 같은 색 위에서 그냥 사라집니다.
 */
type Tone = "neutral" | "selected" | "accent";

const TONES: Record<Tone, string> = {
  /* 이름표. 바탕은 칩 전용 한 톤입니다 — 창 위에서도 바탕 위에서도 파인 칸
     위에서도 한 단계 떠 보입니다. 흰색·검은색을 쓰면 놓인 면에 묻힙니다. */
  neutral: "bg-chip text-ink",
  /* 고른 것. 아직 쓰는 곳은 없지만, 칩이 고를 수 있게 되는 날의 짝입니다 —
     그때 안 고른 것은 neutral 이 아니라 테두리만 있는 모양이어야 합니다. */
  selected: "border border-accent bg-accent-tint text-ink",
  /* 강조 표시 — 저장소에서 찾은 키워드, 신입 공고 요구 등. */
  accent: "border border-accent-line bg-accent-tint text-accent",
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
        "inline-flex items-center gap-2 rounded-pill px-2.5 py-1",
        "text-caption leading-normal",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

/**
 * 칩 안의 숫자. 자릿수가 늘어도 칩 높이가 흔들리지 않게 고정폭을 씁니다.
 *
 * 이름보다 한 단계 조용하되 읽히는 선까지만 낮춥니다 — 칩 바탕 위에서
 * `ink-muted` 는 대비가 3:1 언저리라 작은 글자로는 읽기 어렵습니다.
 */
export function ChipCount({ children }: { children: ReactNode }) {
  return (
    <span className="font-mono text-meta tracking-normal text-ink-soft tabular-nums">
      {children}
    </span>
  );
}
