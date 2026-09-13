import { cn } from "@/lib/cn";

export type Stage = "fit" | "step" | "far";

/**
 * 역매칭 3단계.
 *
 * 점수도 퍼센트도 순위도 쓰지 않습니다. 세 번째 단계가 빨강이 아니라 회색인
 * 것은 실패가 아니라 순서의 문제이기 때문입니다. 붉은 경고는 사용자를
 * 불필요하게 위축시킵니다.
 *
 * 색은 이 배지 테두리 안에서만 삽니다. 버튼이나 링크로 새어 나가지 않기
 * 때문에, 화면에서 초록·호박·회색이 보이면 그건 언제나 "상태" 라는 뜻입니다.
 *
 * 코드(FIT / STEP / FAR)를 함께 적어 색을 못 보는 경우에도 세 단계가
 * 구분됩니다.
 */
const STAGES = {
  fit: {
    code: "FIT",
    label: "잘 맞아요",
    className: "border-stage-fit-edge bg-stage-fit-tint text-stage-fit",
  },
  step: {
    code: "STEP",
    label: "한 걸음 필요해요",
    className: "border-stage-step-edge bg-stage-step-tint text-stage-step",
  },
  far: {
    code: "FAR",
    label: "지금은 거리가 있어요",
    className: "border-stage-far-edge bg-stage-far-tint text-stage-far",
  },
} as const;

export function StageBadge({
  stage,
  className,
}: {
  stage: Stage;
  className?: string;
}) {
  const { code, label, className: tone } = STAGES[stage];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-pill border px-2.5 py-1",
        "font-mono text-meta",
        tone,
        className,
      )}
    >
      {code}
      <span aria-hidden="true" className="opacity-40">
        ·
      </span>
      <span className="font-sans text-caption tracking-normal">{label}</span>
    </span>
  );
}

export const STAGE_ORDER: Stage[] = ["fit", "step", "far"];
export const stageLabel = (stage: Stage) => STAGES[stage].label;
