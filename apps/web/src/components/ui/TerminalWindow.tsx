import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * 맥 터미널 창.
 *
 * 이 제품에서 "터미널"이라는 인상은 어두운 바탕이 아니라 이 창틀과 신호등,
 * 그리고 셸 줄에서 나옵니다. 그래서 라이트에서도 컨셉이 그대로 섭니다.
 *
 * 제목은 가운데가 아니라 왼쪽입니다. 맥 터미널이 제목을 가운데 두는 것은
 * 창 폭이 좁을 때고, 여기서는 `>_` 로 시작하는 한 줄이 그 자리를 대신합니다.
 *
 * 신호등은 눌리지 않습니다. 창을 닫거나 줄일 수 없으므로 버튼으로 만들지
 * 않고 장식으로 둡니다. 색은 제목 표시줄 밖으로 나가지 않습니다.
 */
export function TerminalWindow({
  title,
  children,
  className,
  bodyClassName,
}: {
  title: string;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-window border border-line-strong bg-surface shadow-raised",
        className,
      )}
    >
      <div className="flex items-center gap-2.5 border-b border-line-strong bg-sunken px-3.5 py-2.5">
        <span aria-hidden="true" className="flex shrink-0 gap-2">
          <TrafficLight className="bg-mac-close" />
          <TrafficLight className="bg-mac-min" />
          <TrafficLight className="bg-mac-max" />
        </span>
        <span className="truncate font-mono text-caption text-ink-muted">
          <span className="mr-1.5 text-accent">&gt;_</span>
          {title}
        </span>
      </div>
      <div className={cn("p-4 font-mono text-body-sm", bodyClassName)}>
        {children}
      </div>
    </div>
  );
}

/** 신호등 한 알. 테두리는 흰 창 위에서 원이 뭉개지지 않게 하는 최소한입니다. */
function TrafficLight({ className }: { className: string }) {
  return (
    <span
      className={cn("size-3 rounded-full", className)}
      style={{ boxShadow: "inset 0 0 0 0.5px var(--mac-edge)" }}
    />
  );
}
