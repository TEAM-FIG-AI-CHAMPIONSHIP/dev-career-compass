import type { ReactNode } from "react";
import Link from "next/link";
import { routes } from "@/lib/routes";
import { PageWidth } from "./PageWidth";
import { BrandLogo } from "./Logo";

/**
 * 모든 화면의 상단 바.
 *
 * 왼쪽은 서비스 이름만 둡니다. 앞뒤 이동은 본문 아래 단계 이동 줄이 맡습니다 —
 * 돌아가는 길이 위아래 두 곳에 있으면 어느 쪽이 무엇인지 알기 어렵습니다.
 *
 * 테마 전환은 여기 두지 않습니다. 진입 화면에만 있습니다 — 상단 바에 두면
 * 회사·직무 이름과 단계 표시를 밀어내는데, 한 번 정하면 다시 건드리지 않는
 * 조작이라 모든 화면에 자리를 내줄 이유가 없습니다.
 */
export function AppHeader({ right }: { right?: ReactNode }) {
  return (
    <header className="border-b border-line-strong bg-paper">
      <PageWidth className="flex flex-wrap items-center justify-between gap-3 py-4">
        <Link
          href={routes.home}
          className="inline-flex items-center no-underline transition-opacity hover:opacity-70 hover:no-underline"
        >
          <BrandLogo />
        </Link>
        {right}
      </PageWidth>
    </header>
  );
}
