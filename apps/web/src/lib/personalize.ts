import type { Analysis, ExperienceInput, ExperienceCatalog } from "@/types/data";

/**
 * 개인화(S4)와 역매칭(S6)의 판단 부분입니다.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * 아직 구현하지 않았습니다. 의도한 공백입니다.
 *
 * "다음 단계로 무엇을 고를지", "이 회사가 지금 경험과 얼마나 가까운지" 는
 * 판단이 필요한 일이고, 그 규칙이 아직 정해지지 않았습니다. 임시로 키워드
 * 매칭 같은 것을 넣으면 화면은 그럴듯해지지만 근거 없는 판단이 사용자에게
 * 나가게 됩니다. 그래서 자리만 만들어 두고 비워 뒀습니다.
 *
 * 규칙이 정해지면(LLM 이든 결정적 코드든) 아래 두 함수만 채우면 됩니다.
 * 화면은 이미 결과가 없는 상태를 그릴 수 있게 되어 있습니다.
 * ─────────────────────────────────────────────────────────────────────────
 */

/** 판단 없이 표시만 하면 되는 부분. 사용자가 고른 것을 그대로 보여줍니다. */
export type AlreadyDone = {
  label: string;
  /** 어디서 온 값인지 — 체크 항목인지 진행 수준인지 저장소인지 */
  origin: string;
};

export type NextStep = {
  /** 이미 만든 것 위에 얹는 제안이면 그 출발점 */
  from?: string;
  title: string;
  body: string;
  evidence: { title: string; url: string; publishedAt: string; source: string }[];
  reason: string;
};

export type Gap = {
  label: string;
  body: string;
};

export type PersonalizedResult = {
  nextStep: NextStep;
  gaps: Gap[];
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
export function describeExperience(
  input: ExperienceInput,
  catalog: ExperienceCatalog,
): AlreadyDone[] {
  const out: AlreadyDone[] = [];
  const chosen = new Set(input.itemIds);

  for (const group of catalog.groups) {
    for (const item of group.items) {
      if (chosen.has(item.id)) out.push({ label: item.label, origin: group.title });
    }
  }

  const level = catalog.levels.find((l) => l.id === input.levelId);
  if (level) out.push({ label: level.title, origin: "진행 수준" });

  for (const repo of input.repos ?? []) {
    out.push({ label: repo, origin: "GitHub 저장소" });
  }
  return out;
}

/** 고르지 않은 항목. 판단이 아니라 뺄셈이라 지금도 정확합니다. */
export function describeUnchosen(
  input: ExperienceInput,
  catalog: ExperienceCatalog,
): AlreadyDone[] {
  const chosen = new Set(input.itemIds);
  const out: AlreadyDone[] = [];
  for (const group of catalog.groups) {
    for (const item of group.items) {
      if (!chosen.has(item.id)) out.push({ label: item.label, origin: group.title });
    }
  }
  return out;
}

/**
 * 다음 한 걸음을 고릅니다. 미구현 — 규칙이 정해지면 여기를 채웁니다.
 *
 * 채울 때 지킬 것:
 *  - 제안은 반드시 analysis 안의 근거에 연결되어야 합니다. 없는 근거를 만들지 않습니다.
 *  - 점수나 퍼센트를 만들어 내지 않습니다.
 */
export function personalize(
  _analysis: Analysis,
  _input: ExperienceInput,
): PersonalizedResult | null {
  return null;
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
