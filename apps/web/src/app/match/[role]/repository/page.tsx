import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { RepositoryForm } from "@/components/experience/RepositoryForm";
import { PageHeader } from "@/components/ui/PageHeader";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "GitHub 저장소 선택" };

export default async function MatchRepositoryPage({ params }: Props) {
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
            살펴볼 GitHub 저장소를 골라주세요
          </h1>
          <p className="text-body text-ink-soft">
            직접 만든 공개 저장소를 최대 3개까지 입력할 수 있습니다. 아직 고르기
            어렵다면 건너뛰고 경험부터 입력해도 됩니다.
          </p>
        </div>

        <RepositoryForm role={role} catalogVersion={catalog.version} />
      </main>
    </>
  );
}
