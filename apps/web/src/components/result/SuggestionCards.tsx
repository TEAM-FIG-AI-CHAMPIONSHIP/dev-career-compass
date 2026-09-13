import type { Analysis, Evidence } from "@/types/data";
import {
  ArrowRightIcon,
  ChevronDownIcon,
  CheckIcon,
  ExternalIcon,
} from "@/components/ui/icons";
import { cardStyle } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

/**
 * 제안 번호.
 *
 * 두 무리가 각각 1번부터 다시 시작합니다. 배지까지 같으면 화면 중간에서 본
 * "2" 가 어느 무리의 것인지 구분되지 않아 무리별로 색을 달리합니다. 중요도
 * 차이가 아니라 소속 표시입니다.
 */
function OrderBadge({
  index,
  group,
}: {
  index: number;
  group: "new" | "deepen";
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-card text-body-sm font-semibold",
        group === "new"
          ? "bg-accent-tint text-accent"
          : "bg-sunken text-ink-soft",
      )}
    >
      {index + 1}
    </span>
  );
}

/**
 * 카드 맨 윗줄.
 *
 * 어느 영역에서 나온 제안인지를 제목보다 먼저 둡니다. 본문 아래에 있으면
 * 세 줄을 읽고 나서야 분류를 알게 되어, 훑어보는 사람에게는 보이지 않습니다.
 */
function CardMeta({
  domain,
  juniorDemand,
}: {
  domain?: string;
  juniorDemand?: boolean;
}) {
  if (!domain && !juniorDemand) return null;
  return (
    <div className="flex flex-wrap items-center gap-2">
      {domain && (
        <span className="rounded-pill bg-accent-tint px-2.5 py-1 text-caption text-accent">
          {domain}
        </span>
      )}
      {juniorDemand && (
        <span className="inline-flex items-center gap-1.5 rounded-pill border border-accent px-2.5 py-1 text-caption text-accent">
          <CheckIcon size={12} strokeWidth={1.8} />
          신입 공고에서도 요구됨
        </span>
      )}
    </div>
  );
}

function EvidenceLinks({
  ids,
  byId,
}: {
  ids: string[];
  byId: Map<string, Evidence>;
}) {
  const items = ids.map((id) => byId.get(id)).filter((e): e is Evidence => !!e);
  if (items.length === 0) return null;

  return (
    /* mt-auto: 같은 줄 카드들의 근거 줄이 바닥에서 나란히 놓입니다. */
    <details className="group mt-auto border-t border-line pt-3">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 text-body-sm text-ink-muted hover:text-ink">
        근거 {items.length}건
        <ChevronDownIcon
          size={14}
          className="transition-transform group-open:rotate-180"
        />
      </summary>
      <ul className="mt-2 flex flex-col gap-1.5">
        {items.map((e) => (
          <li key={e.id}>
            <a
              href={e.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-start gap-1.5 text-body-sm"
            >
              {e.title}
              <ExternalIcon
                size={13}
                strokeWidth={1.5}
                className="mt-1 shrink-0"
              />
            </a>
          </li>
        ))}
      </ul>
    </details>
  );
}

/** 카드 바깥틀. 두 무리가 같은 골격을 씁니다. */
function SuggestionCard({
  index,
  group,
  children,
}: {
  index: number;
  group: "new" | "deepen";
  children: React.ReactNode;
}) {
  return (
    <article
      className={cardStyle("static", {
        className: "flex h-full gap-4 p-5 sm:p-6",
      })}
    >
      <OrderBadge index={index} group={group} />
      <div className="flex min-w-0 grow flex-col gap-2.5">{children}</div>
    </article>
  );
}

/**
 * 새로 시작할 것.
 *
 * 만든 게 없어도 착수할 수 있는 제안입니다. 번호는 여러 개를 한꺼번에
 * 벌이라는 뜻이 아니라 위에서부터 하나씩 보라는 뜻이고, 순서는 파이프라인이
 * 준 순서를 그대로 씁니다.
 */
export function NewSuggestions({
  suggestions,
  byId,
  domainLabel,
}: {
  suggestions: Analysis["suggestions"]["new"];
  byId: Map<string, Evidence>;
  domainLabel: (id: string) => string | undefined;
}) {
  return (
    <ol className="grid grid-cols-1 gap-3 lg:grid-cols-2">
      {suggestions.map((s, index) => (
        <li key={s.id}>
          <SuggestionCard index={index} group="new">
            <CardMeta
              domain={domainLabel(s.domainId)}
              juniorDemand={s.juniorDemand}
            />
            <h3 className="text-h3 font-semibold text-pretty">{s.title}</h3>
            <p className="text-body-sm leading-[1.8] text-ink-soft">{s.body}</p>
            <EvidenceLinks ids={s.evidenceIds} byId={byId} />
          </SuggestionCard>
        </li>
      ))}
    </ol>
  );
}

/**
 * 이미 만든 것을 발전시킬 것 — A를 만들었다면 → B.
 *
 * 출발점(from)이 자유 문장이라 경험 입력 항목과 대조되지 않습니다. 지금은
 * 고른 경험과 무관하게 모든 제안을 보여줍니다.
 */
export function DeepenSuggestions({
  suggestions,
  byId,
  domainLabel,
}: {
  suggestions: Analysis["suggestions"]["deepen"];
  byId: Map<string, Evidence>;
  domainLabel: (id: string) => string | undefined;
}) {
  return (
    <ul className="grid grid-cols-1 gap-3 lg:grid-cols-2">
      {suggestions.map((s, index) => (
        <li key={s.id}>
          <SuggestionCard index={index} group="deepen">
            <CardMeta
              domain={domainLabel(s.domainId)}
              juniorDemand={s.juniorDemand}
            />
            {/* 무엇을 만들었던 사람에게 하는 말인지 제목보다 먼저 밝힙니다. */}
            <p className="flex items-center gap-1.5 text-body-sm text-ink-muted">
              {s.from}
              <ArrowRightIcon size={13} className="shrink-0" />
            </p>
            <h3 className="-mt-1.5 text-h3 font-semibold text-pretty">
              {s.to}
            </h3>
            <p className="text-body-sm leading-[1.8] text-ink-soft">{s.body}</p>
            <EvidenceLinks ids={s.evidenceIds} byId={byId} />
          </SuggestionCard>
        </li>
      ))}
    </ul>
  );
}
