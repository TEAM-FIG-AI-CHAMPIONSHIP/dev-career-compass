import type { Metadata } from "next";
import { getExperienceCatalog } from "@/lib/data";
import { ExperienceForm } from "@/components/experience/ExperienceForm";
import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = { title: "내 경험" };

/**
 * S3 경험 입력. 회사를 고른 흐름과 역매칭 흐름이 이 화면을 함께 씁니다.
 *
 * from 과 job 은 쿼리로 받습니다. 어디로 돌아갈지와 어떤 직무 항목을 보일지만
 * 정하며, 사용자가 고른 값은 여기 들어가지 않습니다 — 그건 브라우저에만 남습니다.
 */
export default async function ExperiencePage({
  searchParams,
}: PageProps<"/experience">) {
  const params = await searchParams;
  const catalog = getExperienceCatalog();

  const job = typeof params.job === "string" ? params.job : undefined;
  const from = typeof params.from === "string" ? params.from : undefined;
  const returnTo = from && from.startsWith("/") ? from : "/";

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="here" className="text-[0.875rem] leading-[1.6] text-ink">
            내 경험
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

        <ExperienceForm catalog={catalog} jobSlug={job} returnTo={returnTo} />
      </main>
    </>
  );
}
