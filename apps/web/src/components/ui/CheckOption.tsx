"use client";

import { CheckIcon } from "./icons";
import { Chip } from "./Chip";
import { cn } from "@/lib/cn";

/**
 * 경험 입력의 다중 선택 카드. 최소 선택 개수를 강제하지 않습니다.
 */
export function CheckboxCard({
  label,
  description,
  checked,
  onChange,
  badge,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (next: boolean) => void;
  /** GitHub 저장소 키워드로 자동 제안된 항목임을 표시할 때만 넘깁니다. */
  badge?: string;
}) {
  return (
    <label
      className={cn(
        "flex h-full min-h-11 cursor-pointer items-start gap-3 rounded-card border p-4",
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
        <span className="flex flex-wrap items-center gap-1.5">
          <span
            className={cn(
              "text-[0.90625rem] leading-[1.7]",
              checked && "font-medium",
            )}
          >
            {label}
          </span>
          {badge && (
            <Chip tone="accent" className="px-2 py-0.5 text-[0.6875rem]">
              {badge}
            </Chip>
          )}
        </span>
        {description && (
          <span className="text-caption text-ink-soft">{description}</span>
        )}
      </span>
    </label>
  );
}

/** 디자인 시스템 갤러리와 기존 import를 위한 별칭. */
export const CheckOption = CheckboxCard;

/**
 * 진행 수준 단일 선택 카드. 한 그룹에서 하나만 고릅니다.
 */
export function RadioCard({
  name,
  step,
  title,
  description,
  selected,
  onSelect,
}: {
  name: string;
  step?: string;
  title: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <label
      className={cn(
        "flex h-full cursor-pointer flex-col gap-1.5 rounded-card border p-[18px] text-left",
        "transition-colors",
        selected
          ? "border-ink bg-ink"
          : "border-line bg-surface hover:border-ink-muted",
      )}
    >
      <input
        type="radio"
        name={name}
        checked={selected}
        onChange={onSelect}
        className="sr-only"
      />
      {step ? (
        <span
          className={cn(
            "font-mono text-[0.6875rem] tracking-[0.06em]",
            selected ? "text-ink-soft" : "text-ink-muted",
          )}
        >
          {step}
        </span>
      ) : null}
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
    </label>
  );
}

/** 디자인 시스템 갤러리와 기존 import를 위한 별칭. */
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
    <RadioCard
      name="experience-level-gallery"
      step={step}
      title={title}
      description={description}
      selected={selected}
      onSelect={onSelect}
    />
  );
}
