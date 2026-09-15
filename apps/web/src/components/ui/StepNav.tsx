import type { ReactNode } from "react";

/**
 * 본문 아래 단계 이동 줄. 뒤로·다음을 함께 오른쪽에 둡니다.
 *
 * 전에는 뒤로가 왼쪽, 다음이 오른쪽이라 화면 양 끝에 떨어져 있었습니다.
 * 버튼 하나짜리 화면(`/match` 진입, `/match/{역할}/result`,
 * `/companies/{회사}/{역할}`)은 그 뒤로 버튼만 왼쪽에 혼자 남아, 두 버튼짜리
 * 화면과 자리가 서로 달랐습니다. 둘 다 오른쪽에 모으면 한 칸 넘어가는
 * 동작 — 뒤로든 다음이든 — 이 항상 같은 자리에서 일어납니다.
 *
 * 다섯 화면이 같은 자리에 같은 방향으로 둡니다. 한 화면에서 익힌 위치가 다음
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
    <div className="flex flex-wrap items-center justify-end gap-3">
      {back}
      {next}
    </div>
  );
}
