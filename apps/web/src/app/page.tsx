import { ArrowRightIcon } from "@/components/ui/icons";
import { routes } from "@/lib/routes";
import { CardLink } from "@/components/ui/Card";
import { PageWidth } from "@/components/ui/PageWidth";
import { Wordmark } from "@/components/ui/PixelLogo";
import { TerminalWindow } from "@/components/ui/TerminalWindow";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

/**
 * 진입 화면 — 회사와 경험, 두 탐색 경로의 책임만 가집니다.
 *
 * 화면 전체가 창 하나입니다. 다른 화면은 상단 바 아래에 내용이 놓이지만,
 * 여기서는 창이 곧 페이지입니다. 처음 만나는 화면에서 "이건 터미널이다" 를
 * 한 번에 말하는 자리이기 때문입니다.
 *
 * 설명을 제목으로 늘어놓지 않고 주석 두 줄로 줄였습니다. 무엇을 해주는지는
 * 아래 두 카드가 셸 명령으로 말합니다.
 *
 * 상단 바를 두지 않습니다. 로고가 창 안에 큰 글자로 서 있는데 위에 또 작은
 * 로고를 두면 같은 이름이 두 번 보입니다. 테마 전환만 남깁니다.
 */
export default function Home() {
  return (
    <main className="flex grow flex-col py-5">
      <PageWidth className="flex grow flex-col gap-4">
        <div className="flex justify-end">
          <ThemeToggle />
        </div>

        {/* 창을 화면 가운데 둡니다. 위에 붙이면 아래가 통째로 비어 페이지가
            잘린 것처럼 보입니다. */}
        <div className="flex grow items-center">
          <TerminalWindow
            title="refactor.me — bash"
            className="w-full motion-safe:animate-[landing-enter_320ms_ease-out_both]"
            bodyClassName="flex min-h-[30rem] flex-col items-center justify-center gap-14 px-5 py-20 font-sans sm:px-8 sm:py-24 lg:min-h-[36rem] lg:py-32"
          >
            <div className="flex flex-col items-center gap-5 text-center">
              <Wordmark className="text-[2.75rem] leading-none font-extrabold sm:text-[4rem] lg:text-[4.75rem]" />
              {/* 태그라인은 셸 주석입니다. 설명이지 명령이 아니라는 뜻이 형식에
                드러나고, 흔한 마케팅 문장과도 목소리가 달라집니다. */}
              <div className="flex flex-col gap-1 font-mono text-body-sm text-comment">
                <p>
                  # bridge the gap between your projects and real-world problems
                </p>
                <p># 기업이 반복해 푸는 문제에서 내 다음 프로젝트를 찾습니다</p>
              </div>
            </div>

            <section
              aria-label="탐색 방법 선택"
              className="grid w-full max-w-4xl grid-cols-1 gap-3 sm:grid-cols-2"
            >
              <EntryCard
                href={routes.companies}
                command="cd ./companies"
                title="관심 회사 선택"
                body="고른 조직이 실제로 하는 일과 다음 한 걸음을 봅니다."
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
          </TerminalWindow>
        </div>
      </PageWidth>
    </main>
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
    <CardLink href={href} className="group flex flex-col gap-2.5 p-6 sm:p-7">
      <span className="font-mono text-meta text-accent uppercase">
        $ {command}
      </span>
      <h2 className="text-h3 font-semibold text-balance">{title}</h2>
      <p className="text-body-sm text-pretty text-ink-soft">{body}</p>
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
