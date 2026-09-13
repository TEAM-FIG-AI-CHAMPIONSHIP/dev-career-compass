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
            /* 회사 선택(`/companies`)의 회사 카드와 같은 모양입니다. 고르는
               화면이 둘인데 서로 다르게 생기면, 한쪽에서 익힌 "이건 누르는
               것" 이 다른 쪽에서 다시 시작됩니다.

               터미널이라는 인상은 카드가 아니라 위 `$ jobs --list` 한 줄이
               맡습니다 — `/companies` 도 `$ ls ./companies` 위에 평범한
               카드를 둡니다. */
            <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {jobs.map((job) => (
                <li key={job.slug} className="flex">
                  <CardLink
                    href={routes.matchRepository(job.slug)}
                    className="flex min-h-24 w-full items-center justify-between gap-3 p-4"
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-h3 font-semibold">
                        {job.name}
                      </span>
                      {/* 회사 수는 알약 배지에 넣지 않습니다. 누를 수도 없고
                          상태도 아닌 값이라, 회사 카드의 "N개 직무" 와 같은
                          고정폭 한 줄로 둡니다. */}
                      <span className="mt-0.5 block font-mono text-meta text-ink-muted tabular-nums">
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
