import type { Metadata } from "next";
import { listJobs, listRoles, getRoleCatalog } from "@/lib/data";
import { routes } from "@/lib/routes";
import { CardLink } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { ButtonLink } from "@/components/ui/Button";
import { StepNav } from "@/components/ui/StepNav";
import { PageWidth } from "@/components/ui/PageWidth";
import { StepHeader } from "@/components/ui/StepHeader";
import { CommandLine } from "@/components/ui/CommandLine";
import { ArrowLeftIcon, ArrowRightIcon } from "@/components/ui/icons";
import { Empty } from "@/components/ui/state/Empty";

export const metadata: Metadata = { title: "직무 선택" };

/**
 * 경험 기반 탐색의 1단계. 고른 직무는 이후 모든 단계의 경로에 남습니다.
 *
 * 매칭 가능한 회사가 아직 없는 직무도 목록에서 뺴지 않습니다. 뺴면 그
 * 직무의 저장소·경험 입력 화면을 팀이 미리 열어 보거나 개발할 방법이
 * 클릭만으로는 없어집니다 — URL을 알아야만 들어갈 수 있는 화면이 됩니다.
 * 대신 회사 수를 있는 그대로(0도 포함해) 적어서, 고른 뒤에 무엇을 보게
 * 될지 미리 알 수 있게 합니다.
 *
 * 각 직무 아래 세부 트랙은 **이름표일 뿐 고를 수 없습니다.** 설계 문서(§8)는
 * "세부 트랙은 확인한 경험을 통해 복수로 연결될 수 있다"고 정해 뒀습니다 —
 * 사용자가 여기서 하나 찍는 값이 아니라, 나중에 경험을 확인하는 과정에서
 * 자동으로 붙는 값입니다. 그 연결은 Claude 판정(설계 §11)이 생긴 뒤의
 * 일이라 아직 없고, 지금은 "이 직무 안에 이런 세부 분야가 있다"는 미리보기
 * 까지만 합니다.
 */
export default function MatchPage() {
  const counts = new Map(listJobs().map((job) => [job.slug, job.companyCount]));
  const tracksByRole = new Map(
    getRoleCatalog().roles.map((role) => [role.id, role.tracks]),
  );
  const jobs = listRoles()
    .map((role) => ({
      ...role,
      companyCount: counts.get(role.slug) ?? 0,
      tracks: tracksByRole.get(role.slug) ?? [],
    }))
    .sort(
      (a, b) => b.companyCount - a.companyCount || a.slug.localeCompare(b.slug),
    );

  return (
    <>
      <StepHeader current={1} role="" />

      <main className="grow py-12 lg:py-14">
        <PageWidth className="flex flex-col gap-11">
          <div className="flex max-w-3xl flex-col gap-3">
            <CommandLine>jobs --list</CommandLine>
            <h1 className="text-display font-semibold text-pretty">
              어떤 직무를 찾고 있나요?
            </h1>
            <p className="text-body text-ink-soft">
              직무를 선택하면, GitHub 저장소와 경험을 입력하고 맞는 회사를 찾을
              수 있어요.
            </p>
          </div>

          {jobs.length === 0 ? (
            <div className="max-w-3xl">
              <Empty
                title="아직 고를 직무가 없습니다"
                description="근거가 충분히 모인 조합이 생기면 여기에 나타납니다."
              />
            </div>
          ) : (
            /* 회사 선택(`/companies`)의 회사 카드와 같은 모양입니다. 고르는
               화면이 둘인데 서로 다르게 생기면, 한쪽에서 익힌 "이건 누르는
               것" 이 다른 쪽에서 다시 시작됩니다.

               터미널이라는 인상은 카드가 아니라 위 `$ jobs --list` 한 줄이
               맡습니다 — `/companies` 도 `$ ls ./companies` 위에 평범한
               카드를 둡니다.

               세부 트랙 줄이 늘어나면서 가로 한 줄(items-center)로는 자리가
               안 나 세로로 쌓는 모양으로 바꿨습니다. 화살표는 이름과 같은
               줄 오른쪽 끝에 남겨 눌리는 자리라는 것은 그대로 알아볼 수
               있게 합니다. */
            <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {jobs.map((job) => (
                <li key={job.slug} className="flex">
                  <CardLink
                    href={routes.matchRepository(job.slug)}
                    className="flex w-full flex-col gap-3 p-4"
                  >
                    <span className="flex items-start justify-between gap-3">
                      <span className="min-w-0">
                        <span className="block truncate text-h3 font-semibold">
                          {job.name}
                        </span>
                        {/* 회사 수는 알약 배지에 넣지 않습니다. 누를 수도
                            없고 상태도 아닌 값이라, 회사 카드의 "N개 직무" 와
                            같은 고정폭 한 줄로 둡니다. */}
                        <span className="mt-0.5 block font-mono text-meta text-ink-muted tabular-nums">
                          {job.companyCount}곳 매칭 가능
                        </span>
                      </span>
                      <ArrowRightIcon
                        size={18}
                        className="mt-0.5 shrink-0 text-ink-muted"
                      />
                    </span>

                    {job.tracks.length > 0 && (
                      <ul className="flex flex-wrap gap-1.5">
                        {job.tracks.map((track) => (
                          <li key={track.id}>
                            <Chip className="px-2 py-0.5">{track.label}</Chip>
                          </li>
                        ))}
                      </ul>
                    )}
                  </CardLink>
                </li>
              ))}
            </ul>
          )}

          <StepNav
            back={
              <ButtonLink variant="secondary" href={routes.home}>
                <ArrowLeftIcon size={14} strokeWidth={1.7} />
                처음으로
              </ButtonLink>
            }
          />
        </PageWidth>
      </main>
    </>
  );
}
