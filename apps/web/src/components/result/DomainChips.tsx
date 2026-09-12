import type { Analysis } from "@/types/data";
import { Chip, EvidenceCount } from "@/components/ui/Chip";

/**
 * 이 조직이 반복해서 다루는 영역. 건수는 파이프라인이 센 값을 그대로 씁니다 —
 * 화면에서 다시 계산하지 않습니다.
 */
export function DomainChips({ domains }: { domains: Analysis["domains"] }) {
  return (
    <div className="flex flex-wrap gap-2.5">
      {domains.map((domain) => (
        <Chip key={domain.id}>
          {domain.label}
          <span className="h-3.5 w-px bg-line" aria-hidden="true" />
          <EvidenceCount source="blog" count={domain.counts.blog} />
          {domain.counts.job != null && domain.counts.job > 0 && (
            <EvidenceCount source="job" count={domain.counts.job} />
          )}
        </Chip>
      ))}
    </div>
  );
}
