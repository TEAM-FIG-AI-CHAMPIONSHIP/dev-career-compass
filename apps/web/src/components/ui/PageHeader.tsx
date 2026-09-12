import Link from "next/link";
import type { ReactNode } from "react";
import { routes } from "@/lib/routes";

/** 모든 화면이 쓰는 상단 바. 왼쪽은 현재 위치, 오른쪽은 그 화면의 동작입니다. */
export function PageHeader({
  crumbs = [],
  right,
}: {
  crumbs?: ReactNode[];
  right?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-4 sm:px-8 lg:px-20">
      <div className="flex flex-wrap items-center gap-3">
        <Link
          href={routes.home}
          className="text-[1.0625rem] font-bold tracking-[-0.01em] text-ink no-underline hover:no-underline"
        >
          BeforeJoin
        </Link>
        {crumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-3">
            <span aria-hidden="true" className="text-line-strong">
              /
            </span>
            {crumb}
          </span>
        ))}
      </div>
      {right}
    </header>
  );
}

/** 지금 어떤 데이터를 보고 있는지. fixture 를 실제 결과로 오해하지 않게 합니다. */
export function DataSourceNote({ source }: { source: "published" | "fixtures" }) {
  if (source === "published") return null;
  return (
    <div className="border-t border-line px-4 py-4 sm:px-8 lg:px-20">
      <p className="text-caption text-ink-muted">
        지금 보이는 회사와 근거는 화면 확인용 임시 데이터입니다. 기술 블로그와 채용
        공고의 검증·확정은 따로 진행 중이며, 그 결과가 들어오면 이 화면이 그대로
        바뀝니다.
      </p>
    </div>
  );
}
