import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowLeftIcon } from "./icons";
import { PageWidth } from "./PageWidth";

/**
 * 흐름 안에 있는 화면의 상단 바. 왼쪽은 돌아갈 곳, 오른쪽은 지금 어디인지입니다.
 *
 * 랜딩과 회사 선택은 흐름의 시작이라 돌아갈 곳이 없어 PageHeader 를 씁니다.
 */
export function BackHeader({
  href,
  label,
  right,
}: {
  href: string;
  label: string;
  right?: ReactNode;
}) {
  return (
    <header className="border-b border-line bg-paper">
      <PageWidth className="flex flex-wrap items-center justify-between gap-3 py-4">
        <Link
          href={href}
          className="inline-flex items-center gap-1.5 text-[0.875rem] text-ink-soft no-underline hover:text-ink hover:no-underline"
        >
          <ArrowLeftIcon size={14} strokeWidth={1.7} />
          {label}
        </Link>
        {right}
      </PageWidth>
    </header>
  );
}
