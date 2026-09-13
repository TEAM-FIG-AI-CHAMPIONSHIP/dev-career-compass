"use client";

import { useSyncExternalStore } from "react";
import { AutoThemeIcon, MoonIcon, SunIcon } from "./icons";

/**
 * 테마 전환.
 *
 * 세 상태입니다 — light / dark / auto. auto 는 속성을 떼어 운영체제 설정에
 * 맡깁니다. 두 상태만 두면 "지금 시스템을 따르는 중" 을 표현할 방법이 없어,
 * 시스템을 바꿔도 화면이 따라오지 않는 이유를 설명할 수 없습니다.
 *
 * 버튼은 하나이고 누를 때마다 순환합니다. 세 칸짜리 토글은 상단 바에서
 * 200px 가까이 차지해 회사·직무 이름과 단계 표시를 밀어냈습니다. 테마는
 * 한 번 정하면 다시 건드리지 않는 조작이라 그만한 자리를 줄 이유가 없습니다.
 *
 * 대신 지금 무엇이 켜져 있는지 글자로 보이지 않으므로, 무엇이 켜져 있고
 * 누르면 무엇이 되는지를 aria-label 과 title 에 적습니다.
 *
 * 실제 상태는 문서의 data-theme 속성입니다. state 를 따로 두면 첫 페인트 전에
 * layout.tsx 의 THEME_INIT 이 붙여 놓은 값과 어긋날 수 있습니다.
 */
type Theme = "light" | "dark" | "auto";

const ORDER: Theme[] = ["light", "dark", "auto"];

const META: Record<Theme, { Icon: typeof SunIcon; label: string }> = {
  light: { Icon: SunIcon, label: "라이트" },
  dark: { Icon: MoonIcon, label: "다크" },
  auto: { Icon: AutoThemeIcon, label: "시스템 설정" },
};

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
  const { Icon, label } = META[theme];
  const next = ORDER[(ORDER.indexOf(theme) + 1) % ORDER.length];
  const description = `테마: ${label}. 누르면 ${META[next].label}으로 바뀝니다`;

  return (
    <button
      type="button"
      onClick={() => apply(next)}
      aria-label={description}
      title={description}
      className="inline-flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-btn border border-line-strong bg-surface text-ink-soft transition-colors hover:border-ink-muted hover:text-ink"
    >
      <Icon size={16} />
    </button>
  );
}
