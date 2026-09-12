"use client";

import { useSyncExternalStore } from "react";
import { routes } from "@/lib/routes";

export type MatchFlow = {
  role: string;
  returnTo: string;
  repositories: string[];
};

const KEY = "refactor.me.match-flow.v1";
const LEGACY_KEY = "beforejoin.match-flow.v1";
const listeners = new Set<() => void>();

let lastRaw: string | null = null;
let lastParsed: MatchFlow | null = null;

function safeReturnTo(value: string | undefined, role: string): string {
  if (value?.startsWith("/") && !value.startsWith("//")) return value;
  return routes.matchResult(role);
}

function readRaw(): string | null {
  try {
    return window.sessionStorage.getItem(KEY) ?? window.sessionStorage.getItem(LEGACY_KEY);
  } catch {
    return null;
  }
}

function getSnapshot(): MatchFlow | null {
  const raw = readRaw();
  if (raw !== lastRaw) {
    lastRaw = raw;
    try {
      const value = raw ? (JSON.parse(raw) as Partial<MatchFlow>) : null;
      lastParsed =
        value &&
        typeof value.role === "string" &&
        typeof value.returnTo === "string" &&
        Array.isArray(value.repositories)
          ? {
              role: value.role,
              returnTo: safeReturnTo(value.returnTo, value.role),
              repositories: value.repositories.filter(
                (repository): repository is string => typeof repository === "string",
              ),
            }
          : null;
    } catch {
      lastParsed = null;
    }
  }
  return lastParsed;
}

function getServerSnapshot(): MatchFlow | null {
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
  for (const listener of listeners) listener();
}

function write(flow: MatchFlow): void {
  try {
    window.sessionStorage.setItem(KEY, JSON.stringify(flow));
    window.sessionStorage.removeItem(LEGACY_KEY);
  } catch {
    // 저장소가 막혀도 기본 역매칭 경로로 흐름을 이어갈 수 있습니다.
  }
  emit();
}

export function useMatchFlow(role: string): MatchFlow | null {
  const flow = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  return flow?.role === role ? flow : null;
}

/** 회사 결과에서 시작한 경우, 완료 뒤 돌아갈 URL만 세션 동안 보관합니다. */
export function beginMatchFlow(role: string, returnTo?: string): void {
  const current = getSnapshot();
  write({
    role,
    returnTo: safeReturnTo(returnTo, role),
    repositories: current?.role === role ? current.repositories : [],
  });
}

export function saveMatchRepositories(role: string, repositories: string[]): void {
  const current = getSnapshot();
  write({
    role,
    returnTo:
      current?.role === role ? current.returnTo : routes.matchResult(role),
    repositories,
  });
}

/** 경험 저장 직전에 임시 흐름을 꺼내고 지웁니다. */
export function finishMatchFlow(role: string): {
  active: boolean;
  returnTo: string;
  repositories: string[];
} {
  const current = getSnapshot();
  const active = current?.role === role;
  const result = {
    active,
    returnTo: active ? current.returnTo : routes.matchResult(role),
    repositories: active ? current.repositories : [],
  };

  try {
    window.sessionStorage.removeItem(KEY);
    window.sessionStorage.removeItem(LEGACY_KEY);
  } catch {
    // 다음 화면으로 가는 데 저장소 삭제 성공 여부는 영향을 주지 않습니다.
  }
  emit();
  return result;
}
