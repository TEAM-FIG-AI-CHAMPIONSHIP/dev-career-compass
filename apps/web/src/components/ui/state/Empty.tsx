import { EmptyIcon } from "../icons";
import { cardStyle } from "../Card";

/**
 * 근거 검증을 통과한 제안이 없는 조합은 노출하지 않습니다.
 * 그래서 이 화면은 "아직 없다"고 말하지, 빈 제안을 지어내지 않습니다.
 */
export function Empty({
  title = "아직 보여드릴 게 없습니다",
  description = "근거가 충분히 모인 조합만 공개합니다. 근거 없이 지어낸 제안을 보여드리지 않으려는 것입니다.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div
      className={cardStyle("empty", { className: "flex flex-col gap-3 p-6" })}
    >
      <EmptyIcon size={22} strokeWidth={1.4} className="text-ink-muted" />
      <p className="text-[0.9375rem] leading-[1.6] font-semibold">{title}</p>
      <p className="text-body-sm text-ink-soft">{description}</p>
    </div>
  );
}
