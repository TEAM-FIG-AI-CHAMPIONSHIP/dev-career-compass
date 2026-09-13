import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * 모든 화면이 쓰는 가로 껍데기.
 *
 * 상단 바와 본문이 같은 것을 써야 로고와 본문 첫 글자가 세로로 맞습니다.
 * 전에는 상단 바가 lg:px-20, 회사 선택 본문이 lg:px-12 라 1024~1280px 구간에서
 * 32px 어긋났습니다.
 *
 * 최대 폭은 아주 넓은 화면에서 한 줄이 무한정 길어지지 않게 하는 상한입니다.
 * 읽는 글은 이 안에서 max-w-3xl 로 한 번 더 묶습니다.
 */
export function PageWidth({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "mx-auto w-full max-w-[90rem] px-4 sm:px-8 lg:px-12 xl:px-20",
        className,
      )}
    >
      {children}
    </div>
  );
}
