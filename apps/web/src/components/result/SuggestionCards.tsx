"use client";

import { useId } from "react";
import type { Analysis, Evidence } from "@/types/data";
import {
  ChevronDownIcon,
  CheckIcon,
  ExternalIcon,
} from "@/components/ui/icons";
import { cardStyle } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { cn } from "@/lib/cn";
import { isPicked, togglePick, usePicks } from "@/lib/suggestion-picks";

/**
 * 제안 본문을 해볼 것 목록으로 나눕니다.
 *
 * 제안은 읽고 지나가는 글이 아니라 해볼 것입니다. 한 문단으로 두면 세 줄을
 * 다 읽어야 무엇을 하라는 건지 알 수 있어, 카드가 일곱 장 쌓이면 아무도
 * 끝까지 읽지 않습니다.
 *
 * 지금은 파이프라인이 `body` 를 문단 하나로 주기 때문에 문장 단위로 끊어
 * 씁니다. 데이터에 `steps[]` 가 생기면 이 함수는 사라집니다 — 문장 부호로
 * 자르는 것은 사람이 나눈 단위를 이길 수 없습니다.
 */
function toSteps(body: string): string[] {
  return body
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);
}

/**
 * 카드 맨 윗줄.
 *
 * 어느 영역에서 나온 제안인지를 제목보다 먼저 둡니다. 본문 아래에 있으면
 * 세 줄을 읽고 나서야 분류를 알게 되어, 훑어보는 사람에게는 보이지 않습니다.
 *
 * 위쪽 영역 목록과 같은 칩 모양을 씁니다. 형태가 같아야 "저 영역에서 나온
 * 제안" 이라는 연결이 색 없이도 읽힙니다.
 */
function CardMeta({
  domain,
  juniorDemand,
}: {
  domain?: string;
  juniorDemand?: boolean;
}) {
  if (!domain && !juniorDemand) return null;
  return (
    <div className="flex flex-wrap items-center gap-2">
      {domain && <Chip>{domain}</Chip>}
      {juniorDemand && (
        <Chip tone="accent">
          <CheckIcon size={12} strokeWidth={1.8} />
          신입 공고에서도 요구됨
        </Chip>
      )}
    </div>
  );
}

/**
 * 이미 만든 것 → 갈 곳.
 *
 * 빨강·초록 diff 로도 보여줄 수 있지만, 카드가 여러 장 놓이면 색이 너무
 * 튑니다. 색 대신 명도로 말합니다 — 이미 한 것은 흐리게, 갈 곳은 진하게.
 * 앞의 `이미` 라벨이 없으면 흐린 줄이 "덜 중요한 글" 로 읽힙니다.
 */
function FromTo({ from, to }: { from: string; to: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <p className="flex flex-wrap items-baseline gap-2 text-body-sm text-ink-soft">
        <span className="shrink-0 rounded-pill border border-line-strong bg-sunken px-1.5 py-px font-mono text-meta text-ink-muted">
          이미
        </span>
        {from}
      </p>
      <h3 className="flex gap-2 text-h3 font-semibold text-pretty">
        <span aria-hidden="true" className="shrink-0 font-mono text-accent">
          └─&gt;
        </span>
        {to}
      </h3>
    </div>
  );
}

/**
 * 해볼 것 목록.
 *
 * 체크는 담아 두는 것이지 완료 표시가 아닙니다. 그래서 고른 줄에 취소선을
 * 긋지 않습니다 — 취소선은 "끝냈다" 는 뜻이라, 이제 막 하기로 한 일에
 * 그으면 반대로 읽힙니다.
 */
function StepList({
  id,
  title,
  steps,
}: {
  id: string;
  title: string;
  steps: string[];
}) {
  const picks = usePicks();
  const prefix = useId();

  return (
    <ul className="flex flex-col gap-2.5">
      {steps.map((step, index) => {
        const inputId = `${prefix}-${index}`;
        const checked = isPicked(picks, id, step);
        return (
          <li key={step} className="flex items-start gap-2.5">
            <input
              id={inputId}
              type="checkbox"
              checked={checked}
              onChange={(event) =>
                togglePick(id, title, step, event.target.checked)
              }
              className="sr-only"
            />
            <label
              htmlFor={inputId}
              className="flex cursor-pointer items-start gap-2.5 text-body-sm text-ink-soft"
            >
              <span
                aria-hidden="true"
                className={cn(
                  "mt-[5px] flex size-4 shrink-0 items-center justify-center rounded-[2px] border transition-colors",
                  checked
                    ? "border-accent bg-accent text-accent-on"
                    : "border-ink-muted bg-surface",
                )}
              >
                {checked && <CheckIcon size={11} strokeWidth={2.6} />}
              </span>
              <span className={cn(checked && "text-ink")}>{step}</span>
            </label>
          </li>
        );
      })}
    </ul>
  );
}

