"use client";

import { useSyncExternalStore } from "react";
import type { ExperienceInput } from "@/types/data";

/**
 * 경험 입력은 이 브라우저에만 둡니다. 서버에 저장하지 않습니다.
 *
 * 개인화가 필요할 때만 요청 본문으로 한 번 보내고, 서버는 응답을 만든 뒤 버립니다.
 * 저장 계층을 아예 만들지 않는 것이 "저장하지 않는다"를 지키는 가장 확실한 방법입니다.
 *
 * effect 안에서 setState 하는 대신 useSyncExternalStore 로 읽습니다. 서버 렌더에서는
 * 늘 null 이고, 하이드레이션이 끝나면 저장된 값으로 한 번에 맞춰집니다.
 */

const KEY = "refactor.me.experience.v1";
const LEGACY_KEY = "beforejoin.experience.v1";

const listeners = new Set<() => void>();

function readRaw(): string | null {
  try {
    return window.localStorage.getItem(KEY) ?? window.localStorage.getItem(LEGACY_KEY);
  } catch {
    // 프라이빗 모드나 저장소 차단. 저장이 안 될 뿐 화면은 그대로 돌아야 합니다.
    return null;
  }
}

// getSnapshot 은 같은 값이면 같은 참조를 돌려줘야 합니다. 매번 파싱하면 무한 렌더입니다.
let lastRaw: string | null = null;
let lastParsed: ExperienceInput | null = null;

function getSnapshot(): ExperienceInput | null {
  const raw = readRaw();
  if (raw !== lastRaw) {
    lastRaw = raw;
    try {
      lastParsed = raw ? (JSON.parse(raw) as ExperienceInput) : null;
    } catch {
      lastParsed = null;
    }
  }
  return lastParsed;
}

function getServerSnapshot(): ExperienceInput | null {
  return null;
}

function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  window.addEventListener("storage", onChange);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onChange);
  };
}

function emit(): void {
  for (const l of listeners) l();
}

/**
 * 저장된 경험을 읽습니다.
 *
 * 카탈로그 버전이 다르면 없는 것으로 칩니다. 항목이 바뀌었는데 옛 선택이 남아
 * 있으면, 사라진 항목 id 가 그대로 개인화에 실려 나갑니다.
 */
export function useExperience(catalogVersion: number): ExperienceInput | null {
  const stored = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  if (!stored) return null;
  return stored.catalogVersion === catalogVersion ? stored : null;
}

export function saveExperience(input: ExperienceInput): void {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(input));
    window.localStorage.removeItem(LEGACY_KEY);
  } catch {
    /* 저장 실패는 조용히 넘깁니다. 이번 화면은 화면 상태로 계속 동작합니다. */
  }
  emit();
}

export function clearExperience(): void {
  try {
    window.localStorage.removeItem(KEY);
    window.localStorage.removeItem(LEGACY_KEY);
  } catch {
    /* 위와 같음 */
  }
  emit();
}
