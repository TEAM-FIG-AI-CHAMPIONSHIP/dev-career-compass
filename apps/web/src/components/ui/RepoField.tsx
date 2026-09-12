"use client";

import { cn } from "@/lib/cn";

/**
 * GitHub 저장소 주소 입력. 선택 항목이고 최대 3개까지 받습니다.
 *
 * README는 공개 저장소만 조회하고 원문을 저장하지 않습니다.
 * 읽을 수 없는 저장소는 막지 않고, 그 항목만 빼고 진행한다고 알립니다 —
 * 저장소를 평가하거나 첨삭하는 화면이 아닙니다.
 */
export function RepoField({
  value,
  onChange,
  error,
  ...props
}: {
  value: string;
  onChange: (next: string) => void;
  error?: string;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "value" | "onChange">) {
  return (
    <div className="flex flex-col gap-1.5">
      <div
        className={cn(
          "flex min-h-11 items-center gap-2.5 rounded-card border bg-surface px-3.5 py-3",
          "focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent",
          error ? "border-warn" : "border-line-strong",
        )}
      >
        <span
          className="font-mono text-[0.8125rem] text-ink-soft select-none"
          aria-hidden="true"
        >
          github.com/
        </span>
        <input
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          placeholder="사용자명/저장소"
          aria-label="GitHub 저장소 주소"
          aria-invalid={error ? true : undefined}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "min-w-0 flex-1 bg-transparent font-mono text-[0.84375rem] text-ink",
            "placeholder:font-sans placeholder:text-[0.875rem] placeholder:text-ink-muted",
            "focus:outline-none",
          )}
          {...props}
        />
      </div>
      {error && (
        <span className="text-caption leading-[1.7] text-warn">{error}</span>
      )}
    </div>
  );
}
