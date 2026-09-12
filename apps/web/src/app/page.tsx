import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import {
  ArrowRightIcon,
  BuildingIcon,
  PersonIcon,
} from "@/components/ui/icons";
import { routes } from "@/lib/routes";

/** 진입 화면 — 회사와 경험, 두 탐색 경로의 책임만 가집니다. */
export default function Home() {
  return (
    <>
      <PageHeader />

      <main className="flex grow flex-col items-center justify-center bg-[radial-gradient(ellipse_at_50%_18%,var(--accent-tint)_0%,var(--paper)_62%)] px-4 py-12 sm:px-8 sm:py-14 lg:px-12 lg:py-16">
        <div className="mx-auto flex w-full max-w-6xl flex-col">
          <div className="mx-auto flex max-w-6xl flex-col items-center gap-5 text-center">
            <h1 className="max-w-5xl text-[2.25rem] leading-[1.3] font-semibold tracking-[-0.022em] text-balance motion-safe:animate-[landing-enter_320ms_ease-out_both] sm:text-[2.75rem]">
              기업이 풀고 있는 문제와 내 경험을 연결해,
              <br className="hidden sm:inline" />
              <span className="text-accent"> 다음 한 걸음</span>을 정하세요
            </h1>
            <p className="max-w-6xl break-keep text-[0.9375rem] leading-[1.85] text-pretty text-ink-soft motion-safe:animate-[landing-enter_320ms_ease-out_both] motion-safe:[animation-delay:60ms] sm:text-[1rem] xl:whitespace-nowrap">
              기술 블로그와 채용 공고를 분석해 개발 조직이 반복해서 다루는 문제를
              찾고, 지금의 경험에 맞는 회사와 프로젝트 방향을 제안합니다.
            </p>
          </div>

          <section
            aria-label="탐색 방법 선택"
            className="mx-auto mt-10 grid w-full max-w-4xl grid-cols-1 gap-3.5 motion-safe:animate-[landing-enter_320ms_ease-out_both] motion-safe:[animation-delay:120ms] sm:mt-12 lg:mt-14 lg:grid-cols-2 lg:gap-4"
          >
            <Link
              href={routes.companies}
              className="group flex min-h-[15rem] flex-col rounded-card border border-line-strong bg-surface p-5 text-ink no-underline shadow-raised transition-colors hover:border-accent hover:no-underline motion-safe:transition-[transform,border-color] motion-safe:duration-150 motion-safe:ease-out motion-safe:hover:-translate-y-1 sm:p-6"
            >
              <span className="flex size-11 items-center justify-center rounded-card bg-accent-tint text-accent">
                <BuildingIcon size={23} strokeWidth={1.55} />
              </span>
              <h2 className="mt-5 text-h2 font-semibold text-balance">
                관심 회사 선택
              </h2>
              <p className="mt-2 max-w-md text-body text-pretty text-ink-soft">
                관심 있는 회사를 먼저 고르고,
                <br /> 그 조직이 실제로 하는 일과 다음 한 걸음을 확인합니다.
              </p>
              <span className="mt-auto inline-flex min-h-9 items-center gap-2 pt-4 text-body-sm font-medium text-accent">
                회사부터 선택하기
                <ArrowRightIcon
                  size={16}
                  className="transition-transform duration-150 ease-out motion-safe:group-hover:translate-x-0.5 motion-reduce:transition-none"
                />
              </span>
            </Link>

            <Link
              href={routes.match}
              className="group flex min-h-[15rem] flex-col rounded-card border border-line-strong bg-surface p-5 text-ink no-underline shadow-raised transition-colors hover:border-accent hover:no-underline motion-safe:transition-[transform,border-color] motion-safe:duration-150 motion-safe:ease-out motion-safe:hover:-translate-y-1 sm:p-6"
            >
              <span className="flex size-11 items-center justify-center rounded-card bg-stage-fit-tint text-stage-fit">
                <PersonIcon size={23} strokeWidth={1.55} />
              </span>
              <h2 className="mt-5 text-h2 font-semibold text-balance">
                내 경험으로 맞는 회사 찾기
              </h2>
              <p className="mt-2 max-w-md text-body text-pretty text-ink-soft">
                회사부터 정하기 어렵다면, 내가 만든 것부터 보여주세요.
                <br /> 경험과 맞는 회사를 찾아드립니다.
              </p>
              <span className="mt-auto inline-flex min-h-9 items-center gap-2 pt-4 text-body-sm font-medium text-accent">
                경험부터 시작하기
                <ArrowRightIcon
                  size={16}
                  className="transition-transform duration-150 ease-out motion-safe:group-hover:translate-x-0.5 motion-reduce:transition-none"
                />
              </span>
            </Link>
          </section>
        </div>
      </main>
    </>
  );
}
