"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { RepoField } from "@/components/ui/RepoField";
import { PlusIcon, ShieldIcon } from "@/components/ui/icons";
import { useExperience } from "@/lib/experience-store";
import { saveMatchRepositories, useMatchFlow } from "@/lib/match-flow-store";
import { routes } from "@/lib/routes";

const MAX_REPOSITORIES = 3;
const REPOSITORY_SHAPE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

export function RepositoryForm({
  role,
  catalogVersion,
}: {
  role: string;
  catalogVersion: number;
}) {
  const router = useRouter();
  const flow = useMatchFlow(role);
  const experience = useExperience(catalogVersion);
  const [draft, setDraft] = useState<string[] | null>(null);

  const repositories =
    draft ??
    (flow?.repositories.length
      ? flow.repositories
      : experience?.repos?.length
        ? experience.repos
        : [""]);

  const invalid = repositories.some(
    (repository) =>
      repository.trim() !== "" && !REPOSITORY_SHAPE.test(repository.trim()),
  );

  const continueWith = (next: string[]) => {
    saveMatchRepositories(
      role,
      next
        .map((repository) => repository.trim())
        .filter((repository) => REPOSITORY_SHAPE.test(repository)),
    );
    router.push(routes.matchExperience(role));
  };

  return (
    <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:gap-12">
      <section className="flex max-w-3xl grow flex-col gap-5">
        <div className="flex flex-wrap items-baseline gap-2.5 border-b border-ink pb-2.5">
          <h2 className="text-h3 font-semibold sm:text-[1.125rem]">
            분석할 GitHub 저장소
          </h2>
          <span className="font-mono text-[0.6875rem] tracking-[0.06em] text-ink-muted">
            선택 · 최대 {MAX_REPOSITORIES}개
          </span>
        </div>

        <div className="flex flex-col gap-2">
          {repositories.map((repository, index) => (
            <RepoField
              key={index}
              value={repository}
              onChange={(next) =>
                setDraft(
                  repositories.map((current, currentIndex) =>
                    currentIndex === index ? next : current,
                  ),
                )
              }
              error={
                repository.trim() !== "" &&
                !REPOSITORY_SHAPE.test(repository.trim())
                  ? "사용자명/저장소 형태로 적어주세요."
                  : undefined
              }
            />
          ))}
          {repositories.length < MAX_REPOSITORIES && (
            <button
              type="button"
              onClick={() => setDraft([...repositories, ""])}
              className="inline-flex min-h-11 w-fit cursor-pointer items-center gap-2 rounded-btn border border-dashed border-line-strong px-3.5 py-3 text-[0.84375rem] leading-none text-accent"
            >
              <PlusIcon size={14} strokeWidth={1.7} />
              저장소 추가
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3.5">
          <Button
            variant="primary"
            onClick={() => continueWith(repositories)}
            disabled={invalid}
            className="min-h-12 px-6 py-4 text-[0.9375rem]"
          >
            다음: 경험 입력
          </Button>
          <Button variant="ghost" onClick={() => continueWith([])}>
            저장소 없이 계속
          </Button>
        </div>
      </section>

      <aside className="flex w-full shrink-0 flex-col gap-3 rounded-card border border-line-strong bg-surface p-[22px] lg:w-80">
        <div className="flex items-center gap-2.5">
          <ShieldIcon size={18} strokeWidth={1.5} className="text-stage-fit" />
          <span className="text-[0.90625rem] leading-[1.6] font-semibold">
            주소만 브라우저에 보관합니다
          </span>
        </div>
        <p className="text-body-sm text-ink-soft">
          공개 저장소를 최대 3개까지 고를 수 있습니다. 선택한 주소는 경험 입력을
          마칠 때까지 이 브라우저에만 남습니다.
        </p>
      </aside>
    </div>
  );
}
