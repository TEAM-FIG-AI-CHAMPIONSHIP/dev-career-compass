import { AlertIcon } from "../icons";
import { Button } from "../Button";

/**
 * 개인화 호출이 실패해도 개인화 이전 결과와 입력값은 그대로 둡니다.
 * 사용자가 고른 것을 우리 쪽 실패로 날리지 않습니다.
 */
export function ErrorState({
  title = "개인화를 끝내지 못했습니다",
  description = "아래 결과는 개인화 전 그대로 남아 있습니다. 입력한 내용도 그대로입니다.",
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col gap-3 rounded-card border border-warn bg-surface p-6"
    >
      <AlertIcon size={22} strokeWidth={1.4} className="text-warn" />
      <p className="text-[0.9375rem] leading-[1.6] font-semibold">{title}</p>
      <p className="text-body-sm text-ink-soft">{description}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry} className="self-start">
          다시 시도
        </Button>
      )}
    </div>
  );
}
