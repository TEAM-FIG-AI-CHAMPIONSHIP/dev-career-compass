"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ExperienceCatalog, ExperienceInput } from "@/types/data";
import { CheckboxCard, RadioCard } from "@/components/ui/CheckOption";
import { Button } from "@/components/ui/Button";
import { useExperience, saveExperience } from "@/lib/experience-store";
import { finishMatchFlow, useMatchFlow } from "@/lib/match-flow-store";
import { routes } from "@/lib/routes";
import { StepNav } from "@/components/ui/StepNav";
import { itemIdsFromRepositoryKeywords } from "@/lib/keyword-experience";
import { ArrowLeftIcon } from "@/components/ui/icons";

type Draft = { itemIds: string[]; levelId: string };

/**
 * S5 경험 입력. 회사를 고른 흐름과 역매칭 흐름이 같은 폼을 씁니다.
 *
 * 프로젝트 종류·직무별 경험·진행 수준은 각각 하나 이상 고릅니다.
 * 각 칸에서 몇 개를 더 고를지는 강제하지 않습니다.
 * 입력값은 이 브라우저에만 남기고 서버로 보내지 않습니다.
 */
export function ExperienceForm({
  catalog,
  role,
}: {
  catalog: ExperienceCatalog;
  /** 직무별 항목을 걸러내고 입력 흐름을 이어가는 데 씁니다. */
  role: string;
}) {
  const router = useRouter();
  const stored = useExperience(catalog.version);
  const flow = useMatchFlow(role);
  const [draft, setDraft] = useState<Draft | null>(null);

  const groups = catalog.groups.filter(
    (g) => !g.appliesTo || g.appliesTo.includes(role),
  );
  const allowedItemIds = new Set(
    groups.flatMap((group) => group.items.map((item) => item.id)),
  );
  const suggestedItemIds = itemIdsFromRepositoryKeywords(
    flow?.repositoryKeywords,
    allowedItemIds,
  );
  const suggestedItemIdSet = new Set(suggestedItemIds);

  const current: Draft = draft ?? {
    // 저장된 값이 있어도(빈 배열이어도) GitHub 키워드 제안을 항상 반영한다 —
    // ?? 는 빈 배열을 "값 있음"으로 보고 제안을 통째로 무시해 버리는 문제가 있었다.
    itemIds: [...new Set([...(stored?.itemIds ?? []), ...suggestedItemIds])],
    levelId: stored?.levelId ?? "",
  };
  const { itemIds, levelId } = current;

  const projectKindIds = new Set(
    groups
      .find((group) => group.id === "project-kind")
      ?.items.map((item) => item.id) ?? [],
  );
  const roleExperienceIds = new Set(
    groups
      .filter((group) => group.id !== "project-kind")
      .flatMap((group) => group.items.map((item) => item.id)),
  );
  const hasProjectKind = itemIds.some((id) => projectKindIds.has(id));
  const hasRoleExperience = itemIds.some((id) => roleExperienceIds.has(id));
  const hasLevel = catalog.levels.some((level) => level.id === levelId);
  const canSubmit = hasProjectKind && hasRoleExperience && hasLevel;

  const persist = (next: Draft) => {
    const input: ExperienceInput = {
      catalogVersion: catalog.version,
      itemIds: next.itemIds,
      levelId: next.levelId,
      repos: flow?.repositories ?? stored?.repos ?? [],
    };
    saveExperience(input);
    setDraft(next);
  };

  const toggle = (id: string) =>
    persist({
      ...current,
      itemIds: itemIds.includes(id)
        ? itemIds.filter((x) => x !== id)
        : [...itemIds, id],
    });

  const submit = () => {
    if (!canSubmit) return;
    const finished = finishMatchFlow(role);
    saveExperience({
      catalogVersion: catalog.version,
      itemIds,
      levelId,
      repos: finished.active ? finished.repositories : (stored?.repos ?? []),
    });
    setDraft(null);
    router.push(finished.returnTo);
  };

  const goBack = () => {
    router.push(routes.matchRepository(role));
  };

  return (
    <div className="flex flex-col gap-11">
      {groups.map((group) => (
        <section key={group.id} className="flex flex-col gap-3.5">
          <div className="flex flex-wrap items-baseline gap-2.5 border-b border-line-strong pb-2.5">
            <h2 className="text-h3 font-semibold sm:text-[1.125rem]">
              {group.id === "project-kind" ? "프로젝트 종류" : "직무별 경험"}
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {group.items.map((item) => (
              <CheckboxCard
                key={item.id}
                label={item.label}
                description={item.description}
                checked={itemIds.includes(item.id)}
                onChange={() => toggle(item.id)}
                badge={
                  suggestedItemIdSet.has(item.id) ? "GitHub 제안" : undefined
                }
              />
            ))}
          </div>
        </section>
      ))}

      <section className="flex flex-col gap-3.5">
        <div className="border-b border-line-strong pb-2.5">
          <h2 className="text-h3 font-semibold sm:text-[1.125rem]">
            프로젝트 진행 수준
          </h2>
        </div>
        <div
          role="radiogroup"
          aria-label="프로젝트 진행 수준"
          className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
        >
          {catalog.levels.map((level) => (
            <RadioCard
              key={level.id}
              step={level.step || undefined}
              title={level.title}
              description={level.description}
              selected={levelId === level.id}
              onSelect={() => persist({ ...current, levelId: level.id })}
            />
          ))}
        </div>
      </section>

      {!canSubmit && (
        <span className="text-[0.8125rem] leading-[1.7] text-ink-soft">
          프로젝트 종류, 직무별 경험, 진행 수준을 각각 하나 이상 골라 주세요
        </span>
      )}

      <StepNav
        back={
          <Button variant="secondary" onClick={goBack}>
            <ArrowLeftIcon size={14} strokeWidth={1.7} />
            GitHub 저장소
          </Button>
        }
        next={
          <Button variant="primary" onClick={submit} disabled={!canSubmit}>
            맞는 회사 찾기
          </Button>
        }
      />
    </div>
  );
}
