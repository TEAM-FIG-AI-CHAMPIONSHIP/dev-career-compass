import type { ReactNode } from "react";
import Link from "next/link";
import { routes } from "@/lib/routes";
import { PageWidth } from "./PageWidth";
import { PixelLogo, Wordmark } from "./PixelLogo";
import { ThemeToggle } from "./ThemeToggle";

/**
 * 모든 화면의 상단 바.
 *
 * 왼쪽은 서비스 이름만 둡니다. 앞뒤 이동은 본문 아래 단계 이동 줄이 맡습니다 —
 * 돌아가는 길이 위아래 두 곳에 있으면 어느 쪽이 무엇인지 알기 어렵습니다.
 *
 * 오른쪽 끝은 테마 전환이 고정으로 차지합니다. 화면마다 자리가 바뀌면 찾는
 * 데 시간이 걸리는 종류의 조작입니다.
 */
export function AppHeader({ right }: { right?: ReactNode }) {
  return (
    <header className="border-b border-line-strong bg-paper">
      <PageWidth className="flex flex-wrap items-center justify-between gap-3 py-4">
        <Link
          href={routes.home}
          className="inline-flex items-center gap-2.5 text-ink no-underline hover:text-accent hover:no-underline"
        >
          <PixelLogo size={26} />
          <Wordmark className="font-mono text-h3 font-bold tracking-tight" />
        </Link>
        <div className="flex items-center gap-4">
          {right}
          <ThemeToggle />
        </div>
      </PageWidth>
    </header>
  );
}
