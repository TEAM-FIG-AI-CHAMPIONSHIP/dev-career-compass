import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost";

/**
 * 높이 44px는 손가락 최소 히트 영역입니다. 줄이지 마세요.
 * 선택 상태는 잉크색 채움 하나로만 표시합니다 — 악센트는 기본 동작에만 씁니다.
 */
const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-accent border-accent text-white hover:bg-accent-ink hover:border-accent-ink",
  secondary:
    "bg-surface border-line-strong text-ink hover:border-ink-muted",
  ghost:
    "bg-transparent border-transparent text-ink-soft hover:text-ink hover:bg-sunken",
};

export function Button({
  variant = "secondary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={cn(
        "inline-flex min-h-11 cursor-pointer items-center justify-center gap-2",
        "rounded-btn border px-5 py-3 text-[0.875rem] leading-none font-medium",
        "transition-colors",
        "disabled:cursor-default disabled:border-line disabled:bg-sunken disabled:text-ink-muted",
        VARIANTS[variant],
        className,
      )}
      {...props}
    />
  );
}

/**
 * S1에서 회사를 누르면 인라인으로 펼쳐지는 직무 버튼.
 * selected는 잉크색 채움으로만 구분합니다.
 */
export function JobButton({
  selected = false,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { selected?: boolean }) {
  return (
    <button
      aria-pressed={selected}
      className={cn(
        "inline-flex min-h-11 cursor-pointer items-center justify-center",
        "rounded-btn border px-4 py-3 text-[0.875rem] leading-none",
        "transition-colors",
        selected
          ? "border-ink bg-ink text-paper"
          : "border-line-strong bg-surface text-ink hover:border-ink hover:bg-ink hover:text-paper",
        className,
      )}
      {...props}
    />
  );
}
