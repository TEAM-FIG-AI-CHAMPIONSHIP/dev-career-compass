import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listRoles } from "@/lib/data";
import { ExperienceForm } from "@/components/experience/ExperienceForm";
import { StepHeader } from "@/components/ui/StepHeader";
import { CommandLine } from "@/components/ui/CommandLine";
import { PageWidth } from "@/components/ui/PageWidth";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "경험 입력" };

export default async function MatchExperiencePage({ params }: Props) {
  const { role } = await params;
  const job = listRoles().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <StepHeader current={3} role={role} />

      <main className="grow py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <CommandLine>experience --edit --role {role}</CommandLine>
            <h1 className="text-display font-semibold text-pretty">
              경험 입력
            </h1>
            <p className="text-body text-ink-soft">
              {job.name} 직무에서 맞는 회사를 찾기 위해 만들어 본 것을
              선택해주세요
            </p>
          </div>

          <ExperienceForm catalog={catalog} role={role} />
        </PageWidth>
      </main>
    </>
  );
}
