import type { Analysis, Evidence } from "@/types/data";
import { ArrowRightIcon, CheckIcon, ExternalIcon } from "@/components/ui/icons";
import { cardStyle } from "@/components/ui/Card";

/** 제안이 어느 영역에서 나왔는지. 카드 바닥에 알약으로 답니다. */
function DomainTag({ label }: { label?: string }) {
  if (!label) return null;
  return (
    <span className="w-fit rounded-pill bg-accent-tint px-2.5 py-1 text-[0.8125rem] leading-[1.5] text-accent">
      {label}
    </span>
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
    <details className="group border-t border-line pt-3">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 text-[0.8125rem] leading-[1.7] text-ink-muted hover:text-ink">
        근거 {items.length}건
        <ArrowRightIcon
          size={13}
          className="transition-transform group-open:rotate-90"
        />
      </summary>
      <ul className="mt-2 flex flex-col gap-1.5">
        {items.map((e) => (
          <li key={e.id}>
            <a
              href={e.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-start gap-1.5 text-[0.8125rem] leading-[1.65]"
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

function JuniorBadge() {
  return (
    <span className="inline-flex w-fit items-center gap-1.5 rounded-pill border border-accent bg-accent-tint px-2.5 py-1 text-caption leading-normal text-accent">
      <CheckIcon size={13} strokeWidth={1.8} />
      신입 공고에서도 요구됨
    </span>
  );
}

/**
 * 지금부터 만들면 좋을 것.
 *
 * 번호를 붙입니다. 여러 개를 한꺼번에 벌이라는 뜻이 아니라 위에서부터 하나씩
 * 보라는 뜻이고, 순서는 파이프라인이 준 순서를 그대로 씁니다.
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
    <ol className="grid grid-cols-1 items-start gap-3 lg:grid-cols-2">
      {suggestions.map((s, index) => (
        <li key={s.id}>
          <article className={cardStyle("static", { className: "flex gap-4 p-5 sm:gap-5 sm:p-6" })}>
            <span
              aria-hidden="true"
              className="flex size-8 shrink-0 items-center justify-center rounded-card bg-accent-tint text-[0.875rem] font-semibold text-accent"
            >
              {index + 1}
            </span>
            <div className="flex min-w-0 grow flex-col gap-2">
              <h3 className="text-[1.0625rem] leading-[1.55] font-semibold text-pretty">
                {s.title}
              </h3>
              <p className="text-[0.90625rem] leading-[1.75] text-ink-soft">
                {s.body}
              </p>
              <DomainTag label={domainLabel(s.domainId)} />
              {s.juniorDemand && <JuniorBadge />}
              <EvidenceLinks ids={s.evidenceIds} byId={byId} />
            </div>
          </article>
        </li>
      ))}
    </ol>
  );
}

/**
 * 이미 만든 게 있다면 — A를 만들었다면 → B.
 *
 * 위 무리와 같은 번호 배지를 쓰되 색을 달리합니다. 두 무리가 각각 1번부터
 * 시작하므로, 번호만으로는 어느 무리의 몇 번인지 구분되지 않습니다.
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
    <ul className="grid grid-cols-1 items-start gap-3 lg:grid-cols-2">
      {suggestions.map((s, index) => (
        <li key={s.id}>
          <article className={cardStyle("static", { className: "flex gap-4 p-5 sm:gap-5 sm:p-6" })}>
            <span
              aria-hidden="true"
              className="flex size-8 shrink-0 items-center justify-center rounded-card bg-accent-tint text-[0.875rem] font-semibold text-accent"
            >
              {index + 1}
            </span>
            <div className="flex min-w-0 grow flex-col gap-2">
              {/* 무엇을 만들었던 사람에게 하는 말인지 먼저 밝힙니다. */}
              <p className="flex flex-wrap items-center gap-2">
                <span className="rounded-pill border border-line-strong px-2.5 py-0.5 text-[0.8125rem] leading-[1.6] text-ink-soft">
                  {s.from}
                </span>
                <ArrowRightIcon size={14} className="text-ink-muted" />
              </p>
              <h3 className="text-[1.0625rem] leading-[1.55] font-semibold text-pretty">
                {s.to}
              </h3>
              <p className="text-[0.90625rem] leading-[1.75] text-ink-soft">
                {s.body}
              </p>
              <DomainTag label={domainLabel(s.domainId)} />
              {s.juniorDemand && <JuniorBadge />}
              <EvidenceLinks ids={s.evidenceIds} byId={byId} />
            </div>
          </article>
        </li>
      ))}
    </ul>
  );
}
