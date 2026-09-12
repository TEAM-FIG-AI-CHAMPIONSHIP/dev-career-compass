type ClassValue = string | false | null | undefined;

/** 조건부 클래스 이름을 합칩니다. 의존성을 늘리지 않으려고 직접 둡니다. */
export function cn(...values: ClassValue[]): string {
  return values.filter(Boolean).join(" ");
}
