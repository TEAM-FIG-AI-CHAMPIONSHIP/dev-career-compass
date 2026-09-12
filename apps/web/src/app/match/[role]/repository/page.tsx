import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getExperienceCatalog, listJobs } from "@/lib/data";
import { RepositoryForm } from "@/components/experience/RepositoryForm";
import { ArrowLeftIcon, GithubIcon } from "@/components/ui/icons";
import { routes } from "@/lib/routes";

type Props = { params: Promise<{ role: string }> };

export const metadata: Metadata = { title: "GitHub 저장소 선택" };

export default async function MatchRepositoryPage({ params }: Props) {
  const { role } = await params;
  const job = listJobs().find((candidate) => candidate.slug === role);
  if (!job) notFound();

  const catalog = getExperienceCatalog();

  return (
    <>
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-4 sm:px-8 lg:px-20">
        <Link
          href={routes.home}
          className="inline-flex items-center gap-1.5 text-[0.875rem] text-ink-soft no-underline hover:text-ink hover:no-underline"
        >
          <ArrowLeftIcon size={14} strokeWidth={1.7} />
          처음으로
        </Link>
        <ol className="flex items-center gap-2 text-[0.8125rem]">
          <li className="text-ink-soft">1. 직무</li>
          <li aria-hidden="true" className="text-line-strong">
            →
          </li>
          <li className="font-semibold text-accent">2. GitHub</li>
          <li aria-hidden="true" className="text-line-strong">
            →
          </li>
          <li className="text-ink-soft">3. 경험</li>
        </ol>
      </header>

      <main className="flex grow flex-col gap-11 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <div className="flex max-w-3xl flex-col gap-3">
          <div className="flex size-11 items-center justify-center rounded-card bg-accent-tint text-accent">
            <GithubIcon size={22} strokeWidth={1.5} />
          </div>
          <h1 className="text-[1.75rem] leading-[1.4] font-semibold tracking-[-0.012em] text-pretty sm:text-[1.875rem]">
            GitHub 저장소 (선택)
          </h1>
          <p className="text-body text-ink-soft">
            공개 저장소를 살펴 표준 기술 키워드를 찾아 보여드립니다. 찾은 키워드는
            참고용이며, 다음 단계인 경험 입력에서 직접 고른 항목이 우선합니다.
          </p>
          <p className="text-body-sm text-ink-muted">
            저장소 원문은 서버에 저장하지 않고, 공개 저장소만 조회합니다. 비공개
            저장소이거나 신호를 찾지 못하면 안내 후 그 저장소만 건너뛰고 계속
            진행합니다.
          </p>
        </div>

        <RepositoryForm role={role} catalogVersion={catalog.version} />
      </main>
    </>
  );
}
