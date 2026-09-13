import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs, dataSource } from "@/lib/data";
import { DataSourceNote } from "@/components/ui/DataSourceNote";
import { StepHeader } from "@/components/ui/StepHeader";
import { ReverseResult } from "./ReverseResult";
import { PageWidth } from "@/components/ui/PageWidth";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 기반 회사 찾기" };

export default async function MatchResultPage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <StepHeader current="done" role={role} />

      <main className="grow bg-[linear-gradient(180deg,var(--accent-tint)_0%,var(--paper)_20rem)] py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.014em] text-pretty sm:text-[1.875rem]">
              지금 경험으로 이야기가 통하는 조직부터
            </h1>
            <p className="text-body text-ink-soft">
              회사를 줄 세우지 않습니다. 세 갈래로 나눠 보여드리고, 어디를
              고를지는 당신이 정합니다.
            </p>
          </div>

          <ReverseResult
            catalog={catalog}
            role={job.slug}
            roleName={job.name}
            companyCount={job.companyCount}
          />
        </PageWidth>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
