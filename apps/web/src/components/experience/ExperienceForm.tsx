"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ExperienceCatalog, ExperienceInput } from "@/types/data";
import { CheckboxCard, RadioCard } from "@/components/ui/CheckOption";
import { Button } from "@/components/ui/Button";
import { useExperience, saveExperience } from "@/lib/experience-store";
import { finishMatchFlow, useMatchFlow } from "@/lib/match-flow-store";
import { itemIdsFromRepositoryKeywords } from "@/lib/keyword-experience";
import { routes } from "@/lib/routes";

type Draft = { itemIds: string[]; levelId: string };

/**
 * S5 경험 입력. 회사를 고른 흐름과 역매칭 흐름이 같은 폼을 씁니다.
 *
 * 최소 선택 개수를 강제하지 않습니다. 해당하는 것만 고르면 됩니다.
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
  const allowedItemIds = new Set(groups.flatMap((group) => group.items.map((item) => item.id)));
  const suggestedItemIds = itemIdsFromRepositoryKeywords(
    flow?.repositoryKeywords,
    allowedItemIds,
  );

  const current: Draft = draft ?? {
    itemIds: stored?.itemIds ?? suggestedItemIds,
    levelId: stored?.levelId ?? "",
  };
  const { itemIds, levelId } = current;

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

  const cancel = () => {
    router.push(routes.matchRepository(role));
  };

  return (
    <div className="flex max-w-3xl flex-col gap-11">
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
          <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
            {group.items.map((item) => (
              <CheckboxCard
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
            프로젝트 진행 수준
          </h2>
        </div>
        <div
          role="radiogroup"
          aria-label="프로젝트 진행 수준"
          className="grid grid-cols-1 gap-2.5 sm:grid-cols-2"
        >
          {catalog.levels.map((level) => (
            <RadioCard
              key={level.id}
              name="experience-level"
              step={level.step || undefined}
              title={level.title}
              description={level.description}
              selected={levelId === level.id}
              onSelect={() => persist({ ...current, levelId: level.id })}
            />
          ))}
        </div>
      </section>

      <div className="flex flex-wrap items-center gap-3.5">
        <Button variant="secondary" onClick={cancel} className="min-h-12 px-6 py-4">
          취소
        </Button>
        <Button
          variant="primary"
          onClick={submit}
          className="min-h-12 px-6 py-4 text-[0.9375rem]"
        >
          맞는 회사 찾기
        </Button>
      </div>
    </div>
  );
}
