import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import {
  ArrowRightIcon,
  BuildingIcon,
  PersonIcon,
} from "@/components/ui/icons";

/** 진입 화면 — 회사와 경험, 두 탐색 경로의 책임만 가집니다. */
export default function Home() {
  return (
    <>
      <PageHeader />

      <main className="flex grow flex-col px-4 pt-14 pb-12 sm:px-8 sm:pt-16 sm:pb-14 lg:px-12 lg:pt-20 lg:pb-16">
        <div className="mx-auto flex w-full max-w-6xl flex-col">
          <div className="mx-auto flex max-w-6xl flex-col items-center gap-5 text-center">
            <h1 className="text-[2.25rem] leading-[1.3] font-semibold tracking-[-0.022em] text-balance sm:text-[3rem]">
              기업이 풀고 있는 문제와 내 경험을 연결해,
              <br className="hidden sm:inline" />
              <span className="text-accent"> 다음 한 걸음</span>을 정하세요
            </h1>
            <p className="max-w-none text-[1rem] leading-[1.85] text-ink-soft sm:text-[1.03125rem] lg:whitespace-nowrap">
              기술 블로그와 채용 공고를 분석해 개발 조직이 반복해서 다루는 문제를
              찾고, 지금의 경험에 맞는 회사와 프로젝트 방향을 제안합니다.
            </p>
          </div>

          <section
            aria-label="탐색 방법 선택"
            className="mt-12 grid grid-cols-1 gap-4 sm:mt-14 lg:mt-16 lg:grid-cols-2 lg:gap-5"
          >
            <Link
              href="/companies"
              className="group flex min-h-[18rem] flex-col rounded-card border border-line-strong bg-surface p-[26px] text-ink no-underline shadow-raised transition-colors hover:border-accent hover:no-underline sm:p-9"
            >
              <span className="flex size-14 items-center justify-center rounded-card bg-accent-tint text-accent">
                <BuildingIcon size={29} strokeWidth={1.55} />
              </span>
              <h2 className="mt-7 text-[1.5rem] leading-[1.5] font-semibold">
                관심 회사 선택
              </h2>
              <p className="mt-3 max-w-md text-[1.0625rem] leading-[1.8] text-ink-soft">
                관심 있는 회사를 먼저 고르고,
                <br /> 그 조직이 실제로 하는 일과 다음 한 걸음을 확인합니다.
              </p>
              <span className="mt-auto inline-flex min-h-11 items-center gap-2 pt-6 text-base font-medium text-accent">
                회사부터 선택하기
                <ArrowRightIcon
                  size={18}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </Link>

            <Link
              href="/match"
              className="group flex min-h-[18rem] flex-col rounded-card border border-line-strong bg-surface p-[26px] text-ink no-underline shadow-raised transition-colors hover:border-stage-fit-edge hover:no-underline sm:p-9"
            >
              <span className="flex size-14 items-center justify-center rounded-card bg-stage-fit-tint text-stage-fit">
                <PersonIcon size={29} strokeWidth={1.55} />
              </span>
              <h2 className="mt-7 text-[1.5rem] leading-[1.5] font-semibold">
                내 경험으로 맞는 회사 찾기
              </h2>
              <p className="mt-3 max-w-md text-[1.0625rem] leading-[1.8] text-ink-soft">
                회사부터 정하기 어렵다면, 내가 만든 것부터 보여주세요.
                <br /> 경험과 맞는 회사를 찾아드립니다.
              </p>
              <span className="mt-auto inline-flex min-h-11 items-center gap-2 pt-6 text-base font-medium text-stage-fit">
                경험부터 시작하기
                <ArrowRightIcon
                  size={18}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </Link>
          </section>
        </div>
      </main>
    </>
  );
}
