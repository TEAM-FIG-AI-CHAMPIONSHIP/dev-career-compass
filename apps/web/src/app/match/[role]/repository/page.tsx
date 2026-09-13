import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { RepositoryForm } from "@/components/experience/RepositoryForm";
import { StepHeader } from "@/components/ui/StepHeader";
import { CommandLine } from "@/components/ui/CommandLine";
import { PageWidth } from "@/components/ui/PageWidth";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "GitHub 저장소 선택" };

export default async function MatchRepositoryPage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <StepHeader current={2} role={role} />

      <main className="grow py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <CommandLine>github-scan --role {role}</CommandLine>
            <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
              GitHub 저장소 (선택)
            </h1>
            <p className="text-body text-ink-soft">
              공개 저장소를 살펴 표준 기술 키워드를 찾아 보여드립니다. 찾은
              키워드는 참고용이며, 다음 단계인 경험 입력에서 직접 고른 항목이
              우선합니다.
            </p>
            <p className="text-body-sm text-ink-muted">
              저장소 원문은 서버에 저장하지 않고, 공개 저장소만 조회합니다.
              비공개 저장소이거나 신호를 찾지 못하면 안내 후 그 저장소만
              건너뛰고 계속 진행합니다.
            </p>
          </div>

          <RepositoryForm role={role} catalogVersion={catalog.version} />
        </PageWidth>
      </main>
    </>
  );
}
