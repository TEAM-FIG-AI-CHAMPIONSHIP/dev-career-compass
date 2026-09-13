import type { SVGProps } from "react";

/**
 * 아이콘은 전부 인라인 SVG입니다. 이모지나 딩벳을 쓰지 않습니다 —
 * 크기가 제각각이고 색을 물려받지 못합니다.
 *
 * 20×20 그리드, stroke 기반, currentColor 상속.
 */

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function Icon({ size = 16, children, ...props }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      {children}
    </svg>
  );
}

export const CheckIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 10.5l4 4 8-9" />
  </Icon>
);

export const ArrowRightIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 10h11" />
    <path d="M11 6l4 4-4 4" />
  </Icon>
);

/** 터미널 창 표시. 프롬프트 꺾쇠와 입력 줄. */
export const TerminalIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 6l3.5 3.5L4 13" />
    <path d="M10.5 13.5H16" />
  </Icon>
);

/** 접힌 것을 펼치는 표시. 방향 이동을 뜻하는 화살표와 구분해서 씁니다. */
export const ChevronDownIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 8l5 5 5-5" />
  </Icon>
);

export const SearchIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="8.7" cy="8.7" r="4.8" />
    <path d="M12.3 12.3L16 16" />
  </Icon>
);

/** 랜딩 — 관심 회사를 먼저 고르는 흐름 */
export const BuildingIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4.5 17V5.2c0-.7.5-1.2 1.2-1.2h6.1c.7 0 1.2.5 1.2 1.2V17" />
    <path d="M13 8h1.8c.7 0 1.2.5 1.2 1.2V17" />
    <path d="M3 17h14" />
    <path d="M7.2 7h3.1M7.2 10h3.1M7.2 13h3.1" />
  </Icon>
);

/** 랜딩 — 내 경험에서 출발하는 흐름 */
export const PersonIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="6.2" r="2.8" />
    <path d="M4.8 17v-2.2c0-2.7 2.1-4.7 5.2-4.7s5.2 2 5.2 4.7V17" />
  </Icon>
);

export const PlusIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M10 4v12M4 10h12" />
  </Icon>
);

/** 심화 제안 — 층을 하나 더 쌓는다는 뜻 */

export const ExternalIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M8.5 5H5v10h10v-3.5" />
    <path d="M12 4h4v4" />
    <path d="M16 4l-6 6" />
  </Icon>
);

/** 개인정보 안내 */

export const AlertIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M10 6.4v4.2" />
    <path d="M10 13.4v.2" />
  </Icon>
);

/** 빈 상태 */
export const EmptyIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 5h12v10H4z" />
    <path d="M7 9h6" />
  </Icon>
);

/** 역매칭 3단계 중 "지금은 거리가 있어요" — 점선 원 */
export const DistantIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="6.4" strokeDasharray="3 3.4" />
  </Icon>
);

/** GitHub 저장소 입력 배지에 쓰는 아이콘. 로고를 그대로 쓰지 않고 기존 선 굵기·그리드에 맞춘 단순화 버전. */
export const GithubIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M6.6 5.4L4.3 3.5M13.4 5.4l2.3-1.9" />
    <circle cx="10" cy="10.6" r="5.3" />
    <path d="M7.7 13.3c.6.5 1.4.8 2.3.8s1.7-.3 2.3-.8" />
  </Icon>
);

/** ArrowRightIcon의 좌우 반전. 뒤로 가기 링크에 쓴다. */
export const ArrowLeftIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M17 10H6" />
    <path d="M9 6l-4 4 4 4" />
  </Icon>
);
