import { cn } from "@/lib/cn";

/**
 * 회사 표식. 아이콘이 있으면 아이콘, 없으면 이름 첫 글자입니다.
 *
 * 목록 카드와 오른쪽 패널이 같은 것을 씁니다. 전에는 같은 마크업이 두 곳에
 * 복사돼 있어서, 한쪽만 고치면 두 자리가 달라졌습니다.
 *
 * `next/image` 가 아니라 `img` 입니다. Next 의 이미지 최적화는 SVG 를 기본으로
 * 막아 두는데(원격 SVG 의 스크립트 때문입니다), 회사 아이콘은 우리가 저장소에
 * 직접 넣는 작은 파일이라 최적화가 필요 없습니다. 설정을 전역으로 여는 것보다
 * 이 자리에서 `img` 를 쓰는 편이 좁습니다.
 *
 * 아이콘이 없는 회사는 계속 생깁니다. 첫 글자 대체를 지우지 않습니다.
 */
export function CompanyMark({
  name,
  logoSrc,
  mark,
  size = "sm",
  className,
}: {
  name: string;
  /** `data/**\/index.json` 의 `logoSrc`. 없으면 첫 글자로 갑니다. */
  logoSrc?: string;
  /** 첫 글자 대신 쓸 한 글자. 없으면 이름에서 잘라 씁니다. */
  mark?: string;
  /** sm 은 목록 카드, md 는 선택된 회사 패널 */
  size?: "sm" | "md";
  className?: string;
}) {
  const box = size === "md" ? "size-12" : "size-11";
  const image = size === "md" ? "size-9" : "size-8";

  return (
    <span
      aria-hidden="true"
      className={cn(
        "flex shrink-0 items-center justify-center overflow-hidden rounded-card border border-line bg-surface text-h3 font-semibold text-ink-soft",
        box,
        className,
      )}
    >
      {logoSrc ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={logoSrc} alt="" className={cn(image, "object-contain")} />
      ) : (
        (mark ?? name.slice(0, 1))
      )}
    </span>
  );
}
