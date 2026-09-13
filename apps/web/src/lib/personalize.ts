import type {
  Analysis,
  ExperienceInput,
  ExperienceCatalog,
} from "@/types/data";

/**
 * 고른 경험으로 화면을 조금 다르게 그리는 판단 부분입니다.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * 점수도 퍼센트도 만들지 않습니다.
 *
 * 판단은 하나뿐입니다 — 이 제안이 사용자가 고른 경험에 닿아 있는가. 데이터에
 * 적힌 `coversItemIds` / `fromItemIds` 와 고른 항목이 겹치는지만 봅니다.
 * 키워드를 추측해 맞추거나, 없는 근거를 만들어 순위를 매기지 않습니다.
 *
 * 역매칭(3단계로 회사를 나누는 일)은 아직 비어 있습니다. 그쪽은 규칙이
 * 정해지지 않았고, 임시 규칙을 넣으면 근거 없는 배정이 사용자에게 나갑니다.
 * ─────────────────────────────────────────────────────────────────────────
 */

/** 판단 없이 표시만 하면 되는 부분. 사용자가 고른 것을 그대로 보여줍니다. */
export type AlreadyDone = {
  label: string;
  /** 어디서 온 값인지 — 체크 항목인지 진행 수준인지 저장소인지 */
  origin: string;
};

export type Stage = "fit" | "step" | "far";

export type ReverseMatch = {
  company: { slug: string; name: string; mark?: string };
  stage: Stage;
  body: string;
  /** "한 걸음 필요해요" 일 때 그 한 걸음 */
  step?: string;
};

/**
 * 사용자가 고른 것을 사람이 읽을 수 있는 문장으로 바꿉니다.
 * 판단이 들어가지 않아 지금도 정확합니다 — 고른 것을 그대로 되읽어 줄 뿐입니다.
 */
function visibleGroups(catalog: ExperienceCatalog, role?: string) {
  return catalog.groups.filter(
    (group) => !group.appliesTo || !role || group.appliesTo.includes(role),
  );
}

export function describeExperience(
  input: ExperienceInput,
  catalog: ExperienceCatalog,
  role?: string,
): AlreadyDone[] {
  const out: AlreadyDone[] = [];
  const chosen = new Set(input.itemIds);

  for (const group of visibleGroups(catalog, role)) {
    for (const item of group.items) {
      if (chosen.has(item.id))
        out.push({ label: item.label, origin: group.title });
    }
  }

  const level = catalog.levels.find((l) => l.id === input.levelId);
  if (level) out.push({ label: level.title, origin: "진행 수준" });

  for (const repo of input.repos ?? []) {
    out.push({ label: repo, origin: "GitHub 저장소" });
  }
  return out;
}

/**
 * 고른 경험에 닿아 있는 제안을 가려냅니다.
 *
 * 제안마다 데이터에 적힌 경험 항목(`coversItemIds` 또는 `fromItemIds`)이
 * 있고, 그중 하나라도 고른 항목과 겹치면 "닿아 있다" 고 봅니다. 겹침은
 * 데이터에 적힌 사실이라 추측이 들어가지 않습니다.
 *
 * 경험을 넣지 않았거나 아무것도 고르지 않았으면 빈 집합입니다 — 화면은 아무
 * 표시 없이 원래 순서를 그립니다.
 */
export function groundedSuggestionIds(
  suggestions: { id: string; itemIds: string[] }[],
  input: ExperienceInput | null,
): Set<string> {
  if (!input || input.itemIds.length === 0) return new Set();
  const chosen = new Set(input.itemIds);
  return new Set(
    suggestions
      .filter(({ itemIds }) => itemIds.some((id) => chosen.has(id)))
      .map(({ id }) => id),
  );
}

/**
 * 전제가 있는 제안을 앞으로 보냅니다.
 *
 * "이미 만든 것을 발전시킬 것" 에만 씁니다. 출발점이 없는 사람에게는 제안
 * 자체가 성립하지 않아서, 성립하는 것부터 보는 편이 낫습니다. 같은 무리
 * 안에서는 데이터가 준 순서를 그대로 둡니다 — 무리 안에서 다시 줄을 세울
 * 근거가 없습니다.
 */
export function groundedFirst<T extends { id: string }>(
  suggestions: T[],
  grounded: Set<string>,
): T[] {
  if (grounded.size === 0) return suggestions;
  return [
    ...suggestions.filter((s) => grounded.has(s.id)),
    ...suggestions.filter((s) => !grounded.has(s.id)),
  ];
}

/**
 * 한 직무의 회사들을 3단계로 나눕니다. 미구현 — 규칙이 정해지면 여기를 채웁니다.
 *
 * 채울 때 지킬 것:
 *  - 3단계를 모두 노출합니다. "지금은 거리가 있어요" 를 비우지 않습니다.
 *  - 순위를 매기지 않습니다. 회사를 줄 세우는 화면이 아닙니다.
 */
export function reverseMatch(
  _analyses: Analysis[],
  _input: ExperienceInput,
): ReverseMatch[] | null {
  return null;
}
