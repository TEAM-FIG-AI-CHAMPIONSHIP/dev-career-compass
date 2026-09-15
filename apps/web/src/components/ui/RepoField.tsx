"use client";

import { cn } from "@/lib/cn";
import { CloseIcon } from "@/components/ui/icons";

/**
 * GitHub 저장소 링크 입력. 선택 항목이고 최대 3개까지 받습니다.
 *
 * README/설정 파일은 공개 저장소만 조회하고 원문을 저장하지 않습니다.
 * 읽을 수 없는 저장소는 막지 않고, 그 항목만 빼고 진행한다고 알립니다 —
 * 저장소를 평가하거나 첨삭하는 화면이 아닙니다.
 */
export function RepoField({
  value,
  onChange,
  onRemove,
  removeLabel,
  error,
  ...props
}: {
  value: string;
  onChange: (next: string) => void;
  /** 칸을 지웁니다. 칸이 하나뿐일 때는 넘기지 않습니다. */
  onRemove?: () => void;
  removeLabel?: string;
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
        {/* 손으로 그린 단순화 아이콘 대신 GitHub 공식 마크입니다. 색이
            고정된 그림이라 라이트·다크 두 장을 두고 CSS 로 한 장을
            숨깁니다 — `Logo.tsx` 와 같은 방식입니다. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/icons/github-mark-light.svg"
          alt=""
          aria-hidden="true"
          width={16}
          height={16}
          className="theme-light-only block size-4 shrink-0"
        />
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/icons/github-mark-dark.svg"
          alt=""
          aria-hidden="true"
          width={16}
          height={16}
          className="theme-dark-only block size-4 shrink-0"
        />
        <input
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          placeholder="https://github.com/username/repo"
          aria-label="GitHub 저장소 링크"
          aria-invalid={error ? true : undefined}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "min-w-0 flex-1 bg-transparent font-mono text-[0.84375rem] text-ink",
            "placeholder:font-sans placeholder:text-[0.8125rem] placeholder:text-ink-muted",
            "focus:outline-none",
          )}
          {...props}
        />
        {/* 지우기는 칸 안 오른쪽 끝에 둡니다. 줄 밖에 두면 칸이 늘어날수록
            버튼이 어느 줄의 것인지 눈으로 다시 이어야 합니다. */}
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            aria-label={removeLabel ?? "이 저장소 지우기"}
            className="-mr-1 flex size-7 shrink-0 cursor-pointer items-center justify-center rounded-btn text-ink-muted transition-colors hover:bg-sunken hover:text-ink"
          >
            <CloseIcon size={15} />
          </button>
        )}
      </div>
      {error && (
        <span className="text-caption leading-[1.7] text-warn">{error}</span>
      )}
    </div>
  );
}
