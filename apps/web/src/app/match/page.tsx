import type { Metadata } from "next";
import Link from "next/link";
import { listJobs, dataSource } from "@/lib/data";
import { routes } from "@/lib/routes";
import { PageHeader, DataSourceNote } from "@/components/ui/PageHeader";
import { ArrowRightIcon, ShieldIcon } from "@/components/ui/icons";
import { Empty } from "@/components/ui/state/Empty";

export const metadata: Metadata = { title: "직무 선택" };

/** 경험 기반 탐색의 첫 단계. URL에는 사용자가 선택한 직무만 경로로 남깁니다. */
export default function MatchPage() {
  const jobs = listJobs();

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="here" className="text-[0.875rem] leading-[1.6] text-ink">
            내 경험부터 보기
          </span>,
        ]}
      />

      <main className="flex grow flex-col gap-10 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <span className="font-mono text-meta tracking-[0.06em] text-ink-muted">
            1 / 4
          </span>
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.014em] text-pretty sm:text-[1.875rem]">
            어떤 직무를 찾고 있나요
          </h1>
          <p className="text-body text-ink-soft">
            직무를 먼저 고른 뒤 저장소와 경험을 차례로 확인합니다. 마지막에는 지금
            경험과 이야기가 통하는 회사를 세 갈래로 나눠 보여드립니다.
          </p>
        </div>

        <section className="flex flex-col gap-3.5">
          <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-ink pb-2.5">
            <h2 className="text-h3 font-semibold sm:text-[1.0625rem]">직무</h2>
            <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
              근거가 쌓인 회사가 있는 직무만 보여드립니다
            </span>
          </div>

          {jobs.length === 0 ? (
            <Empty
              title="아직 고를 직무가 없습니다"
              description="근거가 충분히 모인 조합이 생기면 여기에 나타납니다."
            />
          ) : (
            <div className="flex flex-col gap-2">
              {jobs.map((job) => (
                <Link
                  key={job.slug}
                  href={routes.matchRepository(job.slug)}
                  className="flex min-h-11 items-center gap-4 rounded-card border border-line bg-paper p-5 no-underline transition-colors hover:border-ink-muted hover:bg-surface hover:no-underline sm:gap-5 sm:px-6"
                >
                  <span className="shrink-0 text-[1.0625rem] leading-[1.5] font-semibold text-ink sm:w-48">
                    {job.name}
                  </span>
                  <span className="ml-auto shrink-0 font-mono text-[0.8125rem] text-ink-soft">
                    {job.companyCount}곳
                  </span>
                  <ArrowRightIcon size={18} className="text-ink-muted" />
                </Link>
              ))}
            </div>
          )}
        </section>

        <div className="flex flex-col gap-4 rounded-card border border-line-strong bg-surface p-[26px] sm:flex-row sm:gap-6">
          <span
            aria-hidden="true"
            className="flex size-11 shrink-0 items-center justify-center rounded-card bg-sunken font-mono text-[0.9375rem] font-medium text-ink-soft"
          >
            2–4
          </span>
          <div className="flex grow flex-col gap-1.5">
            <p className="text-[1.03125rem] leading-[1.55] font-semibold">
              저장소와 경험을 확인한 뒤 결과를 보여드립니다
            </p>
            <p className="max-w-2xl text-[0.875rem] leading-[1.75] text-ink-soft">
              이미 입력한 적이 있다면 브라우저에 남은 값을 불러오며, 언제든 고칠 수
              있습니다.
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2.5 sm:border-l sm:border-line sm:pl-6">
            <ShieldIcon size={17} strokeWidth={1.5} className="text-stage-fit" />
            <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
              서버에 저장하지 않습니다
            </span>
          </div>
        </div>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
