"use client";

import Link from "next/link";
import type { ExperienceCatalog } from "@/types/data";
import { describeExperience, type Stage } from "@/lib/personalize";
import { useExperience, clearExperience } from "@/lib/experience-store";
import { StageBadge, STAGE_ORDER } from "@/components/ui/StageBadge";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";

const STAGE_NOTE: Record<Stage, string> = {
  fit: "지금 가진 것으로 바로 한 겹 더 팔 수 있는 조직입니다",
  step: "하나만 더 해두면 이야기가 이어집니다",
  far: "못 간다는 뜻이 아니라, 지금 준비하기엔 순서가 뒤라는 뜻입니다",
};

/**
 * S6 역매칭 결과.
 *
 * 3단계를 항상 모두 노출합니다. "지금은 거리가 있어요" 를 비우지 않습니다.
 * 회사를 줄 세우지 않으며 점수·퍼센트·순위를 표시하지 않습니다.
 *
 * 분류 규칙은 아직 없습니다. 지어내지 않고 비어 있다는 것을 그대로 보여줍니다.
 */
export function ReverseResult({
  catalog,
  jobSlug,
  jobName,
  companyCount,
}: {
  catalog: ExperienceCatalog;
  jobSlug: string;
  jobName: string;
  companyCount: number;
}) {
  const input = useExperience(catalog.version);

  const experienceHref = `/experience?job=${jobSlug}&from=${encodeURIComponent(`/match?job=${jobSlug}`)}`;

  if (!input) {
    return (
      <div className="flex flex-col items-start gap-5 rounded-card border border-accent bg-accent-tint p-[26px]">
        <div className="flex flex-col gap-1.5">
          <p className="text-[1.03125rem] leading-[1.55] font-semibold">
            해본 것을 먼저 알려주세요
          </p>
          <p className="max-w-2xl text-[0.875rem] leading-[1.75] text-ink-soft">
            {jobName} 을 여는 회사 {companyCount}곳과 대조하려면 지금까지 만든 것이
            필요합니다. 고른 값은 이 브라우저에만 남습니다.
          </p>
        </div>
        <Link
          href={experienceHref}
          className="inline-flex min-h-11 items-center rounded-btn border border-accent bg-accent px-5 py-3 text-[0.875rem] leading-none font-medium text-white no-underline transition-colors hover:border-accent-ink hover:bg-accent-ink hover:no-underline"
        >
          내 경험 입력하기
        </Link>
      </div>
    );
  }

  const done = describeExperience(input, catalog);

  return (
    <div className="flex flex-col gap-11">
      <section className="flex flex-col gap-3.5">
        <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line-strong pb-2.5">
          <div className="flex flex-wrap items-baseline gap-3">
            <h2 className="text-h2 font-semibold">이미 한 것</h2>
            <span className="text-body-sm text-ink-soft">
              이걸 기준으로 아래를 나눕니다
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={experienceHref}
              className="text-[0.84375rem] text-ink-soft no-underline hover:text-ink"
            >
              입력 고치기
            </Link>
            <Button
              variant="ghost"
              className="px-3 py-2 text-[0.84375rem]"
              onClick={clearExperience}
            >
              입력 지우기
            </Button>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {done.map((d) => (
            <Chip key={`${d.origin}-${d.label}`} className="font-normal">
              {d.label}
            </Chip>
          ))}
        </div>
      </section>

      {STAGE_ORDER.map((stage) => (
        <section key={stage} className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-3.5">
            <StageBadge stage={stage} />
            <span className="text-[0.875rem] leading-[1.7] text-ink-soft">
              {STAGE_NOTE[stage]}
            </span>
          </div>
          <div className="rounded-card border border-dashed border-line-strong bg-surface p-6">
            <p className="text-body-sm text-ink-muted">
              아직 분류하지 않습니다.
            </p>
          </div>
        </section>
      ))}

      <div className="flex flex-col gap-3 rounded-card border border-dashed border-line-strong bg-surface p-6">
        <span className="font-mono text-[0.71875rem] tracking-[0.06em] text-ink-muted">
          아직 연결되지 않았습니다
        </span>
        <p className="max-w-2xl text-body text-ink-soft">
          경험과 각 조직을 대조해 3단계로 나누는 규칙이 아직 없습니다. 임시 규칙을
          넣으면 회사가 어딘가로 배정되지만, 그 배정에 근거가 없습니다. 그래서 세
          칸을 모두 열어 둔 채 비워 뒀습니다.
        </p>
        <p className="max-w-2xl text-body-sm text-ink-muted">
          연결 지점: <code className="font-mono">src/lib/personalize.ts</code> 의{" "}
          <code className="font-mono">reverseMatch()</code>
        </p>
      </div>
    </div>
  );
}
