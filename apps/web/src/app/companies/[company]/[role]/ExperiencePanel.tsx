"use client";

import type { ExperienceCatalog } from "@/types/data";
import { describeExperience } from "@/lib/personalize";
import { useExperience, clearExperience } from "@/lib/experience-store";
import { beginMatchFlow } from "@/lib/match-flow-store";
import { routes } from "@/lib/routes";
import { ArrowRightIcon } from "@/components/ui/icons";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";

/**
 * 경험은 결과를 규정하는 조건이라 제안 목록보다 **위**에 둡니다.
 *
 * 전에는 제안을 다 읽고 난 맨 아래에 있었습니다. 일곱 장을 읽고 나서야 "사실
 * 더 정확하게 볼 수 있었어요" 라고 말하는 셈이라, 눌러도 이미 늦은 자리였습니다.
 *
 * 카드가 아니라 한 줄입니다. 이 화면의 주인공은 아래 제안이고, 경험은 그
 * 제안을 어떻게 볼지 정하는 단서입니다. 카드로 세우면 제안과 무게를 다툽니다.
 *
 * 넣기 전과 넣은 뒤가 같은 자리를 씁니다. 자리가 다르면 입력을 마치고
 * 돌아왔을 때 아래 내용이 통째로 밀립니다.
 */
export function ExperiencePanel({
  catalog,
  role,
  returnTo,
}: {
  catalog: ExperienceCatalog;
  role: string;
  returnTo: string;
}) {
  const input = useExperience(catalog.version);
  const experienceHref = routes.matchRepository(role);
  const prepareExperienceFlow = () => beginMatchFlow(role, returnTo);

  if (!input) {
    return (
      /* 문구가 이 화면을 더 정확하게 만든다고 말하지 않습니다. 지금은 넣어도
         아래 목록이 그대로입니다. 대신 경험이 실제로 쓰이는 곳 — 맞는 회사
         찾기 — 으로 가는 입구라고 밝힙니다. */
      <ButtonLink
        variant="secondary"
        href={experienceHref}
        onClick={prepareExperienceFlow}
        className="justify-between gap-4 px-4 font-normal"
      >
        <span className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
          <span className="font-mono text-meta text-accent">$ cat</span>
          <span className="text-body-sm">
            만든 것을 알려주면 맞는 회사까지 찾아드립니다
          </span>
        </span>
        <ArrowRightIcon size={16} className="shrink-0 text-accent" />
      </ButtonLink>
    );
  }

  const done = describeExperience(input, catalog, role);

  return (
    /* 한 줄입니다. 라벨·칩·조작이 세로로 쌓여 있었더니 내용은 세 덩어리인데
       블록만 커졌습니다. 칩이 늘어나면 왼쪽 안에서만 줄바꿈되고, 조작은 늘
       첫 줄 오른쪽에 붙어 있습니다. */
    <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2 rounded-card border border-line-strong bg-sunken px-4 py-2.5">
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-x-3 gap-y-1.5">
        <span className="flex shrink-0 items-center gap-1.5 font-mono text-meta text-ink-muted">
          <span className="text-accent">$</span>내 경험 {done.length}개
        </span>
        <ul className="flex flex-wrap gap-1.5">
          {done.map((item) => (
            <li key={`${item.origin}-${item.label}`}>
              <Chip className="px-2 py-0.5 text-ink-soft">{item.label}</Chip>
            </li>
          ))}
        </ul>
      </div>

      <div className="-mr-2 flex shrink-0 items-center">
        <ButtonLink
          variant="ghost"
          href={experienceHref}
          onClick={prepareExperienceFlow}
          className="min-h-8 px-2 py-1 text-caption"
        >
          고치기
        </ButtonLink>
        <Button
          variant="ghost"
          onClick={clearExperience}
          className="min-h-8 px-2 py-1 text-caption"
        >
          지우기
        </Button>
      </div>
    </div>
  );
}
