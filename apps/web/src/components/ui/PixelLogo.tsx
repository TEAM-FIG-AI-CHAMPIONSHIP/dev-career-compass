/**
 * 픽셀 로고.
 *
 * 28×24 격자 위의 사각형만으로 그립니다. `crispEdges` 라 어떤 크기에서도
 * 픽셀 경계가 흐려지지 않습니다.
 *
 * 색을 고정하지 않습니다. 흰 부분은 `currentColor` 를 물려받고, 눈·입·화면
 * 안쪽처럼 뚫려 보여야 하는 부분만 바탕색을 칠합니다. 그래서 상단 바에서는
 * 글자색으로, 다른 곳에서는 강조색으로 같은 파일을 씁니다.
 *
 * 움직임은 CSS 로 둡니다. SVG 자체 애니메이션은 동작 줄이기 설정을 따르지
 * 않습니다.
 */
export function PixelLogo({
  size = 120,
  animated = false,
  className,
}: {
  size?: number;
  animated?: boolean;
  className?: string;
}) {
  const ink = "currentColor";
  const hole = "var(--paper)";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 24"
      shapeRendering="crispEdges"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      className={className}
    >
      <g
        className={
          animated
            ? "motion-safe:animate-[pixel-bob_2.8s_ease-in-out_infinite]"
            : undefined
        }
      >
        {/* 얼굴 */}
        <rect x="4" y="0" width="1" height="3" fill={ink} />
        <rect x="8" y="0" width="1" height="3" fill={ink} />
        <rect x="3" y="2" width="7" height="1" fill={ink} />
        <rect x="2" y="3" width="9" height="1" fill={ink} />
        <rect x="2" y="4" width="9" height="1" fill={ink} />
        <rect x="2" y="5" width="9" height="1" fill={ink} />
        <rect x="3" y="6" width="7" height="1" fill={ink} />
        <rect x="4" y="7" width="5" height="1" fill={ink} />

        {/* 눈과 입 — 바탕이 비쳐 보이는 자리 */}
        <rect x="3" y="3" width="2" height="2" fill={hole} />
        <rect x="7" y="3" width="2" height="2" fill={hole} />
        <rect x="3" y="3" width="1" height="1" fill={ink} />
        <rect x="7" y="3" width="1" height="1" fill={ink} />
        <rect x="5" y="6" width="2" height="1" fill={hole} />

        {/* 화면 테두리 */}
        <rect x="11" y="5" width="16" height="1" fill={ink} />
        <rect x="11" y="6" width="1" height="11" fill={ink} />
        <rect x="26" y="6" width="1" height="11" fill={ink} />
        <rect x="11" y="17" width="16" height="1" fill={ink} />
        <rect x="12" y="6" width="14" height="10" fill={hole} />

        {/* 화면 안의 꺾쇠 */}
        <rect x="16" y="8" width="1" height="1" fill={ink} />
        <rect x="15" y="9" width="1" height="1" fill={ink} />
        <rect x="14" y="10" width="1" height="1" fill={ink} />
        <rect x="15" y="11" width="1" height="1" fill={ink} />
        <rect x="16" y="12" width="1" height="1" fill={ink} />
        <rect x="20" y="8" width="1" height="1" fill={ink} />
        <rect x="19" y="9" width="1" height="1" fill={ink} />
        <rect x="18" y="10" width="1" height="1" fill={ink} />
        <rect x="17" y="11" width="1" height="1" fill={ink} />
        <rect x="22" y="8" width="1" height="1" fill={ink} />
        <rect x="23" y="9" width="1" height="1" fill={ink} />
        <rect x="24" y="10" width="1" height="1" fill={ink} />
        <rect x="23" y="11" width="1" height="1" fill={ink} />
        <rect x="22" y="12" width="1" height="1" fill={ink} />

        {/* 받침 */}
        <rect x="10" y="18" width="18" height="1" fill={ink} />
        <rect x="9" y="19" width="19" height="1" fill={ink} />
        <rect x="12" y="20" width="14" height="1" fill={ink} />
      </g>
    </svg>
  );
}

/**
 * 글자 로고. 가운뎃점은 원이 아니라 사각형입니다 — 격자 위에 놓인 한 칸으로
 * 읽히도록 모서리를 깎지 않습니다.
 */
export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={className}>
      Refactor
      <span
        aria-hidden="true"
        className="mx-[0.22em] inline-block size-[0.18em] bg-current align-[0.26em]"
      />
      me
    </span>
  );
}
