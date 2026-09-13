import type { Analysis } from "@/types/data";

/**
 * 이 조직이 반복해서 다루는 영역. 건수는 파이프라인이 센 값을 그대로 씁니다 —
 * 화면에서 다시 계산하지 않습니다.
 *
 * 색만으로 출처를 구분하지 않습니다. "블로그 5" 처럼 늘 글자를 함께 씁니다.
 */
export function DomainChips({ domains }: { domains: Analysis["domains"] }) {
  return (
    <ul className="flex flex-wrap gap-2.5">
      {domains.map((domain) => (
        <li
          key={domain.id}
          className="inline-flex items-center gap-2.5 rounded-pill border border-line-strong bg-surface px-4 py-2"
        >
          <span className="text-body-sm font-medium text-ink">
            {domain.label}
          </span>
          <span aria-hidden="true" className="text-line-strong">
            —
          </span>
          <span className="text-caption text-ink-soft">
            블로그 {domain.counts.blog}
            {domain.counts.job != null && domain.counts.job > 0 && (
              <> · 공고 {domain.counts.job}</>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}
