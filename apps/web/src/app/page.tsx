import { AppHeader } from "@/components/ui/AppHeader";
import { ArrowRightIcon } from "@/components/ui/icons";
import { routes } from "@/lib/routes";
import { CardLink } from "@/components/ui/Card";
import { PageWidth } from "@/components/ui/PageWidth";
import { PixelLogo, Wordmark } from "@/components/ui/PixelLogo";
import { TerminalWindow } from "@/components/ui/TerminalWindow";

/**
 * 진입 화면 — 회사와 경험, 두 탐색 경로의 책임만 가집니다.
 *
 * 설명을 제목으로 늘어놓지 않고 주석 두 줄로 줄인 뒤, 무엇을 해주는지는
 * 아래 터미널이 직접 보여줍니다. 말로 설명하는 것보다 한 번 실행해 보이는
 * 쪽이 짧습니다.
 */
export default function Home() {
  return (
    <>
      <AppHeader />

      <main className="flex grow flex-col items-center py-12 sm:py-14 lg:py-16">
        <PageWidth className="flex flex-col">
          <div className="mx-auto flex flex-col items-center gap-4 text-center motion-safe:animate-[landing-enter_320ms_ease-out_both]">
            <PixelLogo size={80} animated />
            <Wordmark className="text-[2rem] leading-none font-bold tracking-[-0.035em] sm:text-[2.75rem]" />
            {/* 태그라인은 셸 주석입니다. 설명이지 명령이 아니라는 뜻이 형식에
                드러나고, 흔한 마케팅 문장과도 목소리가 달라집니다. */}
            <div className="flex flex-col gap-0.5 font-mono text-caption text-comment">
              <p>
                # bridge the gap between your projects and real-world problems
              </p>
              <p># 기업이 반복해 푸는 문제에서 내 다음 프로젝트를 찾습니다</p>
            </div>
          </div>

          <HeroTerminal />

          <section
            aria-label="탐색 방법 선택"
            className="mx-auto mt-10 grid w-full max-w-4xl grid-cols-1 gap-3 motion-safe:animate-[landing-enter_320ms_ease-out_both] motion-safe:[animation-delay:120ms] sm:grid-cols-2"
          >
            <EntryCard
              href={routes.companies}
              command="cd ./companies"
              title="관심 회사 선택"
              body="고른 조직이 실제로 하는 일과 다음 한 걸음을 확인합니다."
              action="회사부터 선택하기"
            />
            <EntryCard
              href={routes.match}
              command="cat ./my-experience"
              title="내 경험으로 맞는 회사 찾기"
              body="내가 만든 것부터 보여주면 맞는 회사를 찾아드립니다."
              action="경험부터 시작하기"
            />
          </section>
        </PageWidth>
      </main>
    </>
  );
}

/**
 * 히어로 터미널.
 *
 * 여기 적힌 두 줄은 예시입니다. 실제 제안은 회사 결과 화면에서 근거와 함께
 * 나옵니다.
 *
 * 커서가 깜빡이는 곳은 화면 전체에서 여기 하나뿐입니다. 움직이는 것이 둘
 * 이상이면 어디를 봐야 할지 흩어집니다.
 */
function HeroTerminal() {
  return (
    <TerminalWindow
      title="refactor.me — bash"
      className="mx-auto mt-10 w-full max-w-3xl motion-safe:animate-[landing-enter_320ms_ease-out_both] motion-safe:[animation-delay:60ms]"
      bodyClassName="flex flex-col gap-1 p-5 sm:p-6"
    >
      <p className="text-ink">
        <span className="text-accent">$ </span>refactor diff --me --role backend
      </p>
      <p className="pl-5 text-ink-soft">
        <span className="text-ink-muted">&gt; </span>
        내가 만든 것과 기업이 푸는 문제를 맞춰 봅니다
      </p>

      <div className="my-3 flex flex-col">
        <p className="text-ink-muted">--- a/내가_만든_것</p>
        <p className="text-ink-muted">+++ b/회사가_푸는_문제</p>
        <p className="bg-warn-tint px-2 py-1 font-sans text-warn">
          - 주문 API에 페이지네이션을 붙였다
        </p>
        <p className="bg-stage-fit-tint px-2 py-1 font-sans text-stage-fit">
          + 품절이 실시간으로 섞여도 흔들리지 않는 목록
        </p>
      </div>

      <p className="pl-5 text-ink-soft">
        <span className="text-ink-muted">&gt; </span>1 file changed · 다음에
        만들 것이 정해졌습니다
      </p>
      <p className="mt-2 text-accent">
        ${" "}
        <span
          aria-hidden="true"
          className="inline-block h-[1.05em] w-[0.55em] translate-y-[0.15em] bg-ink motion-safe:animate-[caret-blink_1.06s_steps(1)_infinite]"
        />
      </p>
    </TerminalWindow>
  );
}

/** 두 갈래 진입 카드. 무엇을 하는 길인지 셸 명령으로 한 번 더 말합니다. */
function EntryCard({
  href,
  command,
  title,
  body,
  action,
}: {
  href: string;
  command: string;
  title: string;
  body: string;
  action: string;
}) {
  return (
    <CardLink href={href} className="group flex flex-col gap-2.5 p-5 sm:p-6">
      <span className="font-mono text-meta text-accent">$ {command}</span>
      <h2 className="text-h3 font-semibold text-balance">{title}</h2>
      <p className="max-w-md text-body-sm text-pretty text-ink-soft">{body}</p>
      <span className="mt-auto inline-flex min-h-9 items-center gap-2 pt-4 text-caption text-accent">
        {action}
        <ArrowRightIcon
          size={15}
          className="transition-transform duration-150 ease-out motion-safe:group-hover:translate-x-0.5 motion-reduce:transition-none"
        />
      </span>
    </CardLink>
  );
}
