import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * 화면 제목 위에 붙는 셸 명령 한 줄.
 *
 * 이 화면이 무엇을 하는 단계인지를 제목보다 먼저, 개발자의 말로 말합니다.
 * 실제로 실행되는 명령은 아니지만 이름은 화면이 하는 일과 같아야 합니다 —
 * 장식으로 지어낸 명령은 한 번 읽히고 나면 거짓말이 됩니다.
 */
export function CommandLine({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <p className={cn("font-mono text-meta text-ink-muted", className)}>
      <span className="text-accent">$</span> {children}
    </p>
  );
}
