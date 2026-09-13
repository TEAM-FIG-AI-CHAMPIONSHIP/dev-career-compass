"use client";

import { Fragment } from "react";
import { useMatchExit } from "@/lib/match-flow-store";
import { AppHeader } from "./AppHeader";
import { ArrowRightIcon } from "./icons";

/**
 * 경험 기반 탐색의 상단 바. 직무 · GitHub · 경험 세 화면이 같은 것을 씁니다.
 *
 * 1단계는 흐름에 따라 다릅니다. 회사 결과에서 시작했으면 고른 적 없는 직무
 * 선택이 아니라 그 회사·직무가 1단계이고, 그곳이 곧 돌아갈 곳입니다.
 *
 * 결과 화면은 네 번째 단계가 아니라 세 단계를 모두 지나온 도착점이라 "done" 을
 * 넘깁니다. 그때는 어느 단계도 현재로 표시하지 않습니다.
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
          className="flex items-center gap-2 text-[0.8125rem]"
        >
          {steps.map((label, index) => {
            const step = index + 1;
            return (
              <Fragment key={label}>
                {index > 0 && (
                  <li aria-hidden="true" className="flex text-line-strong">
                    <ArrowRightIcon size={13} strokeWidth={1.7} />
                  </li>
                )}
                <li
                  aria-current={step === active ? "step" : undefined}
                  className={
                    step === active
                      ? "font-semibold text-accent"
                      : step < active
                        ? "text-ink-soft"
                        : "text-ink-muted"
                  }
                >
                  {step}. {label}
                </li>
              </Fragment>
            );
          })}
        </ol>
      }
    />
  );
}
