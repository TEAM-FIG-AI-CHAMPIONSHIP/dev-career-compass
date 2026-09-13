"use client";

import { useSyncExternalStore } from "react";
import { routes } from "@/lib/routes";

export type MatchFlow = {
  role: string;
  returnTo: string;
  repositories: string[];
  /** 저장소 URL → 추출된 키워드. 분석에 실패한 저장소는 키가 없다. */
  repositoryKeywords: Record<string, string[]>;
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

function safeKeywords(value: unknown): Record<string, string[]> {
  if (typeof value !== "object" || value === null) return {};
  const out: Record<string, string[]> = {};
  for (const [url, keywords] of Object.entries(value as Record<string, unknown>)) {
    if (Array.isArray(keywords) && keywords.every((k) => typeof k === "string")) {
      out[url] = keywords;
    }
  }
  return out;
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
      const value = raw
        ? (JSON.parse(raw) as Partial<MatchFlow> & { repositoryKeywords?: unknown })
        : null;
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
              repositoryKeywords: safeKeywords(value.repositoryKeywords),
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
    repositoryKeywords: current?.role === role ? current.repositoryKeywords : {},
  });
}

export function saveMatchRepositories(
  role: string,
  repositories: string[],
  repositoryKeywords: Record<string, string[]>,
): void {
  const current = getSnapshot();
  write({
    role,
    returnTo:
      current?.role === role ? current.returnTo : routes.matchResult(role),
    repositories,
    repositoryKeywords,
  });
}

/** 경험 저장 직전에 임시 흐름을 꺼내고 지웁니다. */
export function finishMatchFlow(role: string): {
  active: boolean;
  returnTo: string;
  repositories: string[];
  repositoryKeywords: Record<string, string[]>;
} {
  const current = getSnapshot();
  const active = current?.role === role;
  const result = {
    active,
    returnTo: active ? current.returnTo : routes.matchResult(role),
    repositories: active ? current.repositories : [],
    repositoryKeywords: active ? current.repositoryKeywords : {},
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

/**
 * 이 흐름에서 나갈 곳.
 *
 * 회사 결과에서 시작했으면 그 회사 결과로, 아니면 직무 선택으로 돌아갑니다.
 * 단계 표시의 1단계이자 화면 안의 나가기 버튼이 같은 곳을 가리키도록 한곳에서
 * 정합니다.
 */
export function useMatchExit(role: string): {
  href: string;
  label: string;
  fromCompany: boolean;
} {
  const flow = useMatchFlow(role);
  const fromCompany = flow?.returnTo.startsWith("/companies/") ?? false;
  return fromCompany
    ? { href: flow!.returnTo, label: "회사 결과 보기", fromCompany }
    : { href: routes.match, label: "직무 고르기", fromCompany };
}
