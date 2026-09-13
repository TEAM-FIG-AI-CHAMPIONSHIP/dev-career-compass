import type { ReactNode } from "react";
import Link from "next/link";
import { routes } from "@/lib/routes";
import { PageWidth } from "./PageWidth";

/**
 * 모든 화면의 상단 바.
 *
 * 왼쪽은 서비스 이름만 둡니다. 앞뒤 이동은 본문 아래 단계 이동 줄이 맡습니다 —
 * 돌아가는 길이 위아래 두 곳에 있으면 어느 쪽이 무엇인지 알기 어렵습니다.
 */
export function AppHeader({ right }: { right?: ReactNode }) {
  return (
    <header className="border-b border-line bg-paper">
      <PageWidth className="flex flex-wrap items-center justify-between gap-3 py-4">
        <Link
          href={routes.home}
          className="text-[1.0625rem] font-bold tracking-[-0.01em] text-ink no-underline hover:no-underline"
        >
          Refactor.me
        </Link>
        {right}
      </PageWidth>
    </header>
  );
}
