"use client";

import { Fragment } from "react";
import { useMatchExit } from "@/lib/match-flow-store";
import { AppHeader } from "./AppHeader";

/**
 * 경험 기반 탐색의 상단 바. 직무 · GitHub · 경험 세 화면이 같은 것을 씁니다.
 *
 * 1단계는 흐름에 따라 다릅니다. 회사 결과에서 시작했으면 고른 적 없는 직무
 * 선택이 아니라 그 회사·직무가 1단계이고, 그곳이 곧 돌아갈 곳입니다.
 *
 * 결과 화면은 네 번째 단계가 아니라 세 단계를 모두 지나온 도착점이라 "done" 을
 * 넘깁니다. 그때는 어느 단계도 현재로 표시하지 않습니다.
 *
 * 막대가 아니라 카운터로 씁니다. 진행 막대는 "얼마나 남았나" 를 말하지만
 * 여기서 필요한 것은 "지금 어디인가" 이고, 세 단계뿐이라 이름을 다 적을 수
 * 있습니다. 지금 단계에 붙는 `<` 는 셸의 커서 자리를 흉내 낸 것입니다.
 */
const LATER_STEPS = ["GitHub", "경험"] as const;

export type StepNumber = 1 | 2 | 3;
export type StepState = StepNumber | "done";

export function StepHeader({
  current,
  role,
}: {
  current: StepState;
  role: string;
}) {
  const exit = useMatchExit(role);
  const active = current === "done" ? LATER_STEPS.length + 2 : current;
  const steps = [exit.label, ...LATER_STEPS];

  return (
    <AppHeader
      right={
        <ol
          aria-label="진행 단계"
          className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-caption tracking-normal"
        >
          {steps.map((label, index) => {
            const step = index + 1;
            return (
              <Fragment key={label}>
                {index > 0 && (
                  <li aria-hidden="true" className="text-line-strong">
                    /
                  </li>
                )}
                <li
                  aria-current={step === active ? "step" : undefined}
                  className={
                    step === active
                      ? "text-accent"
                      : step < active
                        ? "text-ink-soft"
                        : "text-ink-muted"
                  }
                >
                  [{step}] {label}
                  {step === active && <span aria-hidden="true"> &lt;</span>}
                </li>
              </Fragment>
            );
          })}
        </ol>
      }
    />
  );
}