/* 서버에서 넘어오는 값은 평범한 객체여야 합니다. 이 파일이 클라이언트
   컴포넌트라 Map 이나 함수는 경계를 넘지 못합니다. */
function EvidenceLinks({
  ids,
  evidence,
}: {
  ids: string[];
  evidence: Record<string, Evidence>;
}) {
  const items = ids.map((id) => evidence[id]).filter((e): e is Evidence => !!e);
  if (items.length === 0) return null;

  return (
    /* mt-auto: 같은 줄 카드들의 근거 줄이 바닥에서 나란히 놓입니다. */
    <details className="group mt-auto border-t border-line pt-3">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 font-mono text-meta text-ink-muted hover:text-ink">
        근거 {items.length}건 · BLOG
        <ChevronDownIcon
          size={13}
          className="transition-transform group-open:rotate-180"
        />
      </summary>
      <ul className="mt-2 flex flex-col gap-1.5">
        {items.map((e) => (
          <li key={e.id}>
            <a
              href={e.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-start gap-1.5 text-caption"
            >
              {e.title}
              <ExternalIcon
                size={12}
                strokeWidth={1.5}
                className="mt-1 shrink-0"
              />
            </a>
          </li>
        ))}
      </ul>
    </details>
  );
}

/** 카드 바깥틀. 두 무리가 같은 골격을 씁니다. */
function SuggestionCard({
  picked,
  children,
}: {
  picked: boolean;
  children: React.ReactNode;
}) {
  return (
    <article
      className={cardStyle("static", {
        className: cn(
          "flex h-full flex-col gap-3.5 p-5 transition-colors sm:p-6",
          /* 하나라도 담기면 테두리만 바꿉니다. 바탕까지 칠하면 카드가 여러 장
             담겼을 때 화면 절반이 물들어 무엇이 제목인지 흐려집니다. */
          picked && "border-accent",
        ),
      })}
    >
      {children}
    </article>
  );
}

/**
 * 새로 시작할 것.
 *
 * 만든 게 없어도 착수할 수 있는 제안입니다. 순서는 파이프라인이 준 순서를
 * 그대로 씁니다.
 */
export function NewSuggestions({
  suggestions,
  evidence,
  domainLabels,
}: {
  suggestions: Analysis["suggestions"]["new"];
  evidence: Record<string, Evidence>;
  domainLabels: Record<string, string>;
}) {
  const picks = usePicks();

  return (
    <ul className="grid grid-cols-1 gap-3 lg:grid-cols-2">
      {suggestions.map((s) => (
        <li key={s.id}>
          <SuggestionCard picked={!!picks[s.id]}>
            <CardMeta
              domain={domainLabels[s.domainId]}
              juniorDemand={s.juniorDemand}
            />
            <h3 className="text-h3 font-semibold text-pretty">{s.title}</h3>
            <StepList id={s.id} title={s.title} steps={toSteps(s.body)} />
            <EvidenceLinks ids={s.evidenceIds} evidence={evidence} />
          </SuggestionCard>
        </li>
      ))}
    </ul>
  );
}

/**
 * 이미 만든 것을 발전시킬 것 — A를 만들었다면 → B.
 *
 * 출발점(from)이 자유 문장이라 경험 입력 항목과 대조되지 않습니다. 지금은
 * 고른 경험과 무관하게 모든 제안을 보여줍니다.
 */
export function DeepenSuggestions({
  suggestions,
  evidence,
  domainLabels,
}: {
  suggestions: Analysis["suggestions"]["deepen"];
  evidence: Record<string, Evidence>;
  domainLabels: Record<string, string>;
}) {
  const picks = usePicks();

  return (
    <ul className="grid grid-cols-1 gap-3 lg:grid-cols-2">
      {suggestions.map((s) => (
        <li key={s.id}>
          <SuggestionCard picked={!!picks[s.id]}>
            <CardMeta
              domain={domainLabels[s.domainId]}
              juniorDemand={s.juniorDemand}
            />
            <FromTo from={s.from} to={s.to} />
            <StepList id={s.id} title={s.to} steps={toSteps(s.body)} />
            <EvidenceLinks ids={s.evidenceIds} evidence={evidence} />
          </SuggestionCard>
        </li>
      ))}
    </ul>
  );
}
