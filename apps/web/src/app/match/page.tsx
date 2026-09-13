import type { Metadata } from "next";
import Link from "next/link";
import { listJobs } from "@/lib/data";
import { routes } from "@/lib/routes";
import { StepHeader } from "@/components/ui/StepHeader";
import { ArrowRightIcon, CompassIcon } from "@/components/ui/icons";
import { Empty } from "@/components/ui/state/Empty";

export const metadata: Metadata = { title: "직무 선택" };

/** 경험 기반 탐색의 1단계. 고른 직무는 이후 모든 단계의 경로에 남습니다. */
export default function MatchPage() {
  const jobs = listJobs();

  return (
    <>
      <StepHeader current={1} />

      <main className="flex grow flex-col gap-11 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <div className="flex size-11 items-center justify-center rounded-card bg-accent-tint text-accent">
            <CompassIcon size={22} strokeWidth={1.5} />
          </div>
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
            어떤 직무를 찾고 있나요?
          </h1>
          <p className="text-body text-ink-soft">
            직무를 선택하면, GitHub 저장소와 경험을 입력하고 맞는 회사를 찾을 수
            있어요.
          </p>
        </div>

        {jobs.length === 0 ? (
          <div className="max-w-3xl">
            <Empty
              title="아직 고를 직무가 없습니다"
              description="근거가 충분히 모인 조합이 생기면 여기에 나타납니다."
            />
          </div>
        ) : (
          /* 머리말은 줄이 길어지면 읽기 나쁘므로 max-w-3xl 로 묶고, 카드는
             그 상한을 풀어 화면 폭을 씁니다. 넓은 화면에서는 네 직무가 한 줄에
             들어와 오른쪽이 비지 않습니다. */
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {jobs.map((job) => (
              <li key={job.slug}>
                <Link
                  href={routes.matchRepository(job.slug)}
                  className="flex h-full min-h-11 items-center justify-between gap-3 rounded-card border border-line bg-surface p-[18px] no-underline transition-colors hover:border-ink-muted hover:no-underline"
                >
                  <span className="flex flex-col gap-1.5">
                    <span className="text-[0.9375rem] leading-[1.6] font-semibold text-ink">
                      {job.name}
                    </span>
                    <span className="w-fit rounded-pill bg-sunken px-2.5 py-1 text-[0.8125rem] leading-[1.5] text-ink-soft">
                      {job.companyCount}곳 매칭 가능
                    </span>
                  </span>
                  <ArrowRightIcon size={18} className="shrink-0 text-ink-muted" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  );
}
