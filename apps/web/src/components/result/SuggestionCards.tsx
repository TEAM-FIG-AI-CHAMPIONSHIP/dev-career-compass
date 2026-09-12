import type { Analysis, Evidence } from "@/types/data";
import { PlusIcon, ArrowRightIcon, CheckIcon } from "@/components/ui/icons";

function EvidenceLinks({ ids, byId }: { ids: string[]; byId: Map<string, Evidence> }) {
  const items = ids.map((id) => byId.get(id)).filter((e): e is Evidence => !!e);
  if (items.length === 0) return null;

  return (
    <div className="flex flex-col gap-1.5 border-t border-line pt-3">
      <span className="font-mono text-[0.71875rem] text-ink-soft">근거</span>
      {items.map((e) => (
        <div key={e.id} className="flex flex-col gap-0.5">
          <a
            href={e.url}
            target="_blank"
            rel="noreferrer"
            className="text-[0.8125rem] leading-[1.65]"
          >
            {e.title}
          </a>
          <span className="font-mono text-[0.71875rem] text-ink-muted">
            {e.publishedAt.slice(0, 7).replace("-", ".")} ·{" "}
            {e.source === "blog" ? "블로그" : "공고"}
          </span>
        </div>
      ))}
    </div>
  );
}

function JuniorBadge() {
  return (
    <span className="inline-flex w-fit items-center gap-1.5 rounded-pill border border-stage-fit-edge bg-stage-fit-tint px-2.5 py-1 text-caption leading-normal text-stage-fit">
      <CheckIcon size={13} strokeWidth={1.8} />
      신입 공고에서도 요구됨
    </span>
  );
}

/** 지금부터 만들면 좋을 것. 결과 페이지 최상단에 놓습니다. */
export function NewSuggestions({
  suggestions,
  byId,
}: {
  suggestions: Analysis["suggestions"]["new"];
  byId: Map<string, Evidence>;
}) {
  return (
    <div className="grid grid-cols-1 items-start gap-3.5 md:grid-cols-2 lg:grid-cols-3">
      {suggestions.map((s) => (
        <article
          key={s.id}
          className="flex flex-col gap-3 rounded-card border border-line-strong bg-surface p-6"
        >
          <div className="flex items-center gap-2 text-accent">
            <PlusIcon size={16} strokeWidth={1.6} />
            <span className="font-mono text-[0.71875rem] tracking-[0.06em]">NEW</span>
          </div>
          <h3 className="text-[1.0625rem] leading-[1.55] font-semibold text-pretty">
            {s.title}
          </h3>
          <p className="text-[0.90625rem] leading-[1.75] text-ink-soft">{s.body}</p>
          {s.juniorDemand && <JuniorBadge />}
          <EvidenceLinks ids={s.evidenceIds} byId={byId} />
        </article>
      ))}
    </div>
  );
}

/** 이미 만든 게 있다면 — A를 만들었다면 → B. */
export function DeepenSuggestions({
  suggestions,
  byId,
}: {
  suggestions: Analysis["suggestions"]["deepen"];
  byId: Map<string, Evidence>;
}) {
  return (
    <div className="flex flex-col gap-2.5">
      {suggestions.map((s) => (
        <article
          key={s.id}
          className="flex flex-col gap-5 rounded-card border border-line bg-surface p-6 lg:flex-row lg:items-start lg:gap-6"
        >
          <div className="flex shrink-0 flex-col gap-2 lg:w-[22rem]">
            <span className="text-[0.875rem] leading-[1.7] text-ink-soft">{s.from}</span>
            <div className="flex items-start gap-2">
              <ArrowRightIcon
                size={17}
                strokeWidth={1.7}
                className="mt-1 shrink-0 text-accent"
              />
              <span className="text-[0.96875rem] leading-[1.6] font-semibold">{s.to}</span>
            </div>
          </div>
          <p className="grow text-[0.90625rem] leading-[1.75] text-ink-soft">{s.body}</p>
          <div className="shrink-0 lg:w-56">
            <EvidenceLinks ids={s.evidenceIds} byId={byId} />
          </div>
        </article>
      ))}
    </div>
  );
}
