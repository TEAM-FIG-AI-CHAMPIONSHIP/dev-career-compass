import type { Analysis } from "@/types/data";
import { Chip, ChipCount } from "@/components/ui/Chip";

/**
 * 이 조직이 반복해서 다루는 영역. 건수는 파이프라인이 센 값을 그대로 씁니다 —
 * 화면에서 다시 계산하지 않습니다.
 *
 * 영역마다 다른 색을 주지 않습니다. 어느 영역인지는 적힌 이름이 이미 말하고
 * 있고, 목록은 근거가 많은 순서라 순서가 무게를 대신합니다. 색을 얹으면 같은
 * 정보를 한 번 더 칠하면서 상태색(3단계 배지)과 체계가 갈립니다.
 *
 * 색만으로 출처를 구분하지 않습니다. "블로그 5" 처럼 늘 글자를 함께 씁니다.
 */
export function DomainChips({ domains }: { domains: Analysis["domains"] }) {
  return (
    <ul className="flex flex-wrap gap-2">
      {domains.map((domain) => (
        <li key={domain.id}>
          <Chip>
            {domain.label}
            <ChipCount>
              블로그 {domain.counts.blog}
              {domain.counts.job != null && domain.counts.job > 0 && (
                <> · 공고 {domain.counts.job}</>
              )}
            </ChipCount>
          </Chip>
        </li>
      ))}
    </ul>
  );
}
