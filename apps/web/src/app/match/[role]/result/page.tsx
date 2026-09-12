import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs, dataSource } from "@/lib/data";
import { PageHeader, DataSourceNote } from "@/components/ui/PageHeader";
import { ReverseResult } from "./ReverseResult";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 기반 회사 찾기" };

export default async function MatchResultPage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="flow" className="text-[0.875rem] leading-[1.6] text-ink-soft">
            내 경험부터 보기
          </span>,
          <span key="role" className="text-[0.875rem] leading-[1.6] text-ink">
            {job.name}
          </span>,
        ]}
      />

      <main className="flex grow flex-col gap-11 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <span className="font-mono text-meta tracking-[0.06em] text-ink-muted">
            4 / 4
          </span>
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.014em] text-pretty sm:text-[1.875rem]">
            지금 경험으로 이야기가 통하는 조직부터
          </h1>
          <p className="text-body text-ink-soft">
            회사를 줄 세우지 않습니다. 세 갈래로 나눠 보여드리고, 어디를 고를지는
            당신이 정합니다.
          </p>
        </div>

        <ReverseResult
          catalog={catalog}
          role={job.slug}
          roleName={job.name}
          companyCount={job.companyCount}
        />
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
