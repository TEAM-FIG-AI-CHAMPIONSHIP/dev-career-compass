import type { AnchorHTMLAttributes, HTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";

/**
 * 카드는 네 종류뿐입니다. 새 카드를 손으로 조립하지 말고 여기서 고르세요.
 *
 *  static  읽기만 하는 정보        흰 바탕 · 테두리 · hover 없음
 *  action  눌러서 가거나 고르는 것  hover·선택 시 악센트
 *  cta     지금 하면 좋은 한 가지   악센트 바탕. 한 화면에 하나만
 *  empty   아직 없는 것            점선 · 흐린 글자
 *
 * hover 는 "누를 수 있다"는 약속입니다. 눌리지 않는 카드에 hover 를 주면
 * 눌러 보다가 아무 일도 일어나지 않습니다 — static 에 hover 가 없는 이유입니다.
 */
export type CardVariant = "static" | "action" | "cta" | "empty";

const BASE = "rounded-card border";

const VARIANTS: Record<CardVariant, string> = {
  static: "border-line-strong bg-surface",
  action: "border-line-strong bg-surface transition-colors hover:border-accent",
  cta: "border-accent bg-accent-tint transition-colors hover:border-accent-ink",
  /* 아직 없는 것. 바탕을 파 두면 "여기 무언가 들어올 자리" 로 읽힙니다. */
  empty: "border-dashed border-line-strong bg-sunken",
};

/**
 * 고른 상태는 테두리에 더해 배경까지 강조색입니다. hover 가 테두리만 바꾸는
 * 이유가 여기 있습니다 — 둘이 같으면 방금 누른 카드 위에 커서가 있는 동안
 * 골랐는지 아닌지 구분되지 않습니다.
 *
 * action 의 클래스에 덧붙이지 않고 통째로 갈아끼웁니다. cn 은 클래스를 잇기만
 * 하므로 bg-surface 와 bg-accent-tint 가 함께 남으면 어느 쪽이 이길지는
 * 스타일시트 순서가 정합니다.
 */
const SELECTED = "border-accent bg-accent-tint transition-colors";

export function cardStyle(
  variant: CardVariant = "static",
  options?: { selected?: boolean; className?: string },
) {
  return cn(
    BASE,
    options?.selected ? SELECTED : VARIANTS[variant],
    options?.className,
  );
}

export function Card({
  variant = "static",
  selected,
  className,
  ...props
}: HTMLAttributes<HTMLDivElement> & {
  variant?: CardVariant;
  selected?: boolean;
}) {
  return (
    <div className={cardStyle(variant, { selected, className })} {...props} />
  );
}

/** 눌러서 다른 화면으로 가는 카드. 기본이 action 입니다. */
export function CardLink({
  variant = "action",
  className,
  href,
  children,
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & {
  variant?: CardVariant;
  href: string;
  children: ReactNode;
}) {
  return (
    <Link
      href={href}
      className={cn(
        cardStyle(variant, { className }),
        "text-ink no-underline hover:no-underline",
      )}
      {...props}
    >
      {children}
    </Link>
  );
}
