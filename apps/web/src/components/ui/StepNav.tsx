import type { ReactNode } from "react";

/**
 * 본문 아래 단계 이동 줄. 왼쪽은 뒤로, 오른쪽은 다음입니다.
 *
 * 네 화면이 같은 자리에 같은 방향으로 둡니다. 한 화면에서 익힌 위치가 다음
 * 화면에서도 그대로여야 합니다.
 */
export function StepNav({
  back,
  next,
}: {
  back?: ReactNode;
  next?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-3">{back}</div>
      <div className="flex items-center gap-3">{next}</div>
    </div>
  );
}
