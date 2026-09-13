import type { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost";

/**
 * 버튼은 이 파일에서만 만듭니다. 화면마다 손으로 만들면 높이와 글자 크기가
 * 조금씩 어긋나 같은 줄에 선 버튼들이 따로 놉니다.
 *
 * 높이 44px 는 손가락 최소 히트 영역입니다. 줄이지 마세요. 크기를 화면에서
 * 덮어쓰지 않습니다 — 크기가 달라야 할 이유가 생기면 여기에 변형을 추가합니다.
 */
const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-accent border-accent text-white hover:bg-accent-ink hover:border-accent-ink",
  secondary:
    "bg-surface border-line-strong text-ink hover:border-accent hover:text-accent",
  ghost:
    "bg-transparent border-transparent text-ink-soft hover:text-accent hover:bg-accent-tint",
};

const BASE = [
  "inline-flex min-h-11 cursor-pointer items-center justify-center gap-2",
  "rounded-btn border px-5 py-3 text-[0.875rem] leading-none font-medium",
  "transition-colors no-underline hover:no-underline",
  "disabled:cursor-default disabled:border-line disabled:bg-sunken disabled:text-ink-muted",
].join(" ");

export function Button({
  variant = "secondary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button className={cn(BASE, VARIANTS[variant], className)} {...props} />
  );
}

/** 눌러서 다른 화면으로 가는 것. 생김새는 Button 과 같습니다. */
export function ButtonLink({
  variant = "secondary",
  className,
  href,
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & {
  variant?: Variant;
  href: string;
}) {
  return (
    <Link
      href={href}
      className={cn(BASE, VARIANTS[variant], className)}
      {...props}
    />
  );
}
