"use client";

import { useEffect, useState } from "react";
import { TerminalWindow } from "@/components/ui/TerminalWindow";

export type TerminalStep = {
  /** 프롬프트 뒤에 한 글자씩 찍히는 명령. */
  command: string;
  /** 명령을 다 친 뒤 한 번에 나오는 응답. */
  output: string;
};

type Status = "running" | "done" | "failed";

const TYPE_MS = 42;
const HOLD_MS = 520;

const DEFAULT_LABEL: Record<Status, string> = {
  running: "분석 중입니다.",
  done: "분석이 끝났습니다.",
  failed: "분석에 실패했습니다.",
};

/** 깜빡이는 블록 커서. 동작 줄이기 설정에서는 켜진 채로 멈춥니다. */
function Caret() {
  return (
    <span
      aria-hidden="true"
      className="inline-block h-[1.05em] w-[0.55em] translate-y-[0.15em] bg-current motion-safe:animate-[caret-blink_1.06s_steps(1,end)_infinite]"
    />
  );
}

function Command({ text, caret }: { text: string; caret?: boolean }) {
  return (
    <div className="flex items-start gap-2">
      <span className="select-none text-accent">$</span>
      <span className="text-ink">{text}</span>
      {caret && <Caret />}
    </div>
  );
}

function Output({ text, failed }: { text: string; failed?: boolean }) {
  return (
    <div className="flex items-start gap-2 pl-4">
      <span className="select-none text-ink-muted">&gt;</span>
      <span className={failed ? "text-warn" : "text-ink-soft"}>{text}</span>
    </div>
  );
}

/**
 * 기다리는 동안 보여주는 터미널.
 *
 * 진행률 막대를 쓰지 않습니다. 몇 퍼센트 왔는지 우리는 모르고, 모르는 숫자를
 * 화면에 적지 않기로 했습니다. 대신 지금 무엇을 하고 있는지 한 줄씩 적습니다.
 *
 * 마지막 명령까지 다 친 뒤에도 `status` 가 `running` 이면 커서만 깜빡이며
 * 기다립니다. 언제 끝날지 모르는 일이라 정해진 개수를 재생하고 멈추면 실제로
 * 끝났는지 알 수 없습니다.
 *
 * 낭독기에는 타이핑을 흘리지 않습니다. 한 글자씩 읽히기 때문에, 화면은
 * 숨기고 상태가 바뀔 때 문장 하나만 알립니다.
 *
 * `steps` 는 렌더마다 새로 만들지 마세요. 모듈 상수로 두거나 `useMemo` 로
 * 감싸야 합니다.
 */
export function AnalysisTerminal({
  steps,
  status = "running",
  title = "refactor.me — bash",
  doneText = "Done.",
  failedText = "Failed. 다시 시도해 주세요.",
  label,
}: {
  steps: TerminalStep[];
  status?: Status;
  title?: string;
  doneText?: string;
  failedText?: string;
  label?: string;
}) {
  const [stepIndex, setStepIndex] = useState(0);
  /* 어느 단계의 글자인지 함께 들고 있어야, 다음 단계로 넘어가는 순간 이전
     명령이 한 번 더 비칩니다. */
  const [typed, setTyped] = useState({ step: 0, text: "" });
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => setReduced(query.matches);
    sync();
    query.addEventListener("change", sync);
    return () => query.removeEventListener("change", sync);
  }, []);

  const command = steps[stepIndex]?.command;

  useEffect(() => {
    if (command == null || reduced) return;

    let timer: ReturnType<typeof setTimeout>;
    let count = 0;

    const tick = () => {
      count += 1;
      setTyped({ step: stepIndex, text: command.slice(0, count) });
      timer =
        count < command.length
          ? setTimeout(tick, TYPE_MS)
          : setTimeout(() => setStepIndex((step) => step + 1), HOLD_MS);
    };

    timer = setTimeout(tick, TYPE_MS);
    return () => clearTimeout(timer);
  }, [stepIndex, command, reduced]);

  /* 동작 줄이기 설정에서는 타이핑을 돌리지 않고 전부 찍힌 상태로 그립니다. */
  const doneCount = reduced ? steps.length : stepIndex;
  const finished = doneCount >= steps.length;
  const partial = typed.step === stepIndex ? typed.text : "";

  return (
    <div className="w-full">
      <p className="sr-only" role="status" aria-live="polite">
        {label ?? DEFAULT_LABEL[status]}
      </p>

      <div aria-hidden="true">
        <TerminalWindow
          title={title}
          bodyClassName="flex min-h-[12.5rem] flex-col gap-1.5 leading-relaxed"
        >
          {steps.slice(0, doneCount).map((step) => (
            <div key={step.command} className="flex flex-col gap-1.5">
              <Command text={step.command} />
              <Output text={step.output} />
            </div>
          ))}

          {!finished && <Command text={partial} caret />}

          {finished && status === "done" && <Output text={doneText} />}
          {finished && status === "failed" && (
            <Output text={failedText} failed />
          )}

          {finished && (
            <div className="flex items-center gap-2 pt-2 text-ink">
              <span className="select-none text-accent">$</span>
              <Caret />
            </div>
          )}
        </TerminalWindow>
      </div>
    </div>
  );
}
