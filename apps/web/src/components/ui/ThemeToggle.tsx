"use client";

import { useSyncExternalStore } from "react";
import { cn } from "@/lib/cn";

/**
 * 테마 전환.
 *
 * 세 상태입니다 — light / dark / auto. auto 는 속성을 떼어 운영체제 설정에
 * 맡깁니다. 두 상태(라이트·다크)만 두면 "지금 시스템을 따르는 중"을 표현할
 * 방법이 없어, 시스템을 바꿔도 화면이 따라오지 않는 이유를 설명할 수 없습니다.
 *
 * 고른 값은 이 브라우저에만 남습니다. 첫 페인트 전 적용은 layout.tsx 의
 * THEME_INIT 이 맡고, 이 컴포넌트는 그 뒤의 전환만 맡습니다.
 *
 * 실제 상태는 문서의 data-theme 속성입니다. 그래서 state 를 따로 두지 않고
 * useSyncExternalStore 로 속성을 그대로 읽습니다 — 두 벌로 두면 THEME_INIT 이
 * 붙여 놓은 값과 어긋날 수 있습니다.
 */
type Theme = "light" | "dark" | "auto";

const OPTIONS: Theme[] = ["light", "dark", "auto"];

const listeners = new Set<() => void>();

function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

function getSnapshot(): Theme {
  const attr = document.documentElement.getAttribute("data-theme");
  return attr === "dark" || attr === "light" ? attr : "auto";
}

/* 서버는 사용자의 선택을 모릅니다. 하이드레이션 직후 실제 값으로 맞춰집니다. */
function getServerSnapshot(): Theme {
  return "auto";
}

function apply(next: Theme): void {
  const root = document.documentElement;
  if (next === "auto") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", next);

  try {
    window.localStorage.setItem("rm-theme", next);
  } catch {
    // 저장소를 막아 둔 브라우저. 저장이 안 될 뿐 이번 방문 동안은 적용됩니다.
  }

  for (const listener of listeners) listener();
}

export function ThemeToggle() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  return (
    <div
      role="group"
      aria-label="테마"
      className="inline-flex overflow-hidden rounded-btn border border-line-strong"
    >
      {OPTIONS.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={theme === option}
          onClick={() => apply(option)}
          className={cn(
            "cursor-pointer border-r border-line-strong px-2.5 py-1 font-mono text-meta last:border-r-0",
            "transition-colors",
            theme === option
              ? "bg-accent text-accent-on"
              : "bg-surface text-ink-soft hover:text-ink",
          )}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
