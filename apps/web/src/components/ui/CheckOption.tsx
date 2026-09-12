"use client";

import { CheckIcon } from "./icons";
import { cn } from "@/lib/cn";

/**
 * S3 경험 입력의 체크 항목.
 * 최소 선택 개수를 강제하지 않습니다 — 해당하는 것만 고르면 됩니다.
 */
export function CheckOption({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <label
      className={cn(
        "flex min-h-11 cursor-pointer items-start gap-3 rounded-card border p-4",
        "bg-surface transition-colors",
        checked ? "border-ink" : "border-line hover:border-ink-muted",
      )}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      <span
        aria-hidden="true"
        className={cn(
          "mt-0.5 flex size-[18px] shrink-0 items-center justify-center rounded-[3px] border",
          checked
            ? "border-ink bg-ink text-paper"
            : "border-ink-muted bg-surface",
        )}
      >
        {checked && <CheckIcon size={12} strokeWidth={2.4} />}
      </span>
      <span className="flex flex-col gap-0.5">
        <span
          className={cn(
            "text-[0.90625rem] leading-[1.7]",
            checked && "font-medium",
          )}
        >
          {label}
        </span>
        {description && (
          <span className="text-caption text-ink-soft">{description}</span>
        )}
      </span>
    </label>
  );
}

/** 진행 수준 3단계 — 하나만 고릅니다. */
export function LevelOption({
  step,
  title,
  description,
  selected,
  onSelect,
}: {
  step: string;
  title: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={cn(
        "flex cursor-pointer flex-col gap-1.5 rounded-card border p-[18px] text-left",
        "transition-colors",
        selected
          ? "border-ink bg-ink"
          : "border-line bg-surface hover:border-ink-muted",
      )}
    >
      <span
        className={cn(
          "font-mono text-[0.6875rem] tracking-[0.06em]",
          selected ? "text-ink-soft" : "text-ink-muted",
        )}
      >
        {step}
      </span>
      <span
        className={cn(
          "text-[0.9375rem] leading-[1.6] font-semibold",
          selected ? "text-paper" : "text-ink",
        )}
      >
        {title}
      </span>
      <span
        className={cn(
          "text-[0.8125rem] leading-[1.7]",
          selected ? "text-line-strong" : "text-ink-soft",
        )}
      >
        {description}
      </span>
    </button>
  );
}
