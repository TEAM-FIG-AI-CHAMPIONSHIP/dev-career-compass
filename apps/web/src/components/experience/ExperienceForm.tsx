"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ExperienceCatalog, ExperienceInput } from "@/types/data";
import { CheckOption, LevelOption } from "@/components/ui/CheckOption";
import { RepoField } from "@/components/ui/RepoField";
import { Button } from "@/components/ui/Button";
import { PlusIcon, ShieldIcon } from "@/components/ui/icons";
import { useExperience, saveExperience, clearExperience } from "@/lib/experience-store";

type Draft = { itemIds: string[]; levelId: string; repos: string[] };

const MAX_REPOS = 3;
const REPO_SHAPE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

/**
 * S3 경험 입력. 회사를 고른 흐름과 역매칭 흐름이 같은 폼을 씁니다.
 * 한 번 입력하면 다른 조합에서도 다시 묻지 않습니다.
 *
 * 최소 선택 개수를 강제하지 않습니다. 해당하는 것만 고르면 됩니다.
 */
export function ExperienceForm({
  catalog,
  jobSlug,
  returnTo,
}: {
  catalog: ExperienceCatalog;
  /** 직무별 항목을 걸러내는 데 씁니다. 없으면 공통 그룹만 보입니다. */
  jobSlug?: string;
  returnTo: string;
}) {
  const router = useRouter();

  // 저장된 값이 기본이고, 사용자가 손대면 그때부터 draft 를 씁니다.
  // effect 로 state 를 덮지 않아 하이드레이션 이후 한 번에 맞춰집니다.
  const stored = useExperience(catalog.version);
  const [draft, setDraft] = useState<Draft | null>(null);

  const current: Draft = draft ?? {
    itemIds: stored?.itemIds ?? [],
    levelId: stored?.levelId ?? catalog.levels[0]?.id ?? "",
    repos: stored?.repos?.length ? [...stored.repos] : [""],
  };
  const { itemIds, levelId, repos } = current;
  const edit = (patch: Partial<Draft>) => setDraft({ ...current, ...patch });

  const groups = catalog.groups.filter(
    (g) => !g.appliesTo || (jobSlug != null && g.appliesTo.includes(jobSlug)),
  );

  const toggle = (id: string) =>
    edit({
      itemIds: itemIds.includes(id)
        ? itemIds.filter((x) => x !== id)
        : [...itemIds, id],
    });

  const invalidRepos = repos.filter((r) => r.trim() !== "" && !REPO_SHAPE.test(r.trim()));

  const submit = () => {
    const input: ExperienceInput = {
      catalogVersion: catalog.version,
      itemIds,
      levelId,
      repos: repos.map((r) => r.trim()).filter((r) => r !== "" && REPO_SHAPE.test(r)),
    };
    saveExperience(input);
    setDraft(null);
    router.push(returnTo);
  };

  const reset = () => {
    clearExperience();
    setDraft({ itemIds: [], levelId: catalog.levels[0]?.id ?? "", repos: [""] });
  };

  return (
    <div className="flex flex-col gap-11 lg:flex-row lg:items-start lg:gap-12">
      <div className="flex max-w-3xl grow flex-col gap-11">
        {groups.map((group) => (
          <section key={group.id} className="flex flex-col gap-3.5">
            <div className="flex flex-wrap items-baseline gap-2.5 border-b border-ink pb-2.5">
              <h2 className="text-h3 font-semibold sm:text-[1.125rem]">{group.title}</h2>
              {group.caption && (
                <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
                  {group.caption}
                </span>
              )}
            </div>
            <div className="flex flex-col gap-2">
              {group.items.map((item) => (
                <CheckOption
                  key={item.id}
                  label={item.label}
                  description={item.description}
                  checked={itemIds.includes(item.id)}
                  onChange={() => toggle(item.id)}
                />
              ))}
            </div>
          </section>
        ))}

        <section className="flex flex-col gap-3.5">
          <div className="border-b border-ink pb-2.5">
            <h2 className="text-h3 font-semibold sm:text-[1.125rem]">
              가장 많이 판 프로젝트는 어디까지 갔나요
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
            {catalog.levels.map((level) => (
              <LevelOption
                key={level.id}
                step={level.step}
                title={level.title}
                description={level.description}
                selected={levelId === level.id}
                onSelect={() => edit({ levelId: level.id })}
              />
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-3.5">
          <div className="flex flex-wrap items-baseline gap-2.5 border-b border-line-strong pb-2.5">
            <h2 className="text-h3 font-semibold sm:text-[1.125rem]">GitHub 저장소</h2>
            <span className="font-mono text-[0.6875rem] tracking-[0.06em] text-ink-muted">
              선택 · 최대 {MAX_REPOS}개
            </span>
          </div>
          <div className="flex flex-col gap-2">
            {repos.map((repo, i) => (
              <RepoField
                key={i}
                value={repo}
                onChange={(next) =>
                  edit({ repos: repos.map((r, j) => (i === j ? next : r)) })
                }
                error={
                  repo.trim() !== "" && !REPO_SHAPE.test(repo.trim())
                    ? "사용자명/저장소 형태로 적어주세요."
                    : undefined
                }
              />
            ))}
            {repos.length < MAX_REPOS && (
              <button
                type="button"
                onClick={() => edit({ repos: [...repos, ""] })}
                className="inline-flex min-h-11 w-fit cursor-pointer items-center gap-2 rounded-btn border border-dashed border-line-strong px-3.5 py-3 text-[0.84375rem] leading-none text-accent"
              >
                <PlusIcon size={14} strokeWidth={1.7} />
                저장소 추가
              </button>
            )}
          </div>
        </section>

        <div className="flex flex-wrap items-center gap-3.5">
          <Button
            variant="primary"
            onClick={submit}
            disabled={invalidRepos.length > 0}
            className="min-h-12 px-6 py-4 text-[0.9375rem]"
          >
            내 경험에 맞춘 결과 보기
          </Button>
          <Button variant="ghost" onClick={reset}>
            입력 지우기
          </Button>
        </div>
      </div>

      <aside className="flex w-full shrink-0 flex-col gap-3.5 lg:w-80">
        <div className="flex flex-col gap-3 rounded-card border border-line-strong bg-surface p-[22px]">
          <div className="flex items-center gap-2.5">
            <ShieldIcon size={18} strokeWidth={1.5} className="text-stage-fit" />
            <span className="text-[0.90625rem] leading-[1.6] font-semibold">
              서버에 저장하지 않습니다
            </span>
          </div>
          <ul className="flex list-disc flex-col gap-2 pl-4">
            <li className="text-body-sm text-ink-soft">
              고른 항목은 이 브라우저에만 남습니다. 다른 회사를 볼 때 다시 쓰이고,
              언제든 지울 수 있습니다.
            </li>
            <li className="text-body-sm text-ink-soft">
              README 는 공개 저장소만 읽고 원문을 저장하지 않습니다.
            </li>
            <li className="text-body-sm text-ink-soft">저장소를 채점하지 않습니다.</li>
            <li className="text-body-sm text-ink-soft">
              공유 링크에는 이 입력이 들어가지 않습니다.
            </li>
          </ul>
        </div>
        <div className="flex flex-col gap-2 rounded-card bg-sunken p-[18px]">
          <span className="font-mono text-[0.6875rem] tracking-[0.06em] text-ink-soft">
            고른 항목
          </span>
          <span className="text-h1 leading-[1.4] font-semibold">{itemIds.length}개</span>
          <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
            적게 골라도 결과는 나옵니다. 최소 개수를 강제하지 않습니다.
          </span>
        </div>
      </aside>
    </div>
  );
}
