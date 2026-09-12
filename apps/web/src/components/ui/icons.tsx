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
