import { CheckIcon, ArrowRightIcon, DistantIcon } from "./icons";
import { cn } from "@/lib/cn";

export type Stage = "fit" | "step" | "far";

/**
 * 역매칭 3단계.
 *
 * 점수도 퍼센트도 순위도 쓰지 않습니다. 색·아이콘·문구 세 가지로만 구분합니다.
 * 세 번째 단계가 빨강이 아니라 회색인 것은 실패가 아니라 순서의 문제이기
 * 때문입니다. 붉은 경고는 사용자를 불필요하게 위축시킵니다.
 */
const STAGES = {
  fit: {
    label: "잘 맞아요",
    Icon: CheckIcon,
    className: "border-stage-fit-edge bg-stage-fit-tint text-stage-fit",
  },
  step: {
    label: "한 걸음 필요해요",
    Icon: ArrowRightIcon,
    className: "border-stage-step-edge bg-stage-step-tint text-stage-step",
  },
  far: {
    label: "지금은 거리가 있어요",
    Icon: DistantIcon,
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
  const { label, Icon, className: tone } = STAGES[stage];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-pill border px-4 py-2",
        "text-[0.875rem] leading-normal font-medium",
        tone,
        className,
      )}
    >
      <Icon size={15} strokeWidth={1.8} />
      {label}
    </span>
  );
}

export const STAGE_ORDER: Stage[] = ["fit", "step", "far"];
export const stageLabel = (stage: Stage) => STAGES[stage].label;
