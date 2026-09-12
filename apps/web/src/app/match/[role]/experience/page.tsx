import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { ExperienceForm } from "@/components/experience/ExperienceForm";
import { PageHeader } from "@/components/ui/PageHeader";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 입력" };

export default async function MatchExperiencePage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="flow" className="text-[0.875rem] leading-[1.6] text-ink-soft">
            경험 정보 입력
          </span>,
          <span key="role" className="text-[0.875rem] leading-[1.6] text-ink">
            {job.name}
          </span>,
        ]}
      />

      <main className="flex grow flex-col gap-11 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
            지금까지 해본 것을 골라주세요
          </h1>
          <p className="text-body text-ink-soft">
            몇 개를 골라야 한다는 기준은 없습니다. 해당하는 것만 고르면 됩니다. 고른
            내용은 이 브라우저에만 남고, 서버에는 저장하지 않습니다.
          </p>
        </div>

        <ExperienceForm catalog={catalog} role={role} />
      </main>
    </>
  );
}
