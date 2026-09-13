import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { ExperienceForm } from "@/components/experience/ExperienceForm";
import { StepHeader } from "@/components/ui/StepHeader";
import { PageWidth } from "@/components/ui/PageWidth";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 입력" };

export default async function MatchExperiencePage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <StepHeader current={3} />

      <main className="grow bg-[linear-gradient(180deg,var(--accent-tint)_0%,var(--paper)_20rem)] py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
              경험 입력
            </h1>
            <p className="text-body text-ink-soft">
              {job.name} 직무에서 맞는 회사를 찾기 위해 만들어 본 것을
              선택해주세요
            </p>
            <p className="text-body-sm text-ink-muted">
              입력값은 브라우저에 저장되며 서버에 전송되지 않습니다.
            </p>
          </div>

          <ExperienceForm catalog={catalog} role={role} />
        </PageWidth>
      </main>
    </>
  );
}
