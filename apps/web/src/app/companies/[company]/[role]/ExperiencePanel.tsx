"use client";

import type { ExperienceCatalog } from "@/types/data";
import { describeExperience } from "@/lib/personalize";
import { useExperience, clearExperience } from "@/lib/experience-store";
import { beginMatchFlow } from "@/lib/match-flow-store";
import { routes } from "@/lib/routes";
import { ArrowRightIcon } from "@/components/ui/icons";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card, CardLink } from "@/components/ui/Card";

/**
 * 경험을 넣기 전의 유도 카드와 넣은 뒤의 요약이 같은 자리를 씁니다.
 *
 * 자리가 다르면 입력을 마치고 돌아왔을 때 화면 아래에 있던 것이 위로 올라가
 * 페이지가 통째로 밀립니다. 두 상태의 여백을 맞춰 두면 내용만 바뀝니다.
 *
 * 넣은 경험은 카드 격자로 다시 펼치지 않습니다. 방금 자기가 입력한 값이라
 * 확인만 되면 충분하고, 이 화면의 주인공은 위의 제안입니다.
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
      <CardLink
        variant="cta"
        href={experienceHref}
        onClick={prepareExperienceFlow}
        className="flex items-center justify-between gap-4 p-5 sm:p-6"
      >
        <span className="flex flex-col gap-1">
          <span className="text-h3 font-semibold">
            내 경험을 넣으면 더 정확해져요
          </span>
          <span className="text-body-sm text-ink-soft">
            만든 것을 선택하면 다음 한 걸음을 좁혀드립니다
          </span>
        </span>
        <ArrowRightIcon size={20} className="shrink-0 text-accent" />
      </CardLink>
    );
  }

  const done = describeExperience(input, catalog, role);

  return (
    <Card className="flex flex-col gap-4 p-5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-h3 font-semibold">내 경험</h2>
        <div className="flex items-center gap-1">
          <ButtonLink
            variant="ghost"
            href={experienceHref}
            onClick={prepareExperienceFlow}
          >
            고치기
          </ButtonLink>
          <Button variant="ghost" onClick={clearExperience}>
            지우기
          </Button>
        </div>
      </div>

      <ul className="flex flex-wrap gap-1.5">
        {done.map((item) => (
          <li
            key={`${item.origin}-${item.label}`}
            className="rounded-pill bg-sunken px-2.5 py-1 text-caption break-all text-ink-soft"
          >
            {item.label}
          </li>
        ))}
      </ul>

      {/* 경험을 넣어도 위 목록이 그대로인 이유를 화면에서 밝힙니다. */}
      <p className="text-body-sm text-ink-muted">
        지금은 넣은 경험에 따라 위 제안의 순서나 표시가 달라지지 않습니다. 어떤
        제안이 먼저인지 가리는 규칙이 아직 정해지지 않았습니다. 연결 지점:{" "}
        <code className="font-mono text-caption">src/lib/personalize.ts</code> 의{" "}
        <code className="font-mono text-caption">personalize()</code>
      </p>
    </Card>
  );
}
