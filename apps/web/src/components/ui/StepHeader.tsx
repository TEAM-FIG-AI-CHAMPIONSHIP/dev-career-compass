import { Fragment } from "react";
import { routes } from "@/lib/routes";
import { BackHeader } from "./BackHeader";

/**
 * 경험 기반 탐색의 상단 바. 직무 · GitHub · 경험 세 화면이 같은 것을 씁니다.
 *
 * 결과 화면은 네 번째 단계가 아니라 세 단계를 모두 지나온 도착점이라 "done" 을
 * 넘깁니다. 그때는 어느 단계도 현재로 표시하지 않습니다.
 *
 * 단계를 늘리거나 줄이면 STEPS 만 고치면 되고, 화면 쪽은 현재 번호만 넘깁니다.
 */
const STEPS = ["직무", "GitHub", "경험"] as const;

export type StepNumber = 1 | 2 | 3;

/** "done" 은 세 단계를 모두 끝낸 상태입니다. */
export type StepState = StepNumber | "done";

export function StepHeader({ current }: { current: StepState }) {
  const active = current === "done" ? STEPS.length + 1 : current;
  return (
    <BackHeader
      href={routes.home}
      label="처음으로"
      right={
        <ol
          aria-label="진행 단계"
          className="flex items-center gap-2 text-[0.8125rem]"
        >
          {STEPS.map((label, index) => {
            const step = index + 1;
            return (
              <Fragment key={label}>
                {index > 0 && (
                  <li aria-hidden="true" className="text-line-strong">
                    →
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
