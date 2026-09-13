"use client";

import { useSyncExternalStore } from "react";

/**
 * 해볼 것으로 고른 제안 항목.
 *
 * 한 회사에 제안이 일곱 개씩 붙는데 다 할 수는 없습니다. 체크는 진척 추적이
 * 아니라 "이번에 할 것 고르기" 입니다.
 *
 * 일부러 저장하지 않습니다. 로그인이 없으니 남길 곳은 이 브라우저뿐인데,
 * 체크리스트는 몇 주에 걸쳐 하는 일이라 기기를 바꾸면 사라집니다. 지켜주지
 * 못할 것을 지켜주는 것처럼 보이는 UI 를 두지 않기로 했습니다. 대신 고른
 * 것을 마크다운으로 내보내 각자 쓰는 도구로 가져가게 합니다.
 */
export type Pick = { title: string; steps: string[] };
export type Picks = Record<string, Pick>;

const EMPTY: Picks = {};

let picks: Picks = EMPTY;
const listeners = new Set<() => void>();

function emit(): void {
  for (const listener of listeners) listener();
}

function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

/* getSnapshot 은 값이 같으면 같은 참조를 돌려줘야 합니다. 매번 새 객체를
   만들면 무한 렌더입니다. */
function getSnapshot(): Picks {
  return picks;
}

function getServerSnapshot(): Picks {
  return EMPTY;
}

export function usePicks(): Picks {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

/** 항목 하나를 담거나 뺍니다. 마지막 항목을 빼면 제안 자체가 목록에서 빠집니다. */
export function togglePick(
  id: string,
  title: string,
  step: string,
  next: boolean,
): void {
  const current = picks[id]?.steps ?? [];
  const steps = next
    ? current.includes(step)
      ? current
      : [...current, step]
    : current.filter((kept) => kept !== step);

  const { [id]: _removed, ...rest } = picks;
  picks = steps.length > 0 ? { ...rest, [id]: { title, steps } } : rest;
  emit();
}

export function isPicked(all: Picks, id: string, step: string): boolean {
  return all[id]?.steps.includes(step) ?? false;
}

export function clearPicks(): void {
  picks = EMPTY;
  emit();
}

export function countPicked(all: Picks): number {
  return Object.values(all).reduce((sum, pick) => sum + pick.steps.length, 0);
}

/**
 * 고른 항목을 마크다운 체크리스트로 만듭니다.
 *
 * 제안 순서가 아니라 고른 순서를 따릅니다 — 사용자가 담은 순서가 곧 그 사람이
 * 생각한 순서입니다.
 */
export function toMarkdown(all: Picks, heading: string): string {
  const blocks = Object.values(all).map(({ title, steps }) =>
    [`### ${title}`, ...steps.map((step) => `- [ ] ${step}`)].join("\n"),
  );
  return [`## ${heading}`, ...blocks].join("\n\n").trim();
}
