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
export const LayersIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 7l7-3 7 3-7 3-7-3z" />
    <path d="M3 12l7 3 7-3" />
  </Icon>
);

export const ChevronDownIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 8l5 5 5-5" />
  </Icon>
);

export const ChevronUpIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 12l5-5 5 5" />
  </Icon>
);

export const ExternalIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M8.5 5H5v10h10v-3.5" />
    <path d="M12 4h4v4" />
    <path d="M16 4l-6 6" />
  </Icon>
);

/** 개인정보 안내 */
export const ShieldIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M10 2.8l6 2.4v4.2c0 3.9-2.5 6.3-6 7.4-3.5-1.1-6-3.5-6-7.4V5.2l6-2.4z" />
  </Icon>
);

export const AlertIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M10 6.4v4.2" />
    <path d="M10 13.4v.2" />
  </Icon>
);

export const InfoIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M10 9.4v4" />
    <path d="M10 6.6v.2" />
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

export const CompassIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M12.9 7.1l-1.5 4.3-4.3 1.5 1.5-4.3z" />
  </Icon>
);

export const SparkleIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M8 3l1.4 3.6L13 8l-3.6 1.4L8 13l-1.4-3.6L3 8l3.6-1.4z" />
    <path d="M14.5 12l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z" />
  </Icon>
);

export const CircleCheckIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M6.8 10.2l2.2 2.2 4.2-4.6" />
  </Icon>
);

export const ClockIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="10" cy="10" r="7.2" />
    <path d="M10 6v4.3l2.8 1.7" />
  </Icon>
);

export const TrendingUpIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3.5 13.5l4-4.2 3 2.6 5.8-6" />
    <path d="M12.6 5.9h3.9v3.9" />
  </Icon>
);

export const DocumentIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M11.4 2.8H6a1.6 1.6 0 00-1.6 1.6v11.2A1.6 1.6 0 006 17.2h8a1.6 1.6 0 001.6-1.6V7z" />
    <path d="M11.4 2.8V7h4.2" />
  </Icon>
);

export const BriefcaseIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="2.8" y="6.2" width="14.4" height="10" rx="1.6" />
    <path d="M7.4 6.2V4.8a1.4 1.4 0 011.4-1.4h2.4a1.4 1.4 0 011.4 1.4v1.4" />
    <path d="M2.8 10.4h14.4" />
  </Icon>
);
