/**
 * 개인화 대기 화면.
 *
 * 진행률 막대를 쓰지 않습니다. 몇 퍼센트 왔는지 우리는 모르고,
 * 모르는 숫자를 화면에 적지 않기로 했습니다. 대신 걸리는 시간을 말합니다.
 */
export function Loading({
  title = "경험을 맞춰보는 중입니다",
  note = "보통 10초 안에 끝납니다.",
}: {
  title?: string;
  note?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col gap-3.5 rounded-card border border-line bg-surface p-6"
    >
      <p className="text-[0.9375rem] leading-[1.6] font-semibold">{title}</p>
      <div className="flex flex-col gap-2.5" aria-hidden="true">
        <div className="skeleton h-[11px] w-full rounded-[3px] bg-line" />
        <div className="skeleton h-[11px] w-[82%] rounded-[3px] bg-line [animation-delay:0.2s]" />
        <div className="skeleton h-[11px] w-[64%] rounded-[3px] bg-line [animation-delay:0.4s]" />
      </div>
      <p className="text-[0.8125rem] leading-[1.7] text-ink-soft">{note}</p>
    </div>
  );
}
