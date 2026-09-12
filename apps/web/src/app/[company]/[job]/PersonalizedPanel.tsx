"use client";

import Link from "next/link";
import type { ExperienceCatalog } from "@/types/data";
import { describeExperience, describeUnchosen } from "@/lib/personalize";
import { useExperience, clearExperience } from "@/lib/experience-store";
import { CheckIcon } from "@/components/ui/icons";
import { Button } from "@/components/ui/Button";

/**
 * S4 개인화 결과. S2 와 같은 URL 위에 얹힙니다 — 공유 링크에 개인화가 들어가면
 * 안 되기 때문입니다. 공유받은 사람의 브라우저에는 입력이 없으니 S2 만 보입니다.
 *
 * "이미 한 것" 은 사용자가 고른 것을 되읽어 주는 것이라 판단이 없고, 지금도
 * 정확합니다. "다음 단계" 와 "아직 빈 곳" 은 판단이 필요해 아직 비어 있습니다.
 */
export function PersonalizedPanel({
  catalog,
  experienceHref,
}: {
  catalog: ExperienceCatalog;
  experienceHref: string;
}) {
  const input = useExperience(catalog.version);

  // 입력이 없으면 개인화 유도 배너만 보입니다.
  if (!input) {
    return (
      <div className="flex flex-col items-start justify-between gap-5 rounded-card border border-accent bg-accent-tint p-[26px] sm:flex-row sm:items-center">
        <div className="flex flex-col gap-1.5">
          <p className="text-[1.03125rem] leading-[1.55] font-semibold">
            내 경험을 넣으면 더 정확해져요
          </p>
          <p className="max-w-2xl text-[0.875rem] leading-[1.75] text-ink-soft">
            해본 것을 몇 개 체크하면 위 제안 중에서 지금 당신에게 맞는 한 걸음만
            남깁니다. 고른 값은 이 브라우저에만 남고 서버로 보내지 않습니다.
          </p>
        </div>
        <Link
          href={experienceHref}
          className="inline-flex min-h-11 shrink-0 items-center rounded-btn border border-accent bg-accent px-5 py-3 text-[0.875rem] leading-none font-medium text-white no-underline transition-colors hover:border-accent-ink hover:bg-accent-ink hover:no-underline"
        >
          내 경험 넣기
        </Link>
      </div>
    );
  }

  const done = describeExperience(input, catalog);
  const gaps = describeUnchosen(input, catalog);

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
          {done.map((d) => (
            <div
              key={`${d.origin}-${d.label}`}
              className="flex items-start gap-2.5 rounded-card border border-line bg-surface p-4"
            >
              <CheckIcon
                size={17}
                strokeWidth={1.9}
                className="mt-0.5 shrink-0 text-stage-fit"
              />
              <div className="flex flex-col gap-0.5">
                <span className="text-[0.90625rem] leading-[1.65] font-medium">
                  {d.label}
                </span>
                <span className="font-mono text-[0.71875rem] text-ink-muted">
                  {d.origin}
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
          {gaps.map((g) => (
            <div
              key={`${g.origin}-${g.label}`}
              className="flex flex-col gap-1.5 rounded-card border border-dashed border-line-strong bg-surface p-5"
            >
              <span className="text-[0.9375rem] leading-[1.6] font-semibold text-ink-soft">
                {g.label}
              </span>
              <span className="font-mono text-[0.71875rem] text-ink-muted">
                {g.origin}
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

/**
 * 판단 로직이 들어갈 자리. 규칙이 정해지기 전까지 임시 결과를 지어내지 않고
 * 비어 있다는 사실을 그대로 보여줍니다.
 */
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
