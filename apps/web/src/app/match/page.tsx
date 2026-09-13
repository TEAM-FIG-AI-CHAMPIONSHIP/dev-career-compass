import type { Metadata } from "next";
import { listJobs } from "@/lib/data";
import { routes } from "@/lib/routes";
import { CardLink } from "@/components/ui/Card";
import { ButtonLink } from "@/components/ui/Button";
import { StepNav } from "@/components/ui/StepNav";
import { PageWidth } from "@/components/ui/PageWidth";
import { StepHeader } from "@/components/ui/StepHeader";
import { CommandLine } from "@/components/ui/CommandLine";
import { ArrowLeftIcon, ArrowRightIcon } from "@/components/ui/icons";
import { Empty } from "@/components/ui/state/Empty";

export const metadata: Metadata = { title: "직무 선택" };

/** 경험 기반 탐색의 1단계. 고른 직무는 이후 모든 단계의 경로에 남습니다. */
export default function MatchPage() {
  const jobs = listJobs();

  return (
    <>
      <StepHeader current={1} role="" />

      <main className="grow py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <CommandLine>jobs --list</CommandLine>
            <h1 className="text-display font-semibold text-pretty">
              어떤 직무를 찾고 있나요?
            </h1>
            <p className="text-body text-ink-soft">
              직무를 선택하면, GitHub 저장소와 경험을 입력하고 맞는 회사를 찾을
              수 있어요.
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
            /* 직무 수가 아직 정해지지 않았습니다. 2열은 개수가 홀수여도 마지막
             한 칸만 남고, 늘어나면 행이 늘 뿐이라 개수에 휘둘리지 않습니다. */
            <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {jobs.map((job) => (
                <li key={job.slug}>
                  <CardLink
                    href={routes.matchRepository(job.slug)}
                    className="flex h-full min-h-11 items-center justify-between gap-3 p-[18px]"
                  >
                    <span className="flex flex-col gap-1.5">
                      <span className="text-[0.9375rem] leading-[1.6] font-semibold text-ink">
                        {job.name}
                      </span>
                      <span className="w-fit rounded-pill bg-sunken px-2.5 py-1 text-[0.8125rem] leading-[1.5] text-ink-soft">
                        {job.companyCount}곳 매칭 가능
                      </span>
                    </span>
                    <ArrowRightIcon
                      size={18}
                      className="shrink-0 text-ink-muted"
                    />
                  </CardLink>
                </li>
              ))}
            </ul>
          )}
          <StepNav
            back={
              <ButtonLink variant="secondary" href={routes.home}>
                <ArrowLeftIcon size={14} strokeWidth={1.7} />
                처음으로
              </ButtonLink>
            }
          />
        </PageWidth>
      </main>
    </>
  );
}
