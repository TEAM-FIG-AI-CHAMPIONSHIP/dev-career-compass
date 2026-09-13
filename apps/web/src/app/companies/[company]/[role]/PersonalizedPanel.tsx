"use client";

import Link from "next/link";
import type { ExperienceCatalog } from "@/types/data";
import { describeExperience, describeUnchosen } from "@/lib/personalize";
import { useExperience, clearExperience } from "@/lib/experience-store";
import { beginMatchFlow } from "@/lib/match-flow-store";
import { routes } from "@/lib/routes";
import { ArrowRightIcon, CheckIcon } from "@/components/ui/icons";
import { Button } from "@/components/ui/Button";

export function PersonalizedPanel({
  catalog,
  role,
  returnTo,
}: {
  catalog: ExperienceCatalog;
  role: string;
  returnTo: string;
}) {
  const input = useExperience(catalog.version);
  const experienceHref = routes.matchRepository(role);
  const prepareExperienceFlow = () => beginMatchFlow(role, returnTo);

  if (!input) {
    return (
      <Link
        href={experienceHref}
        onClick={prepareExperienceFlow}
        className="flex items-center justify-between gap-4 rounded-card border border-accent bg-accent-tint p-5 text-ink no-underline transition-colors hover:border-accent-ink hover:no-underline sm:p-6"
      >
        <span className="flex flex-col gap-1">
          <span className="text-[1.0625rem] leading-[1.55] font-semibold">
            내 경험을 넣으면 더 정확해져요
          </span>
          <span className="text-[0.875rem] leading-[1.75] text-ink-soft">
            만든 것을 선택하면 다음 한 걸음을 좁혀드립니다
          </span>
        </span>
        <ArrowRightIcon size={20} className="shrink-0 text-accent" />
      </Link>
    );
  }

  const done = describeExperience(input, catalog, role);
  const gaps = describeUnchosen(input, catalog, role);

  return (
    <div className="flex flex-col gap-11">
      <section className="flex flex-col gap-4">
        <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line-strong pb-2.5">
          <div className="flex flex-wrap items-baseline gap-3">
            <h2 className="text-h2 font-semibold">이미 한 것</h2>
            <span className="text-body-sm text-ink-soft">
              여기는 다시 만들 필요가 없습니다
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={experienceHref}
              onClick={prepareExperienceFlow}
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
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {done.map((item) => (
            <div
              key={`${item.origin}-${item.label}`}
              className="flex items-start gap-2.5 rounded-card border border-line bg-surface p-4"
            >
              <CheckIcon
                size={17}
                strokeWidth={1.9}
                className="mt-0.5 shrink-0 text-stage-fit"
              />
              <div className="flex flex-col gap-0.5">
                <span className="text-[0.90625rem] leading-[1.65] font-medium break-all">
                  {item.label}
                </span>
                <span className="font-mono text-[0.71875rem] text-ink-muted">
                  {item.origin}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <div className="flex flex-wrap items-baseline gap-3 border-b border-ink pb-2.5">
          <h2 className="text-h2 font-semibold">다음 단계</h2>
          <span className="text-body-sm text-ink-soft">
            여러 개 벌이지 말고 이것 하나만
          </span>
        </div>
        <NotWiredYet />
      </section>

      <section className="flex flex-col gap-4">
        <div className="flex flex-wrap items-baseline gap-3 border-b border-line-strong pb-2.5">
          <h2 className="text-h2 font-semibold">아직 빈 곳</h2>
          <span className="text-body-sm text-ink-soft">
            지금 손대라는 뜻은 아닙니다. 다음 단계를 끝낸 뒤 돌아오세요
          </span>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {gaps.map((gap) => (
            <div
              key={`${gap.origin}-${gap.label}`}
              className="flex flex-col gap-1.5 rounded-card border border-dashed border-line-strong bg-surface p-5"
            >
              <span className="text-[0.9375rem] leading-[1.6] font-semibold text-ink-soft">
                {gap.label}
              </span>
              <span className="font-mono text-[0.71875rem] text-ink-muted">
                {gap.origin}
              </span>
            </div>
          ))}
        </div>
        <p className="text-body-sm text-ink-muted">
          지금은 고르지 않은 항목을 그대로 보여줍니다. 이 조직이 반복해서 다루는
          영역과 대조해 무엇이 먼저인지 가리는 부분은 아직 연결되지 않았습니다.
        </p>
      </section>
    </div>
  );
}

function NotWiredYet() {
  return (
    <div className="flex flex-col gap-3 rounded-card border border-dashed border-line-strong bg-surface p-6">
      <span className="font-mono text-[0.71875rem] tracking-[0.06em] text-ink-muted">
        아직 연결되지 않았습니다
      </span>
      <p className="max-w-2xl text-body text-ink-soft">
        어떤 제안을 다음 한 걸음으로 고를지 정하는 규칙이 아직 없습니다. 임시 규칙을
        넣으면 화면은 채워지지만 근거 없는 판단이 그대로 나가게 되어, 비워 둡니다.
      </p>
      <p className="max-w-2xl text-body-sm text-ink-muted">
        연결 지점: <code className="font-mono">src/lib/personalize.ts</code> 의{" "}
        <code className="font-mono">personalize()</code>
      </p>
    </div>
  );
}
