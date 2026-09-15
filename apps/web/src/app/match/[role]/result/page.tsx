import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listRoles, listJobs, dataSource } from "@/lib/data";
import { DataSourceNote } from "@/components/ui/DataSourceNote";
import { StepHeader } from "@/components/ui/StepHeader";
import { CommandLine } from "@/components/ui/CommandLine";
import { ReverseResult } from "./ReverseResult";
import { PageWidth } from "@/components/ui/PageWidth";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 기반 회사 찾기" };

export default async function MatchResultPage({ params }: Props) {
  const { role } = await params;
  const job = listRoles().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  /* 직무 존재 여부는 listRoles(구조), 화면에 보여줄 회사 수는 listJobs(내용)
     에서 옵니다. 이 직무에 아직 매칭 가능한 회사가 없으면 0입니다 — 그 경우
     에도 화면 자체는 열려야 합니다. */
  const companyCount =
    listJobs().find((candidate) => candidate.slug === role)?.companyCount ?? 0;

  const catalog = getExperienceCatalog();

  return (
    <>
      <StepHeader current="done" role={role} />

      <main className="grow py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <CommandLine>match --role {role}</CommandLine>
            <h1 className="text-display font-semibold text-pretty">
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
            companyCount={companyCount}
          />
        </PageWidth>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
