"use client";

import { CheckIcon } from "./icons";
import { Chip } from "./Chip";
import { cn } from "@/lib/cn";
import { cardStyle } from "./Card";

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
      className={cardStyle("action", {
        selected: checked,
        className: "flex h-full min-h-11 cursor-pointer items-start gap-3 p-4",
      })}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      {/* 네모는 터미널처럼 각지게 두되, 테두리를 진하게 해서 누를 수 있게
          생기도록 합니다. 흐린 테두리는 "표시" 로 읽히고 "조작" 으로 읽히지
          않습니다. */}
      <span
        aria-hidden="true"
        className={cn(
          "mt-[3px] flex size-4 shrink-0 items-center justify-center rounded-[2px] border transition-colors",
          checked
            ? "border-accent bg-accent text-accent-on"
            : "border-ink-muted bg-surface",
        )}
      >
        {checked && <CheckIcon size={11} strokeWidth={2.6} />}
      </span>
      <span className="flex flex-col gap-0.5">
        <span className="flex flex-wrap items-center gap-1.5">
          <span className={cn("text-body-sm", checked && "font-medium")}>
            {label}
          </span>
          {badge && (
            <Chip tone="accent" className="px-2 py-0.5 font-mono text-meta">
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
  step,
  title,
  description,
  selected,
  onSelect,
}: {
  step?: string;
  title: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={selected}
      onClick={onSelect}
      className={cardStyle("action", {
        selected,
        className:
          "flex h-full cursor-pointer flex-col gap-1.5 p-[18px] text-left",
      })}
    >
      {step ? (
        <span
          className={cn(
            "font-mono text-meta",
            selected ? "text-accent" : "text-ink-muted",
          )}
        >
          {step}
        </span>
      ) : null}
      <span className="text-body font-semibold text-ink">{title}</span>
      <span className="text-caption text-ink-soft">{description}</span>
    </button>
  );
}
