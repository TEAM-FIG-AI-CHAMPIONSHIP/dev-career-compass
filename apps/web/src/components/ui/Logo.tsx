import { cn } from "@/lib/cn";

/**
 * 서비스 로고.
 *
 * 손으로 그린 픽셀 SVG 를 디자인 파일로 바꿨습니다. 파일은 라이트·다크 두
 * 벌입니다 — 색이 고정된 그림이라 `currentColor` 로 테마를 따라오게 할 수
 * 없습니다.
 *
 * 두 장을 모두 렌더하고 CSS 로 한 장을 숨깁니다(`theme-light-only` /
 * `theme-dark-only`). 자바스크립트로 고르면 첫 그림에서 잘못된 쪽이 한 번
 * 번쩍입니다. 대체 텍스트는 한 장에만 두어 읽는 프로그램이 이름을 두 번
 * 읽지 않게 합니다.
 *
 * 크기는 `className` 의 높이 하나로 정합니다. 가로는 원본 비율을 따라갑니다 —
 * 폭을 따로 주면 픽셀 그림이 눌립니다. `width`/`height` 속성은 그리기 전에
 * 자리를 잡아 두어 글자가 밀리지 않게 하는 용도입니다.
 *
 *  brand  워드마크만 — 상단 바
 *  main   우주선과 워드마크 — 진입 화면
 */

const LOGOS = {
  brand: {
    light: "/logo/refactor-me-brand-logo-light.svg",
    dark: "/logo/refactor-me-brand-logo-dark.svg",
    width: 1387,
    height: 195,
  },
  main: {
    light: "/logo/refactor-me-main-logo-light.svg",
    dark: "/logo/refactor-me-main-logo-dark.svg",
    width: 2018,
    height: 599,
  },
} as const;

function Logo({
  kind,
  className,
}: {
  kind: keyof typeof LOGOS;
  className?: string;
}) {
  const logo = LOGOS[kind];
  const common = "block h-full w-auto";

  return (
    <span className={cn("inline-flex shrink-0 items-center", className)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={logo.light}
        alt="Refactor.me"
        width={logo.width}
        height={logo.height}
        className={cn("theme-light-only", common)}
      />
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={logo.dark}
        alt=""
        aria-hidden="true"
        width={logo.width}
        height={logo.height}
        className={cn("theme-dark-only", common)}
      />
    </span>
  );
}

/** 상단 바. 워드마크만 들어갑니다 — 우주선은 진입 화면 몫입니다. */
export function BrandLogo({ className }: { className?: string }) {
  return <Logo kind="brand" className={cn("h-5", className)} />;
}

/** 진입 화면. 우주선과 워드마크가 함께 들어갑니다. */
export function MainLogo({ className }: { className?: string }) {
  return <Logo kind="main" className={cn("h-12 sm:h-24 lg:h-28", className)} />;
}
