import type { Metadata } from "next";
import Link from "next/link";
import { listJobs, getExperienceCatalog, dataSource } from "@/lib/data";
import { PageHeader, DataSourceNote } from "@/components/ui/PageHeader";
import { ArrowRightIcon, ShieldIcon } from "@/components/ui/icons";
import { Empty } from "@/components/ui/state/Empty";
import { ReverseResult } from "./ReverseResult";

export const metadata: Metadata = { title: "내 경험부터 보기" };

/**
 * S5 직무 목록 + S6 역매칭 결과.
 *
 * 한 경로에 둘을 둡니다. 회사 라우트가 루트(/{company}/{job})라 두 칸짜리 경로는
 * 전부 회사 것이라 /match/{job} 을 쓸 수 없고, S6 은 브라우저에 저장된 경험으로
 * 그려지므로 URL 이 결과를 대표하지도 않습니다.
 */
export default async function MatchPage({ searchParams }: PageProps<"/match">) {
  const params = await searchParams;
  const selected = typeof params.job === "string" ? params.job : undefined;

  const jobs = listJobs();
  const catalog = getExperienceCatalog();
  const current = jobs.find((j) => j.slug === selected);

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="here" className="text-[0.875rem] leading-[1.6] text-ink">
            내 경험부터 보기
          </span>,
          ...(current
            ? [
                <span key="job" className="text-[0.875rem] leading-[1.6] text-ink-soft">
                  {current.name}
                </span>,
              ]
            : []),
        ]}
      />

      <main className="flex grow flex-col gap-10 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.014em] text-pretty sm:text-[1.875rem]">
            {current ? "지금 경험으로 이야기가 통하는 조직부터" : "어떤 직무를 찾고 있나요"}
          </h1>
          <p className="text-body text-ink-soft">
            {current
              ? "회사를 줄 세우지 않습니다. 세 갈래로 나눠 보여드리고, 어디를 고를지는 당신이 정합니다."
              : "직무를 고르고 해본 것을 체크하면, 지금 경험과 가까운 조직부터 되짚어 드립니다. 회사를 먼저 정하지 않아도 됩니다."}
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
              {jobs.map((job) => {
                const active = job.slug === selected;
                return (
                  <Link
                    key={job.slug}
                    href={`/match?job=${job.slug}`}
                    className={`flex min-h-11 items-center gap-4 rounded-card border p-5 no-underline transition-colors sm:gap-5 sm:px-6 ${
                      active
                        ? "border-ink bg-surface"
                        : "border-line bg-paper hover:border-ink-muted hover:bg-surface"
                    } hover:no-underline`}
                  >
                    <span className="shrink-0 text-[1.0625rem] leading-[1.5] font-semibold text-ink sm:w-48">
                      {job.name}
                    </span>
                    <span className="ml-auto shrink-0 font-mono text-[0.8125rem] text-ink-soft">
                      {job.companyCount}곳
                    </span>
                    <ArrowRightIcon
                      size={18}
                      className={active ? "text-ink" : "text-ink-muted"}
                    />
                  </Link>
                );
              })}
            </div>
          )}
          <p className="text-[0.8125rem] leading-[1.7] text-ink-muted">
            회사 수가 많은 순서로 놓았습니다. 순위나 추천이 아니라 우리가 가진 근거의
            양입니다.
          </p>
        </section>

        {current ? (
          <ReverseResult
            catalog={catalog}
            jobSlug={current.slug}
            jobName={current.name}
            companyCount={current.companyCount}
          />
        ) : (
          <div className="flex flex-col gap-4 rounded-card border border-line-strong bg-surface p-[26px] sm:flex-row sm:gap-6">
            <span
              aria-hidden="true"
              className="flex size-11 shrink-0 items-center justify-center rounded-card bg-sunken font-mono text-[0.9375rem] font-medium text-ink-soft"
            >
              2
            </span>
            <div className="flex grow flex-col gap-1.5">
              <p className="text-[1.03125rem] leading-[1.55] font-semibold">
                그다음 해본 것을 체크합니다
              </p>
              <p className="max-w-2xl text-[0.875rem] leading-[1.75] text-ink-soft">
                회사를 골랐을 때와 똑같은 입력 화면을 씁니다. 이미 입력한 적이 있다면
                그대로 불러오니 다시 고르지 않아도 됩니다.
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-2.5 sm:border-l sm:border-line sm:pl-6">
              <ShieldIcon size={17} strokeWidth={1.5} className="text-stage-fit" />
              <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
                서버에 저장하지 않습니다
              </span>
            </div>
          </div>
        )}
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
